"""
metrics.py — Behavior Metrics для JVG
Собирает и анализирует поведенческие метрики.
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

@dataclass
class BehaviorMetrics:
    """Набор поведенческих метрик."""
    
    # Runtime Metrics
    latency_avg_ms: float = 0.0
    cpu_usage_percent: float = 0.0
    ram_usage_mb: float = 0.0
    token_usage_total: int = 0
    
    # Learning Metrics
    adaptation_score: float = 0.0
    preference_shift: float = 0.0
    correction_count: int = 0
    drift_detected: bool = False
    
    # Quality Metrics
    success_rate: float = 0.0
    user_acceptance: float = 0.0
    semantic_accuracy: float = 0.0
    error_rate: float = 0.0
    
    # Aggregates
    total_queries: int = 0
    total_compilations: int = 0
    total_searches: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BehaviorMetrics':
        return cls(**data)


class MetricsCollector:
    """Сборщик поведенческих метрик."""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Инициализирует базу данных для метрик."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                doc_id TEXT,
                metrics TEXT,
                context TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics_aggregates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                metric_name TEXT,
                value REAL,
                window TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def record_event(self, event_type: str, doc_id: str = None, 
                     metrics: Dict[str, Any] = None, context: Dict[str, Any] = None):
        """Записывает событие с метриками."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO metrics_events (timestamp, event_type, doc_id, metrics, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            event_type,
            doc_id or "",
            json.dumps(metrics or {}, ensure_ascii=False),
            json.dumps(context or {}, ensure_ascii=False)
        ))
        conn.commit()
        conn.close()
    
    def get_aggregates(self, metric_name: str, window: str = "day") -> List[Dict[str, Any]]:
        """Получает агрегированные метрики за период."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, value FROM metrics_aggregates
            WHERE metric_name = ? AND window = ?
            ORDER BY timestamp DESC
            LIMIT 100
        ''', (metric_name, window))
        results = [{"timestamp": row[0], "value": row[1]} for row in cursor.fetchall()]
        conn.close()
        return results
    
    def record_aggregate(self, metric_name: str, value: float, window: str = "day"):
        """Записывает агрегированную метрику."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO metrics_aggregates (timestamp, metric_name, value, window)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), metric_name, value, window))
        conn.commit()
        conn.close()


# ============================================================
# Интеграция с ранжированием и рантаймом
# ============================================================

def update_ranking_metrics(ranking_engine, query: str, results: List[Dict], 
                           collector: MetricsCollector):
    """Обновляет метрики на основе результатов ранжирования."""
    collector.record_event(
        event_type="search",
        metrics={
            "query": query,
            "results_count": len(results),
            "top_score": results[0]["score"] if results else 0.0
        }
    )


def update_runtime_metrics(runtime, doc_id: str, result: Dict, 
                           collector: MetricsCollector):
    """Обновляет метрики на основе выполнения шага Runtime."""
    collector.record_event(
        event_type="runtime_step",
        doc_id=doc_id,
        metrics={
            "new_state": result.get("new_state"),
            "old_state": result.get("old_state"),
            "status": result.get("status")
        }
    )
