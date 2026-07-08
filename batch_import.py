"""
batch_import.py — Пакетный импорт JVG
Загружает все .txt файлы из папки, компилирует, валидирует, сохраняет, векторизует.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List
from datetime import datetime

# Добавляем пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'document'))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'validator'))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'storage'))
sys.path.append(os.path.join(BASE_DIR, '02_search', 'vectorizer'))
sys.path.append(os.path.join(BASE_DIR, '02_search', 'ranking'))
sys.path.append(os.path.join(BASE_DIR, '03_runtime'))

from compiler import JVGCompiler
from validator_pipeline import JVGValidatorPipeline
from store import JVGStore
from vectorizer import JVGVectorizer
from ranking import JVGRankingEngine

class BatchImporter:
    def __init__(self, 
                 input_dir: str = "05_examples",
                 storage_dir: str = "jvg_store",
                 vector_db_path: str = "jvg_chroma_db"):
        self.input_dir = input_dir
        self.compiler = JVGCompiler()
        self.validator = JVGValidatorPipeline()
        self.store = JVGStore(storage_dir=storage_dir)
        self.vectorizer = JVGVectorizer(db_path=vector_db_path)
        self.ranking = JVGRankingEngine(db_path=vector_db_path)
        self.results = []

    def import_all(self, verbose: bool = True) -> Dict[str, Any]:
        """Импортирует все .txt файлы из input_dir."""
        if not os.path.exists(self.input_dir):
            os.makedirs(self.input_dir)
            return {"status": "warning", "message": f"Папка {self.input_dir} создана. Добавьте .txt файлы."}

        files = [f for f in os.listdir(self.input_dir) if f.endswith('.txt')]
        if not files:
            return {"status": "warning", "message": f"В {self.input_dir} нет .txt файлов"}

        print(f"📁 Найдено {len(files)} файлов")
        success_count = 0
        error_count = 0

        for filename in files:
            filepath = os.path.join(self.input_dir, filename)
            print(f"\n📄 Обработка: {filename}")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Компиляция
                compile_result = self.compiler.compile(text)
                if compile_result["status"] != "success":
                    print(f"  ❌ Ошибка компиляции: {compile_result.get('errors')}")
                    error_count += 1
                    continue
                
                jvg = compile_result["jvg"]
                
                # Валидация
                valid, errors = self.validator.validate(jvg)
                if not valid:
                    print(f"  ⚠️ Валидация: {len(errors)} предупреждений")
                
                # Сохранение
                doc_id = self.store.save(jvg)
                
                # Векторизация
                self.vectorizer.vectorize(jvg, doc_id)
                self.ranking.index_jvg(jvg, doc_id)
                
                print(f"  ✅ Импортирован: {doc_id}")
                success_count += 1
                
                self.results.append({
                    "file": filename,
                    "doc_id": doc_id,
                    "status": "success",
                    "errors": errors
                })
                
            except Exception as e:
                print(f"  ❌ Ошибка: {str(e)}")
                error_count += 1
                self.results.append({
                    "file": filename,
                    "status": "error",
                    "error": str(e)
                })

        return {
            "status": "ok",
            "total": len(files),
            "success": success_count,
            "errors": error_count,
            "results": self.results
        }


def main():
    parser = argparse.ArgumentParser(description="Пакетный импорт JVG")
    parser.add_argument("--dir", type=str, default="05_examples", help="Папка с .txt файлами")
    parser.add_argument("--storage", type=str, default="jvg_store", help="Папка хранилища")
    parser.add_argument("--vectors", type=str, default="jvg_chroma_db", help="Папка векторной БД")
    
    args = parser.parse_args()
    
    importer = BatchImporter(
        input_dir=args.dir,
        storage_dir=args.storage,
        vector_db_path=args.vectors
    )
    
    result = importer.import_all()
    
    print("\n" + "="*50)
    print(f"📊 ИТОГИ ИМПОРТА")
    print(f"  Всего файлов: {result.get('total', 0)}")
    print(f"  Успешно: {result.get('success', 0)}")
    print(f"  Ошибок: {result.get('errors', 0)}")
    print("="*50)

if __name__ == "__main__":
    main()
