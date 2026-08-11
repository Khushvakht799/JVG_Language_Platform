import datetime
import json
from pathlib import Path


def log(message):
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    print(f"[{timestamp}] {message}")


def execute_handover(jvg_path):
    jvg_path = Path(jvg_path)

    with jvg_path.open(encoding="utf-8") as file:
        scenario = json.load(file)

    log("Начинаем передачу смены")

    for step in scenario.get("steps", []):
        action = step.get("action")
        params = step.get("params", {})
        log(f"{step.get('id')}: {action} | {params}")

    report = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "scenario": scenario.get("scenario"),
        "status": "HANDOVER_COMPLETE",
        "steps_executed": len(scenario.get("steps", [])),
        "result": "success"
    }

    report_path = jvg_path.parent / "handover_report.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    log("Передача смены завершена")
    log(f"Отчёт сохранён: {report_path.name}")

    return report


if __name__ == "__main__":
    execute_handover(Path(__file__).parent / "handover.jvg")
