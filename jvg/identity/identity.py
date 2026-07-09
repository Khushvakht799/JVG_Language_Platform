"""
jvg/identity/identity.py — Идентичность и версионирование
"""

import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

class Identity:
    @staticmethod
    def generate_uid(entity_name: str, context: str = "") -> str:
        """Генерирует уникальный идентификатор."""
        hash_suffix = hashlib.md5(context.encode()).hexdigest()[:6]
        name = "".join(c for c in entity_name if c.isalnum() or c in " ._-")
        name = name.replace(" ", "_")
        return f"jvg://{name}_{hash_suffix}"

    @staticmethod
    def version(jvg: Dict[str, Any], new_state: str) -> Dict[str, Any]:
        """Обновляет версию документа."""
        if "vectorograph" not in jvg:
            jvg["vectorograph"] = {}
        if "meta" not in jvg["vectorograph"]:
            jvg["vectorograph"]["meta"] = {}
        
        meta = jvg["vectorograph"]["meta"]
        current_version = meta.get("version", "0")
        
        try:
            v = int(current_version) + 1
        except ValueError:
            v = 1
        
        meta["version"] = str(v)
        meta["previous_state"] = jvg["vectorograph"].get("state", {}).get("current", "unknown")
        meta["updated_at"] = datetime.now().isoformat()
        
        return jvg
