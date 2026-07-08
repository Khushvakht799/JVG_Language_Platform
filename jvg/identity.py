"""
identity.py — Модель идентичности для JVG
UID, пространства имён, версионирование, ссылки.
"""

import re
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class ReferenceType(Enum):
    """Тип ссылки."""
    HARD = "hard"      # Обязательная ссылка
    SOFT = "soft"      # Рекомендательная ссылка


@dataclass
class UID:
    """Универсальный идентификатор объекта."""
    namespace: str
    type: str
    local_id: str
    version: Optional[str] = None
    
    @classmethod
    def parse(cls, uid_str: str) -> 'UID':
        """Парсит строку UID вида: jvg://<namespace>/<type>/<local_id>[/<version>]"""
        pattern = r'^jvg://([^/]+)/([^/]+)/([^/]+)(?:/(.+))?$'
        match = re.match(pattern, uid_str)
        if not match:
            raise ValueError(f"Некорректный формат UID: {uid_str}")
        return cls(
            namespace=match.group(1),
            type=match.group(2),
            local_id=match.group(3),
            version=match.group(4)
        )
    
    def to_string(self) -> str:
        """Превращает UID в строку."""
        base = f"jvg://{self.namespace}/{self.type}/{self.local_id}"
        if self.version:
            return f"{base}/{self.version}"
        return base
    
    def without_version(self) -> 'UID':
        """Возвращает UID без версии."""
        return UID(self.namespace, self.type, self.local_id)
    
    def __str__(self):
        return self.to_string()
    
    def __hash__(self):
        return hash(self.to_string())
    
    def __eq__(self, other):
        if isinstance(other, UID):
            return self.to_string() == other.to_string()
        return False


@dataclass
class Reference:
    """Ссылка на другой объект."""
    target: UID
    ref_type: ReferenceType = ReferenceType.HARD
    description: Optional[str] = None
    
    def is_resolved(self, registry: 'IdentityRegistry') -> bool:
        """Проверяет, разрешена ли ссылка."""
        if self.ref_type == ReferenceType.SOFT:
            return True  # Мягкие ссылки всегда считаются разрешёнными
        return registry.has(self.target)


@dataclass
class VersionedObject:
    """Объект с версией."""
    uid: UID
    data: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    previous_version: Optional[UID] = None
    
    def to_jvg(self) -> Dict[str, Any]:
        """Экспортирует объект в JVG-структуру."""
        result = self.data.copy()
        if "vectorograph" in result:
            result["vectorograph"]["meta"]["id"] = self.uid.to_string()
            result["vectorograph"]["meta"]["version"] = self.uid.version or "1.0"
            result["vectorograph"]["meta"]["created_at"] = self.created_at
            result["vectorograph"]["meta"]["updated_at"] = self.updated_at
            if self.previous_version:
                result["vectorograph"]["meta"]["previous_version"] = self.previous_version.to_string()
        return result


