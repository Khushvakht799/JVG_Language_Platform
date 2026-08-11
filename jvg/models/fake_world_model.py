"""
jvg/models/fake_world_model.py — Фейковая модель мира для тестов
"""

from .world_model import WorldModel
from typing import Dict, Any

class FakeWorldModel(WorldModel):
    def __init__(self, initial_state: Dict[str, Any]):
        self.state = initial_state.copy()
    
    def get_state(self) -> Dict[str, Any]:
        return self.state.copy()
    
    def apply_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Применить действие и изменить состояние"""
        name = action.get('name', '')
        
        # Правила перехода состояний
        if name == 'add_changes':
            # untracked + modified → staged
            if self.state.get('has_untracked') or self.state.get('has_modifications'):
                self.state['has_staged'] = True
                self.state['has_untracked'] = False
                self.state['has_modifications'] = False
        
        elif name == 'commit_changes':
            # staged → ahead
            if self.state.get('has_staged'):
                self.state['has_staged'] = False
                self.state['is_ahead'] = True
        
        elif name == 'push_changes':
            # ahead → clean
            if self.state.get('is_ahead'):
                self.state['is_ahead'] = False
                self.state['is_behind'] = False
                self.state['is_clean'] = True
        
        return self.state.copy()
