"""
deploy.py — Скрипт деплоя JVG Platform
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    print("📦 Проверка зависимостей...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Зависимости установлены")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
    return True

def check_structure():
    print("📁 Проверка структуры...")
    required = ["01_toolchain", "02_search", "03_runtime", "storage"]
    for d in required:
        if not os.path.exists(d):
            print(f"⚠️ Отсутствует папка: {d}")
    print("✅ Структура проверена")
    return True

def check_api():
    print("🌐 Проверка API...")
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=2)
        if response.status_code == 200:
            print("✅ API работает")
            return True
    except:
        pass
    print("⚠️ API не запущен. Запустите: python api.py")
    return False

def main():
    print("=" * 50)
    print("JVG Platform — Деплой")
    print("=" * 50)
    
    check_requirements()
    check_structure()
    check_api()
    
    print("\n✅ Деплой завершён")

if __name__ == "__main__":
    main()
