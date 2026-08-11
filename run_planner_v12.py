"""
run_planner_v12.py — Запуск Experience-Based Planner
"""

from jvg import PlannerV12, JVGStore
from jvg.models.fake_world_model import FakeWorldModel
import pprint

def main():
    store = JVGStore()
    doc_id = "GitAgent_20260711_114248_5bed76d1"

    jvg = store.get(doc_id)
    if not jvg:
        print(f"❌ Документ {doc_id} не найден")
        return

    print(f"✅ Документ найден: {doc_id}")

    # Создаём модель мира (пока фейковую)
    model = FakeWorldModel({
        'has_modifications': True,
        'has_untracked': False,
        'has_staged': False,
        'is_ahead': False,
        'is_behind': False,
        'is_clean': False
    })

    planner = PlannerV12(store, model)
    
    planner.set_goal({
        "is_clean": True,
        "is_ahead": False,
        "is_behind": False
    })
    planner.max_iterations = 10

    result = planner.run(doc_id)

    print(f"\n📊 Результат:")
    print(f"  Статус: {result['status']}")
    print(f"  Итераций: {result.get('iterations', 0)}")
    if result.get('final_state'):
        print(f"  Финальное состояние:")
        pprint.pprint(result['final_state'])

    print(f"\n📚 Опыт планировщика:")
    for i, episode in enumerate(planner.experience, 1):
        print(f"  {i}. Действие: {episode.get('action', {}).get('name', 'unknown')}")
        print(f"     Результат: {'✅' if episode.get('score', 0) > 0 else '❌'}")

if __name__ == "__main__":
    main()
