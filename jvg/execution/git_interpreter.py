"""
jvg/execution/git_interpreter.py — Семантический интерпретатор для Git (с игнорированием)
"""

import re
import subprocess
from typing import Dict, Any, List

class GitInterpreter:
    # Папки и файлы, которые игнорируются при анализе
    IGNORED_PATHS = [
        "jvg_store/",
        "__pycache__/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".coverage",
        "htmlcov/",
        ".tox/",
        ".venv/",
        "venv/",
        "ENV/",
        "env/"
    ]

    @staticmethod
    def _is_ignored(file_name: str) -> bool:
        """Проверяет, нужно ли игнорировать файл."""
        for pattern in GitInterpreter.IGNORED_PATHS:
            if pattern in file_name:
                return True
        return False

    @staticmethod
    def interpret(status_output: str) -> Dict[str, Any]:
        facts = {
            "git": {
                "branch": "unknown",
                "ahead": False,
                "behind": False,
                "modified": [],
                "staged": [],
                "untracked": [],
                "conflicts": [],
                "clean": False
            }
        }

        lines = status_output.strip().split("\n") if status_output else []
        if not lines:
            return facts

        for line in lines:
            if line.startswith("On branch"):
                facts["git"]["branch"] = line.replace("On branch", "").strip()
                break
            elif "HEAD detached" in line:
                facts["git"]["branch"] = "detached"
                break

        full_text = "\n".join(lines)
        if "nothing to commit" in full_text and "working tree clean" in full_text:
            facts["git"]["clean"] = True
            return facts

        if "Your branch is ahead of" in full_text:
            facts["git"]["ahead"] = True

        if "Your branch is behind of" in full_text:
            facts["git"]["behind"] = True

        modified_section = False
        staged_section = False
        untracked_section = False
        conflict_section = False

        for line in lines:
            line = line.strip()

            if "Changes to be committed:" in line:
                staged_section = True
                modified_section = False
                untracked_section = False
                conflict_section = False
                continue

            if "Changes not staged for commit:" in line:
                modified_section = True
                staged_section = False
                untracked_section = False
                conflict_section = False
                continue

            if "Untracked files:" in line:
                untracked_section = True
                modified_section = False
                staged_section = False
                conflict_section = False
                continue

            if "Unmerged paths:" in line or "You have unmerged paths" in line:
                conflict_section = True
                continue

            # Извлекаем имена файлов (с проверкой игнорирования)
            if staged_section and line and not line.startswith("(") and not line.startswith("\t"):
                if ":" in line and not line.startswith("  "):
                    file_name = line.split(":")[-1].strip()
                    if file_name and not GitInterpreter._is_ignored(file_name):
                        facts["git"]["staged"].append(file_name)
                elif line.startswith("\t"):
                    file_name = line.replace("\t", "").strip()
                    if file_name and not GitInterpreter._is_ignored(file_name):
                        facts["git"]["staged"].append(file_name)

            if modified_section and line and not line.startswith("(") and not line.startswith("\t"):
                if ":" in line and not line.startswith("  "):
                    file_name = line.split(":")[-1].strip()
                    if file_name and not GitInterpreter._is_ignored(file_name):
                        facts["git"]["modified"].append(file_name)
                elif line.startswith("\t"):
                    file_name = line.replace("\t", "").strip()
                    if file_name and not GitInterpreter._is_ignored(file_name):
                        facts["git"]["modified"].append(file_name)

            if untracked_section and line and not line.startswith("(") and not line.startswith("\t"):
                if not line.startswith("  "):
                    file_name = line.strip()
                    if file_name and not file_name.startswith("(") and not GitInterpreter._is_ignored(file_name):
                        facts["git"]["untracked"].append(file_name)
                elif line.startswith("\t"):
                    file_name = line.replace("\t", "").strip()
                    if file_name and not GitInterpreter._is_ignored(file_name):
                        facts["git"]["untracked"].append(file_name)

            if conflict_section and line and not line.startswith("("):
                file_name = line.strip()
                if file_name and not GitInterpreter._is_ignored(file_name):
                    facts["git"]["conflicts"].append(file_name)

        if facts["git"]["modified"] or facts["git"]["staged"] or facts["git"]["untracked"]:
            facts["git"]["clean"] = False
        else:
            facts["git"]["clean"] = True

        return facts

    @staticmethod
    def get_current_status(repo_path: str = ".") -> Dict[str, Any]:
        try:
            result = subprocess.run(
                ["git", "-C", repo_path, "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return GitInterpreter.interpret(result.stdout)
            return {}
        except Exception:
            return {}
