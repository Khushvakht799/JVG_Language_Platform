import pytest
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules.tool_composer import ToolComposer, generate_tool_composer_config

def test_tool_composer_init():
    registry = {"tool1": {"name": "tool1", "keywords": ["test"]}}
    composer = ToolComposer(registry)
    assert composer.tool_registry["tool1"]["name"] == "tool1"

def test_compose_tool_chain():
    registry = {
        "calculator": {"name": "calculator", "keywords": ["calculate", "math"]},
        "weather": {"name": "weather", "keywords": ["weather", "forecast"]}
    }
    composer = ToolComposer(registry)
    task = "Calculate the total cost"
    chain = composer.compose_tool_chain(task)
    assert len(chain) == 1
    assert chain[0]["name"] == "calculator"

def test_generate_tool_config():
    tools = [{"name": "test_tool", "description": "Test tool", "input_schema": {}, "output_schema": {}}]
    composer = ToolComposer({})
    config = composer.generate_tool_config(tools)
    assert "api_schema" in config
    assert "/test_tool" in config["api_schema"]["paths"]

def test_generate_config_file():
    config = generate_tool_composer_config("test_tool_config.json")
    assert os.path.exists("test_tool_config.json")
    with open("test_tool_config.json", "r") as f:
        data = json.load(f)
    assert data["name"] == "ToolComposer"
    os.remove("test_tool_config.json")
