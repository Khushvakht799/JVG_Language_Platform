"""
benchmark.py — Бенчмарк JVG Platform
Замер производительности всех компонентов.
"""

import time
import json
import statistics
from typing import Dict, Any, List
from datetime import datetime

from jvg import (
    JVGCompiler, JVGValidatorPipeline, JVGStore, 
    JVGVectorizer, JVGRankingEngine, JVGRuntime
)

class JVGBenchmark:
    def __init__(self):
        self.compiler = JVGCompiler()
        self.validator = JVGValidatorPipeline()
        self.store = JVGStore()
        self.vectorizer = JVGVectorizer()
        self.ranking = JVGRankingEngine()
        self.runtime = JVGRuntime()
        self.results = {}

    def measure(self, name: str, func, *args, **kwargs) -> float:
        """Замеряет время выполнения функции."""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        self.results[name] = {"time": elapsed, "result": result}
        print(f"  {name}: {elapsed:.4f} сек")
        return result

    def run_compilation_benchmark(self, iterations: int = 10):
        """Бенчмарк компиляции."""
        print("\n📝 Бенчмарк компиляции...")
        text = """
entity:
  name: Тестовая система
  type: система
  purpose: бенчмарк
state:
  current: ИССЛЕДОВАНИЕ
actions:
  next_steps: протестировать, развернуть
"""
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            result = self.compiler.compile(text)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        avg = statistics.mean(times)
        min_t = min(times)
        max_t = max(times)
        self.results["compilation"] = {
            "avg": avg,
            "min": min_t,
            "max": max_t,
            "iterations": iterations
        }
        print(f"  ✅ Компиляция: ср. {avg:.4f} сек, мин. {min_t:.4f}, макс. {max_t:.4f}")

    def run_validation_benchmark(self, iterations: int = 10):
        """Бенчмарк валидации."""
        print("\n🔍 Бенчмарк валидации...")
        # Сначала создаём JVG
        text = """
entity:
  name: Тестовая система
  type: система
  purpose: бенчмарк
state:
  current: ИССЛЕДОВАНИЕ
actions:
  next_steps: протестировать, развернуть
"""
        result = self.compiler.compile(text)
        jvg = result["jvg"]
        
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            valid, errors = self.validator.validate(jvg)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        avg = statistics.mean(times)
        min_t = min(times)
        max_t = max(times)
        self.results["validation"] = {
            "avg": avg,
            "min": min_t,
            "max": max_t,
            "iterations": iterations
        }
        print(f"  ✅ Валидация: ср. {avg:.4f} сек, мин. {min_t:.4f}, макс. {max_t:.4f}")

    def run_storage_benchmark(self, iterations: int = 10):
        """Бенчмарк хранилища."""
        print("\n💾 Бенчмарк хранилища...")
        text = """
entity:
  name: Тестовая система
  type: система
  purpose: бенчмарк
"""
        result = self.compiler.compile(text)
        jvg = result["jvg"]
        
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            doc_id = self.store.save(jvg)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        avg = statistics.mean(times)
        min_t = min(times)
        max_t = max(times)
        self.results["storage"] = {
            "avg": avg,
            "min": min_t,
            "max": max_t,
            "iterations": iterations
        }
        print(f"  ✅ Хранилище: ср. {avg:.4f} сек, мин. {min_t:.4f}, макс. {max_t:.4f}")

    def run_vectorization_benchmark(self, iterations: int = 10):
        """Бенчмарк векторизации."""
        print("\n🧠 Бенчмарк векторизации...")
        text = """
entity:
  name: Тестовая система
  type: система
  purpose: бенчмарк векторизации
"""
        result = self.compiler.compile(text)
        jvg = result["jvg"]
        doc_id = self.store.save(jvg)
        
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            vector = self.vectorizer.vectorize(jvg, doc_id)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        avg = statistics.mean(times)
        min_t = min(times)
        max_t = max(times)
        self.results["vectorization"] = {
            "avg": avg,
            "min": min_t,
            "max": max_t,
            "iterations": iterations
        }
        print(f"  ✅ Векторизация: ср. {avg:.4f} сек, мин. {min_t:.4f}, макс. {max_t:.4f}")

    def run_search_benchmark(self, iterations: int = 10):
        """Бенчмарк поиска."""
        print("\n🔎 Бенчмарк поиска...")
        query = "система"
        
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            results = self.ranking.search(query, top_k=5)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        avg = statistics.mean(times)
        min_t = min(times)
        max_t = max(times)
        self.results["search"] = {
            "avg": avg,
            "min": min_t,
            "max": max_t,
            "iterations": iterations
        }
        print(f"  ✅ Поиск: ср. {avg:.4f} сек, мин. {min_t:.4f}, макс. {max_t:.4f}")

    def run_runtime_benchmark(self, iterations: int = 10):
        """Бенчмарк Runtime."""
        print("\n⚡ Бенчмарк Runtime...")
        text = """
entity:
  name: Тестовый процесс
  type: процесс
  purpose: бенчмарк
state:
  current: ИССЛЕДОВАНИЕ
actions:
  next_steps: протестировать, развернуть
"""
        result = self.compiler.compile(text)
        jvg = result["jvg"]
        doc_id = self.store.save(jvg)
        
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            step_result = self.runtime.step(doc_id, "ПРОЕКТИРОВАНИЕ", "начало")
            elapsed = time.perf_counter() - start
            times.append(elapsed)
            # Обновляем doc_id для следующей итерации
            if "updated_doc_id" in step_result:
                doc_id = step_result["updated_doc_id"]
        
        avg = statistics.mean(times)
        min_t = min(times)
        max_t = max(times)
        self.results["runtime"] = {
            "avg": avg,
            "min": min_t,
            "max": max_t,
            "iterations": iterations
        }
        print(f"  ✅ Runtime: ср. {avg:.4f} сек, мин. {min_t:.4f}, макс. {max_t:.4f}")

    def run_all(self, iterations: int = 10):
        """Запускает все бенчмарки."""
        print("=" * 50)
        print("📊 JVG Platform — Бенчмарк")
        print(f"   Итераций: {iterations}")
        print("=" * 50)
        
        self.run_compilation_benchmark(iterations)
        self.run_validation_benchmark(iterations)
        self.run_storage_benchmark(iterations)
        self.run_vectorization_benchmark(iterations)
        self.run_search_benchmark(iterations)
        self.run_runtime_benchmark(iterations)
        
        print("\n" + "=" * 50)
        print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        print("=" * 50)
        for name, data in self.results.items():
            if isinstance(data, dict) and "avg" in data:
                print(f"  {name}: {data['avg']:.4f} сек (ср.) | {data['min']:.4f} (мин) | {data['max']:.4f} (макс)")
            else:
                print(f"  {name}: {data}")
        
        # Сохраняем результаты
        with open("benchmark_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print("\n✅ Результаты сохранены в benchmark_results.json")


def main():
    benchmark = JVGBenchmark()
    benchmark.run_all(iterations=10)

if __name__ == "__main__":
    main()
