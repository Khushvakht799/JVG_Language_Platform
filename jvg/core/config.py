"""
jvg/core/config.py — Единая конфигурация
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
STORAGE_DIR = PROJECT_ROOT / "jvg_store"
CHROMA_DIR = PROJECT_ROOT / "jvg_chroma_db"

STORAGE_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)

class Config:
    STORAGE_PATH = str(STORAGE_DIR)
    CHROMA_PATH = str(CHROMA_DIR)
    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
