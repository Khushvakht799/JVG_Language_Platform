"""
validator_pipeline.py — Объединяет все уровни валидации JVG.
"""

from typing import Dict, Any, List, Tuple
from structural_validator import JVGValidator
from semantic_validator import SemanticValidator
from referential_validator import ReferentialValidator
from behavioral_validator import BehavioralValidator

class JVGValidatorPipeline:
    def __init__(self):
        self.structural = JVGValidator()
        self.semantic = SemanticValidator()
        self.referential = ReferentialValidator()
        self.behavioral = BehavioralValidator()

    def validate(self, jvg: Dict[str, Any]) -> Tuple[bool, List[str]]:
        all_errors = []

        # L1: Structural
        valid, errors = self.structural.validate(jvg)
        all_errors.extend(errors)

        # L2: Semantic
        valid, errors = self.semantic.validate(jvg)
        all_errors.extend(errors)

        # L3: Referential (без хранилища)
        valid, errors = self.referential.validate(jvg)
        all_errors.extend(errors)

        # L4: Behavioral
        valid, errors = self.behavioral.validate(jvg)
        all_errors.extend(errors)

        return len(all_errors) == 0, all_errors
