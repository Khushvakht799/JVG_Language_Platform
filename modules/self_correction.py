"""
Модуль самоисправления агентов (Self-Correction Module)
Для Amazon AGI Lab — тема: Self-Correcting Agents
"""

from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class SelfCorrectionAgent:
    """Базовый класс для агента с самоисправлением."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.history = []
        self.reflection_log = []
        
    def reflect(self, action: Dict[str, Any]) -> Dict[str, Any]:
        reflection = {
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": self._analyze_action(action),
            "suggestions": self._suggest_corrections(action)
        }
        self.reflection_log.append(reflection)
        return reflection
    
    def self_evaluate(self, planned_action: Dict[str, Any]) -> float:
        complexity = len(planned_action.get("steps", []))
        history_success_rate = self._calculate_success_rate()
        score = 0.8 - (complexity * 0.1) + (history_success_rate * 0.2)
        return max(0.0, min(1.0, score))
    
    def verify_cot(self, reasoning_chain: List[str]) -> bool:
        if not reasoning_chain:
            return False
        for i in range(1, len(reasoning_chain)):
            if not self._is_logical_follow(reasoning_chain[i-1], reasoning_chain[i]):
                return False
        return True
    
    def _analyze_action(self, action: Dict[str, Any]) -> str:
        if action.get("status") == "success":
            return "Действие выполнено успешно."
        elif action.get("status") == "failure":
            return f"Ошибка: {action.get('error', 'неизвестная причина')}"
        else:
            return "Действие требует проверки."
    
    def _suggest_corrections(self, action: Dict[str, Any]) -> List[str]:
        suggestions = []
        if action.get("status") == "failure":
            suggestions.append("Повторить действие с другими параметрами.")
            suggestions.append("Изменить порядок шагов.")
        return suggestions
    
    def _calculate_success_rate(self) -> float:
        if not self.history:
            return 0.5
        successes = sum(1 for h in self.history if h.get("status") == "success")
        return successes / len(self.history)
    
    def _is_logical_follow(self, prev: str, current: str) -> bool:
        return True


def generate_self_correcting_agent_config(output_path: str = "configs/self_correcting_agent.json"):
    config = {
        "name": "SelfCorrectingAgent",
        "version": "1.0",
        "description": "Агент с механизмами самоисправления для AGI Lab",
        "modules": [
            {"name": "Reflection", "enabled": True, "parameters": {"history_length": 10, "correction_threshold": 0.3}},
            {"name": "SelfEvaluation", "enabled": True, "parameters": {"success_threshold": 0.7}},
            {"name": "CoTVerification", "enabled": True, "parameters": {"max_chain_length": 5}}
        ],
        "model": {
            "type": "llm",
            "provider": "amazon-bedrock",
            "model_id": "anthropic.claude-3-sonnet",
            "parameters": {"temperature": 0.3, "max_tokens": 2048}
        },
        "tools": [],
        "memory": {"type": "vector", "provider": "amazon-opensearch", "config": {}},
        "verification": {"enabled": True, "rules": ["no_unsafe_actions", "no_cycles", "consistency_check"]}
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return config


if __name__ == "__main__":
    agent = SelfCorrectionAgent({"name": "TestAgent"})
    test_action = {"action": "fetch_data", "status": "failure", "error": "timeout"}
    reflection = agent.reflect(test_action)
    print("Рефлексия:", json.dumps(reflection, indent=2, ensure_ascii=False))
    generate_self_correcting_agent_config()
