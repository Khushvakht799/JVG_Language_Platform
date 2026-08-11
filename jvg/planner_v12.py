"""
jvg/planner_v12.py — Experience-Based Planner с WorldModel
"""

from typing import Dict, Any, List, Optional
from jvg.models.world_model import WorldModel
from jvg.models.fake_world_model import FakeWorldModel
from jvg.store import JVGStore

class PlannerV12:
    def __init__(self, store: Optional[JVGStore] = None, model: Optional[WorldModel] = None):
        self.store = store
        self.model = model
        self.goal = {}
        self.max_iterations = 10
        self.experience = []
        self._current_doc_id = None
    
    def set_goal(self, goal: Dict[str, Any]):
        """Установить целевую цель"""
        self.goal = goal
    
    def run(self, doc_id: str) -> Dict[str, Any]:
        """Запустить планировщик для документа"""
        self._current_doc_id = doc_id
        iterations = 0
        
        while iterations < self.max_iterations:
            state = self.model.get_state()
            
            # Проверка достижения цели
            if self._goal_reached(state):
                return {
                    'status': 'success',
                    'iterations': iterations,
                    'final_state': state
                }
            
            # Построить план
            actions = self._build_plan(state)
            
            if not actions:
                return {
                    'status': 'stuck',
                    'iterations': iterations,
                    'final_state': state,
                    'error': 'No actions available'
                }
            
            # Выполнить первое действие
            action = actions[0]
            
            # Применить действие к модели мира
            new_state = self.model.apply_action(action)
            
            # Сохранить опыт
            self.experience.append({
                'state': state.copy(),
                'action': action.copy(),
                'new_state': new_state.copy(),
                'score': 1.0 if self._goal_reached(new_state) else 0.0
            })
            
            iterations += 1
        
        return {
            'status': 'timeout',
            'iterations': iterations,
            'final_state': self.model.get_state()
        }
    
    def _goal_reached(self, state: Dict) -> bool:
        """Проверить, достигнута ли цель"""
        for key, value in self.goal.items():
            if state.get(key) != value:
                return False
        return True
    
    def _build_plan(self, state: Dict) -> List[Dict]:
        """Построить план на основе текущего состояния"""
        plan = []
        
        # Простые правила (позже заменим на поиск)
        if state.get('has_untracked') or state.get('has_modifications'):
            plan.append({'name': 'add_changes', 'params': {}})
        
        if state.get('has_staged'):
            plan.append({'name': 'commit_changes', 'params': {}})
        
        if state.get('is_ahead'):
            plan.append({'name': 'push_changes', 'params': {}})
        
        return plan
