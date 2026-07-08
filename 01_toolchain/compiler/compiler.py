"""
compiler.py — Компилятор JVG (v5)
Работает с семантическим AST, построенным ASTBuilder.
"""

import json
from typing import Dict, Any
from lexer import EBNFLexer
from parser import EBNFParser
from ast_builder import ASTBuilder

class JVGCompiler:
    def __init__(self):
        self.lexer = EBNFLexer()
        self.ast_builder = ASTBuilder()

    def compile(self, text: str) -> Dict[str, Any]:
        # 1. Токенизация
        tokens, errors = self.lexer.tokenize_with_errors(text)
        if errors:
            return {"status": "error", "errors": errors}

        # 2. Парсинг (CST)
        parser = EBNFParser(tokens)
        try:
            cst = parser.parse()
        except SyntaxError as e:
            return {"status": "error", "errors": [str(e)]}

        # 3. Построение семантического AST
        try:
            sem_ast = self.ast_builder.build(cst)
        except Exception as e:
            return {"status": "error", "errors": [f"Ошибка построения AST: {str(e)}"]}

        # 4. Преобразование AST в JVG
        try:
            jvg = self._sem_ast_to_jvg(sem_ast)
            return {"status": "success", "jvg": jvg}
        except Exception as e:
            return {"status": "error", "errors": [f"Ошибка преобразования: {str(e)}"]}

    def _sem_ast_to_jvg(self, sem_ast: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "vectorograph": {
                "meta": {"version": "1.0", "title": "", "date": "", "author": "", "status": ""},
                "entity": {"name": "", "type": "", "purpose": ""},
                "context": {"origin": "", "environment": "", "dependencies": []},
                "structure": {"components": [], "layers": []},
                "relations": {"inputs": [], "outputs": [], "connected_to": []},
                "logic": {"rules": [], "algorithms": [], "decision_model": []},
                "state": {"current": "", "problems": [], "risks": []},
                "actions": {"next_steps": [], "required_resources": []},
                "evolution": {"history": "", "future_versions": []}
            }
        }

        # Проходим по семантическим узлам
        for rule_name, sem_node in sem_ast.items():
            if rule_name == "meta":
                result["vectorograph"]["meta"] = sem_node.to_dict()
            elif rule_name == "entity":
                result["vectorograph"]["entity"] = sem_node.to_dict()
            elif rule_name == "context":
                result["vectorograph"]["context"] = sem_node.to_dict()
            elif rule_name == "structure":
                result["vectorograph"]["structure"] = sem_node.to_dict()
            elif rule_name == "relations":
                result["vectorograph"]["relations"] = sem_node.to_dict()
            elif rule_name == "logic":
                result["vectorograph"]["logic"] = sem_node.to_dict()
            elif rule_name == "state":
                result["vectorograph"]["state"] = sem_node.to_dict()
            elif rule_name == "actions":
                result["vectorograph"]["actions"] = sem_node.to_dict()
            elif rule_name == "evolution":
                result["vectorograph"]["evolution"] = sem_node.to_dict()

        return result


# ============================================================
# Тест
# ============================================================

def test_compiler():
    sample = '''
        meta ::= "version" "1.0" "title" "Тестовый JVG" "date" "2026-07-07" "author" "Архитектор" "status" "черновик";
        entity ::= "name" "Сервер" "type" "система" "purpose" "обработка данных";
        context ::= "origin" "тестовый проект" "environment" "локальная сеть" "dependencies" "БД, API";
        structure ::= "components" "ядро, модули, интерфейс" "layers" "приложение, сервис, хранилище";
        relations ::= "inputs" "запросы REST" "outputs" "ответы JSON" "connected_to" "база данных, кэш";
        logic ::= "rules" "обработка ошибок; валидация" "algorithms" "поиск; сортировка" "decision_model" "приоритет по времени";
        state ::= "current" "ВЫПОЛНЕНИЕ" "problems" "нет" "risks" "низкий";
        actions ::= "next_steps" "протестировать; развернуть" "required_resources" "сервер, доступы";
        evolution ::= "history" "начало проекта" "future_versions" "v2.0, v3.0";
    '''

    compiler = JVGCompiler()
    result = compiler.compile(sample)

    if result["status"] == "error":
        print("❌ Ошибки компиляции:")
        for err in result["errors"]:
            print(f"  {err}")
    else:
        print("✅ Компиляция успешна!")
        print("\n=== JVG ===")
        print(json.dumps(result["jvg"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_compiler()
