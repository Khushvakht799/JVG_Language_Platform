"""
feedback_engine.py — Feedback Engine для JVG
Анализирует метрики и обновляет Preference Profile.
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from preference import PreferenceProfile, ARCHITECT_PROFILE
from metrics import MetricsCollector


@dataclass
class AdaptationRule:
    """Правило адаптации профиля."""
    condition: str
    action: str
    delta: float
    policy: str  # "recommend_only", "confirm_required", "autonomous"
    description: str


class FeedbackEngine:
    """Двигатель обратной связи — замыкает цикл управления."""
    
    def __init__(self, db_path: str = "metrics.db", profile_path: str = "preference_profile.json"):
        self.collector = MetricsCollector(db_path=db_path)
        self.profile_path = profile_path
        self.rules = self._default_rules()
    
    def _default_rules(self) -> List[AdaptationRule]:
        """Правила адаптации по умолчанию."""
        return [
            AdaptationRule(
                condition="success_rate < 0.7",
                action="decrease_abstraction_tolerance",
                delta=-0.1,
                policy="confirm_required",
                description="При низкой успешности снижаем уровень абстракции"
            ),
            AdaptationRule(
                condition="user_acceptance > 0.9 AND correction_count < 3",
                action="lock_profile",
                delta=0.0,
                policy="recommend_only",
                description="При высокой удовлетворённости закрепляем профиль"
            ),
            AdaptationRule(
                condition="preference_shift > 0.2",
                action="request_confirmation",
                delta=0.0,
                policy="confirm_required",
                description="При значительном сдвиге предпочтений запрашиваем подтверждение"
            ),
            AdaptationRule(
                condition="avg_response_tokens > 500 AND user_acceptance < 0.6",
                action="decrease_time_priority",
                delta=-0.05,
                policy="autonomous",
                description="При долгих ответах и низкой оценке снижаем приоритет времени"
            ),
            AdaptationRule(
                condition="search_top_score < 0.3",
                action="increase_automation",
                delta=0.05,
                policy="autonomous",
                description="При низкой релевантности поиска повышаем автоматизацию"
            )
        ]
    
    def analyze(self, window_days: int = 7) -> Dict[str, Any]:
        """Анализирует метрики за последние N дней."""
        conn = sqlite3.connect(self.collector.db_path)
        cursor = conn.cursor()
        
        # Получаем агрегаты
        cursor.execute('''
            SELECT metric_name, AVG(value) as avg_value, COUNT(*) as count
            FROM metrics_aggregates
            WHERE timestamp > datetime('now', ?)
            GROUP BY metric_name
        ''', (f'-{window_days} days',))
        
        aggregates = {}
        for row in cursor.fetchall():
            aggregates[row[0]] = {"avg": row[1], "count": row[2]}
        
        conn.close()
        return aggregates
    
    def evaluate(self, metrics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Оценивает метрики по правилам."""
        recommendations = []
        
        for rule in self.rules:
            # Проверяем условие
            condition_met = self._evaluate_condition(rule.condition, metrics_data)
            if condition_met:
                recommendations.append({
                    "rule": rule,
                    "condition": rule.condition,
                    "action": rule.action,
                    "delta": rule.delta,
                    "policy": rule.policy,
                    "description": rule.description,
                    "timestamp": datetime.now().isoformat()
                })
        
        return recommendations
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Вычисляет условие."""
        try:
            # Безопасно вычисляем условие
            # Для реального использования нужен парсер выражений
            # Сейчас используем упрощённую проверку
            if "success_rate" in condition:
                rate = data.get("success_rate", 1.0)
                threshold = float(condition.split("<")[1].strip())
                return rate < threshold
            elif "user_acceptance" in condition:
                acceptance = data.get("user_acceptance", 0.0)
                threshold = float(condition.split(">")[1].strip())
                return acceptance > threshold
            elif "preference_shift" in condition:
                shift = data.get("preference_shift", 0.0)
                threshold = float(condition.split(">")[1].strip())
                return shift > threshold
            elif "avg_response_tokens" in condition:
                tokens = data.get("avg_response_tokens", 0)
                threshold = float(condition.split(">")[1].strip())
                return tokens > threshold
            elif "search_top_score" in condition:
                score = data.get("search_top_score", 0.0)
                threshold = float(condition.split("<")[1].strip())
                return score < threshold
            elif "correction_count" in condition:
                count = data.get("correction_count", 0)
                threshold = float(condition.split("<")[1].strip())
                return count < threshold
        except Exception:
            pass
        return False
    
    def apply_recommendations(self, recommendations: List[Dict[str, Any]], 
                              auto_apply: bool = False) -> Dict[str, Any]:
        """Применяет рекомендации к профилю."""
        # Загружаем текущий профиль
        if os.path.exists(self.profile_path):
            profile = PreferenceProfile.load(self.profile_path)
        else:
            profile = ARCHITECT_PROFILE
        
        changes = []
        for rec in recommendations:
            policy = rec["policy"]
            action = rec["action"]
            delta = rec["delta"]
            
            if policy == "autonomous" or (policy == "confirm_required" and auto_apply):
                # Применяем изменение
                if action == "decrease_abstraction_tolerance":
                    profile.AbstractionTolerance = max(0.0, profile.AbstractionTolerance + delta)
                    changes.append({
                        "field": "AbstractionTolerance",
                        "old_value": profile.AbstractionTolerance - delta,
                        "new_value": profile.AbstractionTolerance,
                        "delta": delta
                    })
                elif action == "decrease_time_priority":
                    profile.TimePriority = max(0.0, profile.TimePriority + delta)
                    changes.append({
                        "field": "TimePriority",
                        "old_value": profile.TimePriority - delta,
                        "new_value": profile.TimePriority,
                        "delta": delta
                    })
                elif action == "increase_automation":
                    profile.AutomationPreference = min(1.0, profile.AutomationPreference + delta)
                    changes.append({
                        "field": "AutomationPreference",
                        "old_value": profile.AutomationPreference - delta,
                        "new_value": profile.AutomationPreference,
                        "delta": delta
                    })
        
        # Сохраняем профиль, если были изменения
        if changes:
            profile.save(self.profile_path)
            self.collector.record_event(
                event_type="profile_updated",
                metrics={"changes": changes}
            )
        
        return {
            "profile": profile.to_dict(),
            "changes": changes,
            "recommendations_applied": len(changes),
            "total_recommendations": len(recommendations)
        }
    
    def run(self, auto_apply: bool = False, window_days: int = 7) -> Dict[str, Any]:
        """Полный цикл анализа и адаптации."""
        print("🔄 Запуск Feedback Engine...")
        
        # 1. Анализ метрик
        metrics = self.analyze(window_days=window_days)
        print(f"  📊 Проанализировано метрик: {len(metrics)}")
        
        # 2. Оценка по правилам
        recommendations = self.evaluate(metrics)
        print(f"  📋 Сгенерировано рекомендаций: {len(recommendations)}")
        
        # 3. Применение
        result = self.apply_recommendations(recommendations, auto_apply=auto_apply)
        print(f"  ✅ Применено изменений: {len(result['changes'])}")
        
        return result


# ============================================================
# Тест
# ============================================================

def test_feedback_engine():
    """Тестирует Feedback Engine."""
    engine = FeedbackEngine()
    
    # Создаём тестовые метрики
    metrics_data = {
        "success_rate": 0.65,
        "user_acceptance": 0.95,
        "preference_shift": 0.25,
        "avg_response_tokens": 600,
        "search_top_score": 0.25,
        "correction_count": 2
    }
    
    print("=== Тест Feedback Engine ===")
    print("Входные метрики:", json.dumps(metrics_data, indent=2, ensure_ascii=False))
    
    # Оцениваем
    recommendations = engine.evaluate(metrics_data)
    print(f"\nРекомендаций: {len(recommendations)}")
    for rec in recommendations:
        print(f"  - {rec['description']} (политика: {rec['policy']})")
    
    # Применяем с подтверждением
    print("\nПрименяем изменения (auto_apply=True)...")
    result = engine.apply_recommendations(recommendations, auto_apply=True)
    print(f"Изменений: {len(result['changes'])}")
    print("Новый профиль:", json.dumps(result['profile'], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_feedback_engine()
