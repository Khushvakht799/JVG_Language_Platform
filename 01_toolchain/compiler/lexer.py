"""
lexer.py — Лексер для EBNF-грамматики JVG
Превращает строку с правилами в список токенов.
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

class EBNFLexer:
    def __init__(self):
        # Определяем паттерны токенов в порядке убывания приоритета
        self.token_patterns = [
            # Специальные символы
            (r'::=', 'ASSIGN'),           # Присваивание
            (r'\|', 'OR'),                # Альтернатива
            (r'\(', 'LPAREN'),            # Левая скобка
            (r'\)', 'RPAREN'),            # Правая скобка
            (r'\{', 'LBRACE'),            # Левая фигурная скобка (повторение)
            (r'\}', 'RBRACE'),            # Правая фигурная скобка
            (r'\[', 'LBRACKET'),          # Левая квадратная скобка (опционально)
            (r'\]', 'RBRACKET'),          # Правая квадратная скобка
            (r',', 'COMMA'),              # Запятая
            (r'=', 'EQUALS'),             # Равно
            (r'!=', 'NEQUALS'),           # Не равно
            (r';', 'SEMICOLON'),          # Точка с запятой
            (r'\.\.\.', 'ELLIPSIS'),      # Многоточие
            
            # Строковые литералы (в двойных кавычках)
            (r'"[^"]*"', 'STRING_LITERAL'),
            
            # Идентификаторы (начинаются с буквы или подчёркивания)
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
            
            # Числа
            (r'\d+\.\d+', 'FLOAT'),
            (r'\d+', 'INTEGER'),
            
            # Комментарии (однострочные)
            (r'//[^\n]*', 'COMMENT'),
            
            # Пробелы и переносы строк (игнорируем, но считаем строки)
            (r'\n', 'NEWLINE'),
            (r'[ \t]+', 'WHITESPACE'),
        ]
        
        self.token_regex = self._compile_regex()
        
    def _compile_regex(self) -> re.Pattern:
        """Собирает все паттерны в один регулярный регекс."""
        patterns = [f'(?P<{name}>{pattern})' for pattern, name in self.token_patterns]
        return re.compile('|'.join(patterns), re.UNICODE)
    
    def tokenize(self, code: str) -> List[Token]:
        """Превращает строку кода в список токенов."""
        tokens = []
        line = 1
        column = 1
        
        for match in self.token_regex.finditer(code):
            token_type = match.lastgroup
            token_value = match.group(0)
            
            # Вычисляем позицию (строку и колонку) из позиции матча в строке
            # Для простоты используем line и column из предыдущих токенов
            # (в реальном лексере нужно отслеживать точные позиции)
            
            # Пропускаем пробелы и комментарии
            if token_type == 'WHITESPACE':
                column += len(token_value)
                continue
                
            if token_type == 'NEWLINE':
                line += 1
                column = 1
                continue
                
            if token_type == 'COMMENT':
                # Комментарии игнорируем, но счётчик строк обновляем
                line += 1
                column = 1
                continue
            
            # Для всех остальных токенов создаём объект
            tokens.append(Token(
                type=token_type,
                value=token_value,
                line=line,
                column=column
            ))
            column += len(token_value)
        
        return tokens
    
    def tokenize_with_errors(self, code: str) -> Tuple[List[Token], List[str]]:
        """Токенизирует код и возвращает список ошибок, если они есть."""
        tokens = []
        errors = []
        line = 1
        column = 1
        
        # Если строка заканчивается не на перенос, добавляем его для удобства
        if not code.endswith('\n'):
            code += '\n'
        
        for match in self.token_regex.finditer(code):
            token_type = match.lastgroup
            token_value = match.group(0)
            
            if token_type == 'WHITESPACE':
                column += len(token_value)
                continue
                
            if token_type == 'NEWLINE':
                line += 1
                column = 1
                continue
                
            if token_type == 'COMMENT':
                line += 1
                column = 1
                continue
            
            # Если токен не распознан — ошибка
            if token_type is None:
                errors.append(f"Неизвестный символ '{token_value}' на строке {line}, колонка {column}")
                column += len(token_value)
                continue
            
            tokens.append(Token(
                type=token_type,
                value=token_value,
                line=line,
                column=column
            ))
            column += len(token_value)
        
        return tokens, errors


def test_lexer():
    """Тестовая функция для проверки лексера."""
    sample_code = '''
    // Пример EBNF-правила для JVG
    
    entity ::= "entity" "{" name ":" string "," type ":" string "}";
    
    action ::= "action" "{" verb ":" string "," target ":" reference "}";
    
    rule ::= "rule" "{" condition ":" string "," consequence ":" action "}";
    '''
    
    lexer = EBNFLexer()
    tokens, errors = lexer.tokenize_with_errors(sample_code)
    
    print("=== ТОКЕНЫ ===")
    for t in tokens:
        print(f"{t.type:12} | '{t.value}' | line {t.line}, col {t.column}")
    
    if errors:
        print("\n=== ОШИБКИ ===")
        for e in errors:
            print(f"❌ {e}")
    else:
        print("\n✅ Ошибок нет.")


if __name__ == "__main__":
    test_lexer()