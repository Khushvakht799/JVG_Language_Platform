import pytest
import json
from pathlib import Path

def test_handover_jvg_exists():
    jvg_path = Path("demos/handover.jvg")
    assert jvg_path.exists(), "handover.jvg не найден"

def test_handover_jvg_is_valid_json():
    jvg_path = Path("demos/handover.jvg")
    with open(jvg_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert "scenario" in data
    assert "steps" in data
    assert len(data["steps"]) == 5

def test_handover_demo_imports():
    import sys
    sys.path.insert(0, str(Path("demos").resolve()))
    import handover_demo
    assert hasattr(handover_demo, "execute_handover")
