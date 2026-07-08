import re
from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field
from lexer import Token, EBNFLexer

# ============================================================
# Узлы AST (абстрактное синтаксическое дерево)
# ============================================================

@dataclass
class ASTNode:
    type: str
    value: Any = None
    children: List['ASTNode'] = field(default_factory=list)

@dataclass
class RuleNode(ASTNode):
    def __init__(self, name: str, expression: ASTNode):
        super().__init__(type='Rule', value=name)
        self.children.append(expression)

@dataclass
class SequenceNode(ASTNode):
    def __init__(self, elements: List[ASTNode]):
        super().__init__(type='Sequence')
        self.children = elements

@dataclass
class ChoiceNode(ASTNode):
    def __init__(self, alternatives: List[ASTNode]):
        super().__init__(type='Choice')
        self.children = alternatives

@dataclass
class TerminalNode(ASTNode):
    def __init__(self, value: str):
        super().__init__(type='Terminal', value=value)

@dataclass
class NonTerminalNode(ASTNode):
    def __init__(self, name: str):
        super().__init__(type='NonTerminal', value=name)

@dataclass
class RepetitionNode(ASTNode):
    def __init__(self, inner: ASTNode):
        super().__init__(type='Repetition')
        self.children.append(inner)

@dataclass
class OptionalNode(ASTNode):
    def __init__(self, inner: ASTNode):
        super().__init__(type='Optional')
        self.children.append(inner)

@dataclass
class GroupNode(ASTNode):
    def __init__(self, inner: ASTNode):
        super().__init__(type='Group')
        self.children.append(inner)

# ============================================================
# Парсер
# ============================================================

class EBNFParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def next_token(self) -> Optional[Token]:
        t = self.peek()
        if t:
            self.pos += 1
        return t

    def expect(self, token_type: str, value: Optional[str] = None) -> Token:
        t = self.peek()
        if not t:
            raise SyntaxError(f"Ожидался {token_type}, но достигнут конец ввода")
        if t.type != token_type:
            raise SyntaxError(f"Ожидался {token_type}, получен {t.type} (строка {t.line}, колонка {t.column})")
        if value is not None and t.value != value:
            raise SyntaxError(f"Ожидалось значение '{value}', получено '{t.value}'")
        return self.next_token()

    def parse(self) -> Dict[str, ASTNode]:
        rules = {}
        while self.peek():
            rule = self.parse_rule()
            if rule:
                rules[rule.value] = rule
        return rules

    def parse_rule(self) -> Optional[RuleNode]:
        if self.peek() and self.peek().type == 'IDENTIFIER':
            name = self.next_token().value
            self.expect('ASSIGN')
            expr = self.parse_expression()
            self.expect('SEMICOLON')
            return RuleNode(name, expr)
        return None

    def parse_expression(self) -> ASTNode:
        return self.parse_sequence()

    def parse_sequence(self) -> ASTNode:
        elements = []
        while True:
            t = self.peek()
            if not t or t.type in ('SEMICOLON', 'OR', 'RPAREN', 'RBRACE', 'RBRACKET'):
                break
            elements.append(self.parse_term())
        if len(elements) == 1:
            return elements[0]
        return SequenceNode(elements)

    def parse_term(self) -> ASTNode:
        t = self.peek()
        if not t:
            raise SyntaxError("Неожиданный конец ввода")

        # Терминал (строка в кавычках)
        if t.type == 'STRING_LITERAL':
            self.next_token()
            return TerminalNode(t.value)

        # Нетерминал (идентификатор)
        if t.type == 'IDENTIFIER':
            self.next_token()
            return NonTerminalNode(t.value)

        # Повторение: { ... }
        if t.type == 'LBRACE':
            self.next_token()
            inner = self.parse_expression()
            self.expect('RBRACE')
            return RepetitionNode(inner)

        # Опционально: [ ... ]
        if t.type == 'LBRACKET':
            self.next_token()
            inner = self.parse_expression()
            self.expect('RBRACKET')
            return OptionalNode(inner)

        # Группа: ( ... )
        if t.type == 'LPAREN':
            self.next_token()
            inner = self.parse_expression()
            self.expect('RPAREN')
            return GroupNode(inner)

        # Если ни одно правило не подошло
        raise SyntaxError(f"Неизвестный токен: {t.type} '{t.value}' (строка {t.line}, колонка {t.column})")

# ============================================================
# Тест
# ============================================================

def test_parser():
    sample = '''
        entity ::= "entity" "{" name ":" string "," type ":" string "}";
        action ::= "action" "{" verb ":" string "," target ":" reference "}";
        rule ::= "rule" "{" condition ":" string "," consequence ":" action "}";
    '''
    lexer = EBNFLexer()
    tokens, errors = lexer.tokenize_with_errors(sample)
    if errors:
        print("Ошибки лексера:", errors)
        return

    parser = EBNFParser(tokens)
    try:
        ast = parser.parse()
        print("=== AST ===")
        for name, node in ast.items():
            print(f"Rule: {name}")
            print(f"  {node}")
    except SyntaxError as e:
        print(f"Ошибка синтаксиса: {e}")

if __name__ == "__main__":
    test_parser()
