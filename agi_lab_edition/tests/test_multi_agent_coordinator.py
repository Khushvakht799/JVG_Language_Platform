import pytest
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.multi_agent_coordinator import MultiAgentCoordinator, generate_multi_agent_config

def test_register_agent():
    coordinator = MultiAgentCoordinator()
    coordinator.register_agent("agent1", ["planning", "analysis"])
    assert "agent1" in coordinator.agents
    assert coordinator.agents["agent1"]["status"] == "idle"

def test_assign_task():
    coordinator = MultiAgentCoordinator()
    coordinator.register_agent("agent1", ["planning", "analysis"])
    coordinator.register_agent("agent2", ["execution"])
    
    task_id = "task1"
    assigned = coordinator.assign_task(task_id, ["analysis"])
    assert assigned == "agent1"
    assert coordinator.agents["agent1"]["status"] == "busy"
    
    assigned = coordinator.assign_task("task2", ["execution"])
    assert assigned == "agent2"

def test_complete_task():
    coordinator = MultiAgentCoordinator()
    coordinator.register_agent("agent1", ["planning"])
    task_id = "task1"
    coordinator.assign_task(task_id, ["planning"])
    coordinator.complete_task(task_id)
    assert coordinator.agents["agent1"]["status"] == "idle"
    assert coordinator.tasks[task_id]["status"] == "completed"

def test_get_status():
    coordinator = MultiAgentCoordinator()
    coordinator.register_agent("agent1", ["planning"])
    status = coordinator.get_status()
    assert "agents" in status
    assert "tasks" in status
    assert "resources" in status

def test_generate_config():
    config = generate_multi_agent_config("test_multi_agent.json")
    assert os.path.exists("test_multi_agent.json")
    with open("test_multi_agent.json", "r") as f:
        data = json.load(f)
    assert data["name"] == "MultiAgentCoordinator"
    assert len(data["agents"]) == 3
    os.remove("test_multi_agent.json")
