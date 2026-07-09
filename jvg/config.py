"""
config.py — Конфигурация JVG
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.absolute()
STORAGE_DIR = PROJECT_ROOT / "jvg_store"
STORAGE_DIR.mkdir(exist_ok=True)

JVG_STORE_PATH = str(STORAGE_DIR)
CHROMA_DB_PATH = str(PROJECT_ROOT / "jvg_chroma_db")
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

def get_store_path() -> str:
    return JVG_STORE_PATH

def get_vector_db_path() -> str:
    return CHROMA_DB_PATH
