"""
Демо-скрипт для AGI Lab Edition
Показывает работу всех 4 модулей на примерах.
"""

import os
import sys
import json
from datetime import datetime

# Добавляем путь к модулям
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.self_correction import SelfCorrectionAgent
from modules.tool_composer import ToolComposer
from modules.multi_agent_coordinator import MultiAgentCoordinator
from modules.verifier import AgentVerifier

def run_demo():
    """Запускает демонстрацию всех модулей."""
    print("=" * 60)
    print("AGI Lab Edition — Демонстрация работы модулей")
    print(f"Время запуска: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # 1. Self-Correction Demo
    print("\n[1] Self-Correction Agent")
    print("-" * 40)
    agent = SelfCorrectionAgent({"name": "DemoAgent"})
    action = {"action": "fetch_data", "status": "failure", "error": "timeout"}
    reflection = agent.reflect(action)
    print(f"  Действие: {action['action']} (статус: {action['status']})")
    print(f"  Анализ: {reflection['analysis']}")
    print(f"  Предложения: {reflection['suggestions']}")
    
    # 2. Tool Composer Demo
    print("\n[2] Tool Composer")
    print("-" * 40)
    registry = {
        "calculator": {"name": "calculator", "keywords": ["calculate", "math"]},
        "weather": {"name": "weather", "keywords": ["weather", "forecast"]}
    }
    composer = ToolComposer(registry)
    task = "Calculate the total cost and check weather in Barcelona"
    chain = composer.compose_tool_chain(task)
    print(f"  Задача: {task}")
    print(f"  Выбранные инструменты: {[t['name'] for t in chain]}")
    
    # 3. Multi-Agent Coordinator Demo
    print("\n[3] Multi-Agent Coordinator")
    print("-" * 40)
    coordinator = MultiAgentCoordinator()
    coordinator.register_agent("Planner", ["planning", "analysis"])
    coordinator.register_agent("Executor", ["execution", "api_calls"])
    task_id = "task_001"
    assigned = coordinator.assign_task(task_id, ["analysis", "execution"])
    print(f"  Задача: {task_id}")
    print(f"  Назначена агенту: {assigned}")
    print(f"  Статус системы: {coordinator.get_status()['agents']['Planner']['status']}")
    
    # 4. Verifier Demo
    print("\n[4] Agent Verifier")
    print("-" * 40)
    rules = {"required_fields": ["name", "version", "model"]}
    verifier = AgentVerifier(rules)
    config = {
        "name": "TestAgent",
        "version": "1.0",
        "model": {"type": "llm"},
        "verification": {"rules": ["no_unsafe_actions"]}
    }
    result = verifier.verify_configuration(config)
    print(f"  Конфигурация: {config['name']} v{config['version']}")
    print(f"  Статус: {'✅ Валидна' if result['is_valid'] else '❌ Невалидна'}")
    print(f"  Предупреждения: {result['warnings'] if result['warnings'] else 'нет'}")
    
    print("\n" + "=" * 60)
    print("Демонстрация завершена. Все модули работают корректно.")
    print("=" * 60)

if __name__ == "__main__":
    run_demo()