class IdentityRegistry:
    """Реестр идентичности — хранит все объекты и ссылки."""
    
    def __init__(self):
        self.objects: Dict[str, VersionedObject] = {}  # uid_str -> VersionedObject
        self.references: Dict[str, List[Reference]] = {}  # uid_str -> [Reference]
        self.namespaces: Dict[str, Dict[str, Any]] = {}  # namespace -> metadata
    
    def register(self, obj: VersionedObject) -> str:
        """Регистрирует объект в реестре."""
        uid_str = obj.uid.to_string()
        self.objects[uid_str] = obj
        
        # Создаём запись для ссылок, если её нет
        if uid_str not in self.references:
            self.references[uid_str] = []
        
        # Обновляем пространство имён
        ns = obj.uid.namespace
        if ns not in self.namespaces:
            self.namespaces[ns] = {
                "created_at": datetime.now().isoformat(),
                "object_count": 0
            }
        self.namespaces[ns]["object_count"] += 1
        
        return uid_str
    
    def get(self, uid: UID) -> Optional[VersionedObject]:
        """Получает объект по UID."""
        return self.objects.get(uid.to_string())
    
    def has(self, uid: UID) -> bool:
        """Проверяет существование объекта."""
        return uid.to_string() in self.objects
    
    def add_reference(self, source: UID, target: UID, ref_type: ReferenceType = ReferenceType.HARD):
        """Добавляет ссылку между объектами."""
        source_str = source.to_string()
        if source_str not in self.references:
            self.references[source_str] = []
        self.references[source_str].append(Reference(target, ref_type))
    
    def get_references(self, uid: UID) -> List[Reference]:
        """Возвращает все ссылки объекта."""
        return self.references.get(uid.to_string(), [])
    
    def resolve_reference(self, ref: Reference) -> Optional[VersionedObject]:
        """Разрешает ссылку в объект."""
        if ref.ref_type == ReferenceType.SOFT:
            return self.get(ref.target)  # Может вернуть None — это нормально
        return self.get(ref.target)  # Жёсткая ссылка должна быть разрешена
    
    def get_latest_version(self, uid_without_version: UID) -> Optional[VersionedObject]:
        """Возвращает последнюю версию объекта."""
        # Ищем все версии
        versions = []
        for uid_str, obj in self.objects.items():
            uid = obj.uid
            if uid.namespace == uid_without_version.namespace and \
               uid.type == uid_without_version.type and \
               uid.local_id == uid_without_version.local_id:
                versions.append((uid.version or "0", obj))
        
        if not versions:
            return None
        
        # Сортируем по версии (простое сравнение строк — для semver нужен парсер)
        versions.sort(key=lambda x: x[0])
        return versions[-1][1]
    
    def to_dict(self) -> Dict[str, Any]:
        """Экспортирует реестр в словарь."""
        return {
            "objects": {k: v.to_jvg() for k, v in self.objects.items()},
            "references": {k: [{"target": r.target.to_string(), "type": r.ref_type.value} 
                              for r in v] for k, v in self.references.items()},
            "namespaces": self.namespaces
        }


# ============================================================
# Вспомогательные функции
# ============================================================

def generate_uid(namespace: str, type: str, local_id: str, version: Optional[str] = None) -> UID:
    """Генерирует UID."""
    return UID(namespace, type, local_id, version)


def generate_local_id(name: str, context: str = "") -> str:
    """Генерирует локальный ID из имени."""
    base = name.lower().replace(" ", "_").replace("-", "_")
    # Убираем недопустимые символы
    base = re.sub(r'[^a-zA-Z0-9_\-.]', '_', base)
    if context:
        hash_suffix = hashlib.md5(context.encode()).hexdigest()[:6]
        return f"{base}_{hash_suffix}"
    return base


# ============================================================
# Тест
# ============================================================

def test_identity():
    print("=== Тест Identity ===")
    
    # 1. Создаём UID
    uid1 = generate_uid("slc", "system", "optimizer", "1.0")
    print(f"UID: {uid1}")
    
    # 2. Парсим UID
    parsed = UID.parse(str(uid1))
    print(f"Парсинг: {parsed.namespace}/{parsed.type}/{parsed.local_id} v{parsed.version}")
    
    # 3. Создаём объект
    obj = VersionedObject(
        uid=uid1,
        data={"name": "Route Optimizer", "type": "система"}
    )
    
    # 4. Регистрируем
    registry = IdentityRegistry()
    registry.register(obj)
    print(f"Зарегистрирован: {uid1}")
    
    # 5. Добавляем ссылку
    uid2 = generate_uid("core", "entity", "route-database", "2.0")
    registry.add_reference(uid1, uid2)
    print(f"Ссылка: {uid1} → {uid2}")
    
    # 6. Проверяем наличие
    print(f"Существует: {registry.has(uid1)}")
    print(f"Существует: {registry.has(uid2)}")
    
    # 7. Экспортируем реестр
    print("\nРеестр:", json.dumps(registry.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_identity()
