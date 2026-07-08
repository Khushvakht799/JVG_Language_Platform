"""
compiler.py — Отладочная версия с выводом AST
"""

import json
from lexer import EBNFLexer
from parser import EBNFParser

def debug_ast():
    sample = '''
        meta ::= "version" "1.0" "title" "Тестовый JVG" "date" "2026-07-07" "author" "Архитектор" "status" "черновик";
        entity ::= "name" "Сервер" "type" "система" "purpose" "обработка данных";
    '''

    lexer = EBNFLexer()
    tokens, errors = lexer.tokenize_with_errors(sample)
    if errors:
        print("Ошибки лексера:", errors)
        return

    parser = EBNFParser(tokens)
    try:
        ast = parser.parse()
    except SyntaxError as e:
        print("Ошибка синтаксиса:", e)
        return

    print("=== AST (сырой) ===")
    for rule_name, rule_node in ast.items():
        print(f"\nПравило: {rule_name}")
        print(f"  Тип узла: {rule_node.type}")
        print(f"  Значение: {rule_node.value}")
        print(f"  Дети ({len(rule_node.children)}):")
        for i, child in enumerate(rule_node.children):
            print(f"    [{i}] {child.type}: {child.value} (дети: {len(child.children)})")
            if child.children:
                for j, sub in enumerate(child.children):
                    print(f"        [{j}] {sub.type}: {sub.value}")

if __name__ == "__main__":
    debug_ast()
