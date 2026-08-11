"""
tests/test_planner_v12.py — Тесты с FakeWorldModel
"""

import pytest
from jvg.planner_v12 import PlannerV12
from jvg.models.fake_world_model import FakeWorldModel
from jvg.store import JVGStore

@pytest.fixture
def mock_store():
    return JVGStore()

def test_clean_repo(mock_store):
    """Чистый репозиторий → сразу успех"""
    model = FakeWorldModel({
        'has_modifications': False,
        'has_untracked': False,
        'has_staged': False,
        'is_ahead': False,
        'is_behind': False,
        'is_clean': True
    })
    
    planner = PlannerV12(mock_store, model)
    planner.set_goal({
        'is_clean': True,
        'is_ahead': False,
        'is_behind': False
    })
    
    result = planner.run("test_doc")
    assert result['status'] == 'success'
    assert result['iterations'] == 0

def test_untracked_files(mock_store):
    """Неотслеживаемые файлы → add → commit → push"""
    model = FakeWorldModel({
        'has_modifications': False,
        'has_untracked': True,
        'has_staged': False,
        'is_ahead': False,
        'is_behind': False,
        'is_clean': False
    })
    
    planner = PlannerV12(mock_store, model)
    planner.set_goal({
        'is_clean': True,
        'is_ahead': False,
        'is_behind': False
    })
    planner.max_iterations = 5
    
    result = planner.run("test_doc")
    
    assert result['status'] == 'success'
    assert len(planner.experience) >= 3
    assert planner.experience[0]['action']['name'] == 'add_changes'
    assert planner.experience[1]['action']['name'] == 'commit_changes'
    assert planner.experience[2]['action']['name'] == 'push_changes'

def test_staged_files(mock_store):
    """Подготовленные файлы → commit → push"""
    model = FakeWorldModel({
        'has_modifications': False,
        'has_untracked': False,
        'has_staged': True,
        'is_ahead': False,
        'is_behind': False,
        'is_clean': False
    })
    
    planner = PlannerV12(mock_store, model)
    planner.set_goal({
        'is_clean': True,
        'is_ahead': False,
        'is_behind': False
    })
    planner.max_iterations = 5
    
    result = planner.run("test_doc")
    
    assert result['status'] == 'success'
    assert planner.experience[0]['action']['name'] == 'commit_changes'
    assert planner.experience[1]['action']['name'] == 'push_changes'

def test_ahead(mock_store):
    """Локальный коммит → push"""
    model = FakeWorldModel({
        'has_modifications': False,
        'has_untracked': False,
        'has_staged': False,
        'is_ahead': True,
        'is_behind': False,
        'is_clean': False
    })
    
    planner = PlannerV12(mock_store, model)
    planner.set_goal({
        'is_clean': True,
        'is_ahead': False,
        'is_behind': False
    })
    planner.max_iterations = 5
    
    result = planner.run("test_doc")
    
    assert result['status'] == 'success'
    assert planner.experience[0]['action']['name'] == 'push_changes'

def test_modified_files(mock_store):
    """Изменённые файлы → add → commit → push"""
    model = FakeWorldModel({
        'has_modifications': True,
        'has_untracked': False,
        'has_staged': False,
        'is_ahead': False,
        'is_behind': False,
        'is_clean': False
    })
    
    planner = PlannerV12(mock_store, model)
    planner.set_goal({
        'is_clean': True,
        'is_ahead': False,
        'is_behind': False
    })
    planner.max_iterations = 5
    
    result = planner.run("test_doc")
    
    assert result['status'] == 'success'
    assert planner.experience[0]['action']['name'] == 'add_changes'
    assert planner.experience[1]['action']['name'] == 'commit_changes'
    assert planner.experience[2]['action']['name'] == 'push_changes'

def test_experience_collection(mock_store):
    """Проверка накопления опыта"""
    model = FakeWorldModel({
        'has_modifications': True,
        'has_untracked': False,
        'has_staged': False,
        'is_ahead': False,
        'is_behind': False,
        'is_clean': False
    })
    
    planner = PlannerV12(mock_store, model)
    planner.set_goal({
        'is_clean': True,
        'is_ahead': False,
        'is_behind': False
    })
    
    result = planner.run("test_doc")
    
    assert len(planner.experience) > 0
    assert 'state' in planner.experience[0]
    assert 'action' in planner.experience[0]
    assert 'new_state' in planner.experience[0]
