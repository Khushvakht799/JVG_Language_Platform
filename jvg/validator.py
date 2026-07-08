"""
validator.py — Валидатор JVG (объединяет все уровни)
"""

import sys
import os
from typing import Dict, Any, List, Tuple

# Добавляем путь к валидаторам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, '01_toolchain', 'validator'))

from structural_validator import JVGValidator as StructuralValidator
from semantic_validator import SemanticValidator
from referential_validator import ReferentialValidator
from behavioral_validator import BehavioralValidator

class JVGValidatorPipeline:
    def __init__(self):
        self.structural = StructuralValidator()
        self.semantic = SemanticValidator()
        self.referential = ReferentialValidator()
        self.behavioral = BehavioralValidator()

    def validate(self, jvg: Dict[str, Any]) -> Tuple[bool, List[str]]:
        all_errors = []

        valid, errors = self.structural.validate(jvg)
        all_errors.extend(errors)

        valid, errors = self.semantic.validate(jvg)
        all_errors.extend(errors)

        valid, errors = self.referential.validate(jvg)
        all_errors.extend(errors)

        valid, errors = self.behavioral.validate(jvg)
        all_errors.extend(errors)

        return len(all_errors) == 0, all_errors
