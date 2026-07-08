"""
cognitive_integration.py — Полная интеграция с Cognitive OS (L1–L5)
Замкнутый цикл: реальность → память → модели → исполнение → аудит.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from jvg import (
    JVGCompiler, JVGValidatorPipeline, JVGStore, 
    JVGVectorizer, JVGRankingEngine, JVGRuntime,
    L1Adapter, L2Memory, L3Models, L4Execution, L5Audit,
    PreferenceProfile, MetricsCollector, FeedbackEngine,
    IdentityRegistry, UID, VersionedObject, generate_uid
)

class CognitiveIntegration:
    """Полный цикл Cognitive OS."""
    
    def __init__(self):
        self.compiler = JVGCompiler()
        self.validator = JVGValidatorPipeline()
        self.store = JVGStore()
        self.vectorizer = JVGVectorizer()
        self.ranking = JVGRankingEngine()
        self.runtime = JVGRuntime()
        self.l1 = L1Adapter()
        self.l2 = L2Memory()
        self.l3 = L3Models(self.l2)
        self.l4 = L4Execution()
        self.l5 = L5Audit()
        self.metrics = MetricsCollector()
        self.feedback = FeedbackEngine()
        self.registry = IdentityRegistry()
    
    def process_real_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        L1 → L2 → L3 → L4 → L5
        Полный цикл обработки события из реальности.
        """
        print("=" * 50)
        print("🔄 L1: Обработка события из реальности")
        print(f"   Событие: {event.get('title', 'без названия')}")
        
        # L1: Реальность → JVG
        jvg = self.l1.event_to_jvg(event)
        print("   ✅ L1: Событие → JVG")
        
        # L5: Аудит (проверка)
        audit = self.l5.validate(jvg)
        print(f"   ✅ L5: Аудит — {'пройден' if audit['valid'] else 'есть ошибки'}")
        
        # L2: Память (сохранение + векторизация)
        doc_id = self.l2.save(jvg)
        print(f"   ✅ L2: Сохранено в память — ID: {doc_id}")
        
        # L3: Модели (анализ состояния)
        analysis = self.l3.analyze_state(doc_id)
        print(f"   ✅ L3: Анализ — состояние: {analysis['state']}")
        
        # L4: Исполнение (если нужно выполнить действия)
        if analysis.get('is_healthy', False) and analysis.get('next_suggested_state'):
            result = self.l4.step(
                doc_id, 
                new_state=analysis['next_suggested_state'],
                action_result=f"Автоматический переход по анализу L3"
            )
            print(f"   ✅ L4: Исполнение — {result.get('new_state', 'без изменений')}")
        
        # Сбор метрик
        self.metrics.record_event(
            event_type="cognitive_cycle",
            doc_id=doc_id,
            metrics={
                "status": "success",
                "state": analysis.get('state', 'unknown'),
                "problems": len(jvg.get('vectorograph', {}).get('state', {}).get('problems', []))
            }
        )
        
        return {
            "doc_id": doc_id,
            "jvg": jvg,
            "audit": audit,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Обработка текста через полный цикл.
        """
        print("=" * 50)
        print("📝 Обработка текста через полный цикл")
        
        # Компиляция
        compile_result = self.compiler.compile(text)
        if compile_result["status"] != "success":
            return {"status": "error", "errors": compile_result.get("errors", [])}
        
        jvg = compile_result["jvg"]
        print("   ✅ Компиляция успешна")
        
        # Валидация
        valid, errors = self.validator.validate(jvg)
        print(f"   ✅ Валидация: {'пройдена' if valid else 'есть предупреждения'}")
        
        # Сохранение
        doc_id = self.l2.save(jvg)
        print(f"   ✅ Сохранено: {doc_id}")
        
        # Анализ
        analysis = self.l3.analyze_state(doc_id)
        print(f"   ✅ Анализ: состояние {analysis['state']}")
        
        # Аудит
        explanation = self.l5.explain(doc_id, jvg)
        print(f"   ✅ Аудит: {explanation[:100]}...")
        
        return {
            "status": "success",
            "doc_id": doc_id,
            "jvg": jvg,
            "analysis": analysis,
            "explanation": explanation
        }
    
    def run_feedback_cycle(self, doc_id: str = None):
        """
        Запускает цикл обратной связи.
        """
        print("=" * 50)
        print("🔄 Запуск цикла обратной связи")
        
        # Собираем метрики
        metrics = self.feedback.analyze(window_days=7)
        print(f"   📊 Собрано метрик: {len(metrics)}")
        
        # Генерируем рекомендации
        recommendations = self.feedback.evaluate(metrics)
        print(f"   📋 Рекомендаций: {len(recommendations)}")
        
        # Применяем
        result = self.feedback.apply_recommendations(recommendations, auto_apply=True)
        print(f"   ✅ Применено изменений: {len(result['changes'])}")
        
        return result


def test_cognitive_integration():
    """Тестирует полный цикл."""
    print("🧪 Тестирование Cognitive Integration")
    print("=" * 50)
    
    integration = CognitiveIntegration()
    
    # Тест 1: Обработка события
    event = {
        "title": "Системный сбой на сервере",
        "entity": "сервер",
        "source": "мониторинг",
        "purpose": "восстановление работы",
        "actions": ["проверить логи", "перезапустить сервис"],
        "problems": ["отказ сервера"],
        "risks": ["потеря данных"]
    }
    result = integration.process_real_event(event)
    print(f"\n✅ Результат: {result['doc_id']}")
    
    # Тест 2: Обработка текста
    text = """
entity:
  name: Тестовая система
  type: система
  purpose: проверка Cognitive OS
state:
  current: ИССЛЕДОВАНИЕ
actions:
  next_steps: протестировать, развернуть
"""
    result = integration.process_text(text)
    print(f"\n✅ Результат: {result['doc_id']}")
    
    # Тест 3: Цикл обратной связи
    print("\n")
    integration.run_feedback_cycle()

if __name__ == "__main__":
    test_cognitive_integration()
