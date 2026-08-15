import pytest
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.verifier import AgentVerifier, generate_verifier_config

def test_verifier_init():
    rules = {"required_fields": ["name"]}
    verifier = AgentVerifier(rules)
    assert verifier.rules["required_fields"] == ["name"]

def test_verify_configuration_valid():
    rules = {"required_fields": ["name", "version", "model"]}
    verifier = AgentVerifier(rules)
    config = {
        "name": "TestAgent",
        "version": "1.0",
        "model": {"type": "llm"},
        "verification": {"rules": ["no_unsafe_actions"]}
    }
    result = verifier.verify_configuration(config)
    assert result["is_valid"] == True
    assert len(result["violations"]) == 0

def test_verify_configuration_missing_field():
    rules = {"required_fields": ["name", "version", "model"]}
    verifier = AgentVerifier(rules)
    config = {
        "name": "TestAgent",
        "version": "1.0"
    }
    result = verifier.verify_configuration(config)
    assert result["is_valid"] == False
    assert "Отсутствует обязательное поле: model" in result["violations"]

def test_verify_configuration_missing_rule():
    rules = {"required_fields": ["name", "version", "model"]}
    verifier = AgentVerifier(rules)
    config = {
        "name": "TestAgent",
        "version": "1.0",
        "model": {"type": "llm"},
        "verification": {"rules": []}
    }
    result = verifier.verify_configuration(config)
    assert result["is_valid"] == True
    assert "Отсутствует правило безопасности 'no_unsafe_actions'" in result["warnings"]

def test_generate_config():
    config = generate_verifier_config("test_verifier.json")
    assert os.path.exists("test_verifier.json")
    with open("test_verifier.json", "r") as f:
        data = json.load(f)
    assert data["name"] == "AgentVerifier"
    assert "required_fields" in data["rules"]
    os.remove("test_verifier.json")
