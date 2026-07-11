"""
commit_git.py — Выполняет Git commit через JVG (исправленный)
"""

from jvg import ActionExecutor

def main():
    print("📤 Выполнение Git commit...")
    
    result = ActionExecutor.execute(
        "run_git",
        {
            "command": 'commit -m "JVG automatic commit"'
        }
    )
    
    print(f"✅ success  : {result.success}")
    print(f"exit_code : {result.exit_code}")
    print(f"stdout    :\n{result.stdout}")
    print(f"stderr    :\n{result.stderr}")
    print(f"error     : {result.error}")

if __name__ == "__main__":
    main()
