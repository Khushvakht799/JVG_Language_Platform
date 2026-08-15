import pytest
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.self_correction import SelfCorrectionAgent, generate_self_correcting_agent_config

def test_self_correction_init():
    config = {"name": "TestAgent"}
    agent = SelfCorrectionAgent(config)
    assert agent.config["name"] == "TestAgent"
    assert agent.history == []
    assert agent.reflection_log == []

def test_reflect_success():
    agent = SelfCorrectionAgent({"name": "TestAgent"})
    action = {"action": "test", "status": "success"}
    reflection = agent.reflect(action)
    assert reflection["action"]["status"] == "success"
    assert "Действие выполнено успешно" in reflection["analysis"]
    assert len(agent.reflection_log) == 1

def test_reflect_failure():
    agent = SelfCorrectionAgent({"name": "TestAgent"})
    action = {"action": "test", "status": "failure", "error": "timeout"}
    reflection = agent.reflect(action)
    assert reflection["action"]["status"] == "failure"
    assert "timeout" in reflection["analysis"]
    assert "Повторить действие" in reflection["suggestions"][0]

def test_self_evaluate():
    agent = SelfCorrectionAgent({"name": "TestAgent"})
    planned_action = {"steps": ["step1", "step2", "step3", "step4", "step5"]}
    score = agent.self_evaluate(planned_action)
    assert 0.0 <= score <= 1.0

def test_verify_cot():
    agent = SelfCorrectionAgent({"name": "TestAgent"})
    chain = ["step1", "step2", "step3"]
    assert agent.verify_cot(chain) == True
    assert agent.verify_cot([]) == False

def test_generate_config():
    config = generate_self_correcting_agent_config("test_config.json")
    assert os.path.exists("test_config.json")
    with open("test_config.json", "r") as f:
        data = json.load(f)
    assert data["name"] == "SelfCorrectingAgent"
    os.remove("test_config.json")
