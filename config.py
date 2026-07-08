"""
config.py — Единая конфигурация JVG Platform
"""

import os
from pathlib import Path

# Корень проекта
PROJECT_ROOT = Path(__file__).parent.absolute()

# Единое хранилище
STORAGE_DIR = PROJECT_ROOT / "storage"
STORAGE_DIR.mkdir(exist_ok=True)

# Пути к базам
JVG_STORE_PATH = STORAGE_DIR / "jvg_store"
CHROMA_DB_PATH = STORAGE_DIR / "chroma_db"

# Создаём папки
JVG_STORE_PATH.mkdir(exist_ok=True)
CHROMA_DB_PATH.mkdir(exist_ok=True)

# Настройки
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K_DEFAULT = 5
LOG_LEVEL = "INFO"

# Функция для получения путей
def get_store_path() -> str:
    return str(JVG_STORE_PATH)

def get_vector_db_path() -> str:
    return str(CHROMA_DB_PATH)

if __name__ == "__main__":
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"JVG_STORE_PATH: {JVG_STORE_PATH}")
    print(f"CHROMA_DB_PATH: {CHROMA_DB_PATH}")
