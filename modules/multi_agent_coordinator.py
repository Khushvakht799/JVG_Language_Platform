"""
Модуль координации многоагентных систем (Multi-Agent Coordinator)
Для Amazon AGI Lab — тема: Multi-Agent Coordination
"""

from typing import Dict, List, Any, Optional
import json
import uuid

class MultiAgentCoordinator:
    """Координатор для систем из нескольких агентов."""
    
    def __init__(self):
        self.agents = {}
        self.tasks = {}
        self.resources = {}
        
    def register_agent(self, agent_id: str, capabilities: List[str]) -> None:
        """Регистрирует агента в системе."""
        self.agents[agent_id] = {
            "id": agent_id,
            "capabilities": capabilities,
            "status": "idle",
            "assigned_task": None
        }
    
    def assign_task(self, task_id: str, requirements: List[str]) -> Optional[str]:
        """Назначает задачу агенту с подходящими возможностями."""
        for agent_id, agent_info in self.agents.items():
            if agent_info["status"] == "idle" and all(req in agent_info["capabilities"] for req in requirements):
                agent_info["status"] = "busy"
                agent_info["assigned_task"] = task_id
                self.tasks[task_id] = {"agent": agent_id, "status": "assigned"}
                return agent_id
        return None
    
    def complete_task(self, task_id: str) -> None:
        """Завершает выполнение задачи."""
        if task_id in self.tasks:
            agent_id = self.tasks[task_id]["agent"]
            self.agents[agent_id]["status"] = "idle"
            self.agents[agent_id]["assigned_task"] = None
            self.tasks[task_id]["status"] = "completed"
    
    def get_status(self) -> Dict[str, Any]:
        """Возвращает статус системы."""
        return {
            "agents": self.agents,
            "tasks": self.tasks,
            "resources": self.resources
        }


def generate_multi_agent_config(output_path: str = "configs/multi_agent_config.json"):
    config = {
        "name": "MultiAgentCoordinator",
        "version": "1.0",
        "description": "Модуль координации многоагентных систем для AGI Lab",
        "agents": [
            {
                "id": "agent-1",
                "capabilities": ["planning", "analysis", "data_processing"],
                "role": "planner"
            },
            {
                "id": "agent-2",
                "capabilities": ["execution", "api_calls", "data_retrieval"],
                "role": "executor"
            },
            {
                "id": "agent-3",
                "capabilities": ["verification", "quality_control", "reporting"],
                "role": "verifier"
            }
        ],
        "coordination_protocols": [
            {
                "name": "TaskDistribution",
                "description": "Агенты распределяют задачи по возможностям"
            },
            {
                "name": "ResourceSharing",
                "description": "Агенты делят общие ресурсы (данные, инструменты)"
            }
        ]
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return config


if __name__ == "__main__":
    coordinator = MultiAgentCoordinator()
    coordinator.register_agent("agent-1", ["planning", "analysis"])
    coordinator.register_agent("agent-2", ["execution", "api_calls"])
    
    task_id = str(uuid.uuid4())
    assigned = coordinator.assign_task(task_id, ["analysis", "execution"])
    if assigned:
        print(f"Задача {task_id} назначена агенту {assigned}")
    
    print("Статус системы:", json.dumps(coordinator.get_status(), indent=2, ensure_ascii=False))
    generate_multi_agent_config()
