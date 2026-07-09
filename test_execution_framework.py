"""
test_execution_framework.py — Проверка Execution Framework
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from jvg import ActionExecutor, ExecutorRegistry

def main():
    print("=== Execution Framework Test ===")
    print(f"Зарегистрировано исполнителей: {len(ExecutorRegistry.list())}")
    print(f"Список: {ExecutorRegistry.list()}")

    # Тест CmdExecutor
    result = ActionExecutor.execute("run_cmd", {"command": "echo Hello from JVG"})
    print(f"\nРезультат run_cmd:")
    print(f"  success: {result.success}")
    print(f"  stdout: {result.stdout}")
    print(f"  exit_code: {result.exit_code}")
    print(f"  duration: {result.duration:.3f}s")

    # Тест PowerShellExecutor
    result = ActionExecutor.execute("run_powershell", {"command": "Write-Host 'Hello from PowerShell'"})
    print(f"\nРезультат run_powershell:")
    print(f"  success: {result.success}")
    print(f"  stdout: {result.stdout}")
    print(f"  exit_code: {result.exit_code}")
    print(f"  duration: {result.duration:.3f}s")

    # Тест UrlExecutor
    result = ActionExecutor.execute("open_url", {"url": "https://example.com"})
    print(f"\nРезультат open_url:")
    print(f"  success: {result.success}")
    print(f"  stdout: {result.stdout}")
    print(f"  duration: {result.duration:.3f}s")

    # Тест неизвестного исполнителя
    result = ActionExecutor.execute("unknown_action", {})
    print(f"\nРезультат unknown_action:")
    print(f"  success: {result.success}")
    print(f"  error: {result.error}")

if __name__ == "__main__":
    main()
