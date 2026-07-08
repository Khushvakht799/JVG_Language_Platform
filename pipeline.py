"""
pipeline.py — Полный пайплайн JVG (с поддержкой .env)
Компиляция → Валидация → Хранение → Векторизация → Поиск
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List

# Загружаем .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv не обязателен

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'document'))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'validator'))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'storage'))
sys.path.append(os.path.join(BASE_DIR, '02_search', 'vectorizer'))
sys.path.append(os.path.join(BASE_DIR, '02_search', 'ranking'))

# Конфигурация из .env
STORAGE_DIR = os.getenv('STORAGE_DIR', 'jvg_store')
VECTOR_DB_PATH = os.getenv('VECTOR_DB_PATH', 'jvg_chroma_db')

# Импорты
try:
    from compiler import JVGCompiler
    from validator_pipeline import JVGValidatorPipeline
    from store import JVGStore
    from vectorizer import JVGVectorizer
    from ranking import JVGRankingEngine
except ModuleNotFoundError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что структура папок:")
    print("  JVG_Language_Platform/")
    print("  ├── 01_toolchain/")
    print("  │   ├── document/compiler.py")
    print("  │   ├── validator/validator_pipeline.py")
    print("  │   └── storage/store.py")
    print("  ├── 02_search/")
    print("  │   ├── vectorizer/vectorizer.py")
    print("  │   └── ranking/ranking.py")
    print("  └── pipeline.py")
    sys.exit(1)

class JVGPipeline:
    def __init__(self):
        self.storage_dir = STORAGE_DIR
        self.vector_db_path = VECTOR_DB_PATH
        self.compiler = JVGCompiler()
        self.validator = JVGValidatorPipeline()
        self.store = JVGStore(storage_dir=self.storage_dir)
        self.vectorizer = JVGVectorizer(db_path=self.vector_db_path)
        self.ranking = JVGRankingEngine(db_path=self.vector_db_path)

    def run(self, text: str, 
            search_query: str = None, 
            filters: Dict[str, Any] = None,
            save: bool = True,
            vectorize: bool = True,
            search: bool = True) -> Dict[str, Any]:
        result = {"status": "ok", "steps": {}, "errors": []}

        # Шаг 1: Компиляция
        print("📝 Шаг 1: Компиляция...")
        compile_result = self.compiler.compile(text)
        if compile_result["status"] != "success":
            result["status"] = "error"
            result["errors"].append(f"Компиляция: {compile_result.get('errors', 'неизвестная ошибка')}")
            return result
        jvg = compile_result["jvg"]
        result["steps"]["compile"] = {"status": "ok"}
        print("  ✅ Компиляция успешна")

        # Шаг 2: Валидация
        print("🔍 Шаг 2: Валидация...")
        valid, errors = self.validator.validate(jvg)
        if not valid:
            result["status"] = "warning"
            result["errors"].extend([f"Валидация: {e}" for e in errors])
            print(f"  ⚠️ Валидация: {len(errors)} предупреждений")
        else:
            result["steps"]["validate"] = {"status": "ok"}
            print("  ✅ Валидация успешна")

        # Шаг 3: Сохранение
        doc_id = None
        if save:
            print("💾 Шаг 3: Сохранение...")
            doc_id = self.store.save(jvg)
            result["steps"]["store"] = {"status": "ok", "doc_id": doc_id}
            print(f"  ✅ Сохранён: {doc_id}")

        # Шаг 4: Векторизация
        if vectorize and doc_id:
            print("🧠 Шаг 4: Векторизация...")
            vector = self.vectorizer.vectorize(jvg, doc_id)
            result["steps"]["vectorize"] = {"status": "ok", "dimension": len(vector)}
            print(f"  ✅ Векторизован (размерность: {len(vector)})")
            self.ranking.index_jvg(jvg, doc_id)
            print("  ✅ Индексация по слоям завершена")

        # Шаг 5: Поиск
        if search and search_query:
            print(f"🔎 Шаг 5: Поиск по запросу: '{search_query}'")
            results = self.ranking.search(search_query, filters=filters, top_k=10)
            result["steps"]["search"] = {"status": "ok", "query": search_query, "results": results}
            print(f"  ✅ Найдено: {len(results)} результатов")
            for i, r in enumerate(results[:3], 1):
                print(f"    {i}. {r.get('title', '')} ({r.get('type', '')}) — скор: {r['score']:.4f}")

        return result

    def search_only(self, query: str, filters: Dict[str, Any] = None, top_k: int = 10):
        return self.ranking.search(query, filters=filters, top_k=top_k)

def main():
    parser = argparse.ArgumentParser(description="JVG Pipeline")
    parser.add_argument("--file", type=str, help="Путь к файлу с текстом JVG")
    parser.add_argument("--text", type=str, help="Текст JVG (если не указан --file)")
    parser.add_argument("--query", type=str, help="Поисковый запрос")
    parser.add_argument("--filter-type", type=str, help="Фильтр по типу (система|процесс|идея|агент)")
    parser.add_argument("--no-save", action="store_true", help="Не сохранять JVG")
    parser.add_argument("--no-vectorize", action="store_true", help="Не векторизовать")
    parser.add_argument("--no-search", action="store_true", help="Не выполнять поиск")
    parser.add_argument("--search-only", action="store_true", help="Только поиск (без компиляции)")
    args = parser.parse_args()

    pipeline = JVGPipeline()

    if args.search_only:
        if not args.query:
            print("❌ Для поиска укажите --query")
            return
        filters = {}
        if args.filter_type:
            filters["type"] = args.filter_type
        results = pipeline.search_only(args.query, filters=filters)
        print(f"\n=== Результаты поиска: '{args.query}' ===")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.get('title', '')} ({r.get('type', '')}) — скор: {r['score']:.4f}")
        return

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        print("❌ Укажите --file или --text")
        return

    filters = {}
    if args.filter_type:
        filters["type"] = args.filter_type

    result = pipeline.run(
        text=text,
        search_query=args.query,
        filters=filters,
        save=not args.no_save,
        vectorize=not args.no_vectorize,
        search=not args.no_search
    )

    if result["status"] == "error":
        print(f"\n❌ Ошибка: {result['errors']}")
    else:
        print(f"\n✅ Пайплайн завершён. Статус: {result['status']}")

if __name__ == "__main__":
    main()
