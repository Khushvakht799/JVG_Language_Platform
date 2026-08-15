"""
Главный пайплайн для AGI Lab
Объединяет все 4 модуля в единый процесс.
"""

import json
from modules.self_correction import SelfCorrectionAgent, generate_self_correcting_agent_config
from modules.tool_composer import ToolComposer, generate_tool_composer_config
from modules.multi_agent_coordinator import MultiAgentCoordinator, generate_multi_agent_config
from modules.verifier import AgentVerifier, generate_verifier_config

def run_agi_pipeline(topic: str):
    """Запускает пайплайн для указанной темы AGI Lab."""
    print(f"Запуск пайплайна для темы: {topic}")
    
    if topic == "self_correction":
        config = generate_self_correcting_agent_config()
        print("Сгенерирована конфигурация для Self-Correction Agent")
        
    elif topic == "tool_composer":
        config = generate_tool_composer_config()
        print("Сгенерирована конфигурация для Tool Composer")
        
    elif topic == "multi_agent":
        config = generate_multi_agent_config()
        print("Сгенерирована конфигурация для Multi-Agent Coordination")
        
    elif topic == "verifier":
        config = generate_verifier_config()
        print("Сгенерирована конфигурация для Verifier")
        
    else:
        print(f"Неизвестная тема: {topic}")
        return None
    
    return config

if __name__ == "__main__":
    topics = ["self_correction", "tool_composer", "multi_agent", "verifier"]
    for topic in topics:
        run_agi_pipeline(topic)
