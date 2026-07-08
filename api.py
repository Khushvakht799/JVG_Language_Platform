"""
api.py — REST API для JVG (с единым конфигом)
"""

import os
import sys
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'document'))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'validator'))
sys.path.append(os.path.join(BASE_DIR, '01_toolchain', 'storage'))
sys.path.append(os.path.join(BASE_DIR, '02_search', 'vectorizer'))
sys.path.append(os.path.join(BASE_DIR, '02_search', 'ranking'))
sys.path.append(os.path.join(BASE_DIR, '03_runtime'))

from compiler import JVGCompiler
from validator_pipeline import JVGValidatorPipeline
from store import JVGStore
from vectorizer import JVGVectorizer
from ranking import JVGRankingEngine
from l1_adapter import L1Adapter
from l2_memory import L2Memory
from l3_models import L3Models
from l4_execution import L4Execution
from l5_audit import L5Audit

class CompileRequest(BaseModel):
    text: str

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class EventRequest(BaseModel):
    title: str
    entity: str
    source: str
    purpose: str
    actions: List[str] = []

class StepRequest(BaseModel):
    doc_id: str
    new_state: Optional[str] = None
    action_result: Optional[str] = None

app = FastAPI(title="JVG API", description="API для работы с JVG")

# Инициализация с едиными путями
compiler = JVGCompiler()
validator = JVGValidatorPipeline()
store = JVGStore()
vectorizer = JVGVectorizer()
ranking = JVGRankingEngine()
l1 = L1Adapter()
l2 = L2Memory()
l3 = L3Models(l2)
l4 = L4Execution()
l5 = L5Audit()

@app.get("/")
def root():
    return {"status": "ok", "message": "JVG API работает"}

@app.post("/compile")
def compile_text(request: CompileRequest):
    result = compiler.compile(request.text)
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result.get("errors", "Ошибка компиляции"))
    return result

@app.post("/validate")
def validate_jvg(data: Dict[str, Any]):
    valid, errors = validator.validate(data)
    return {"valid": valid, "errors": errors, "errors_count": len(errors)}

@app.post("/store")
def save_jvg(data: Dict[str, Any]):
    doc_id = store.save(data)
    return {"doc_id": doc_id}

@app.get("/store/{doc_id}")
def get_jvg(doc_id: str):
    jvg = store.get(doc_id)
    if not jvg:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return jvg

@app.post("/search")
def search_jvg(request: SearchRequest):
    results = ranking.search(request.query, top_k=request.top_k)
    return {"query": request.query, "results": results}

@app.post("/event")
def process_event(request: EventRequest):
    event = request.dict()
    jvg = l1.event_to_jvg(event)
    doc_id = l2.save(jvg)
    analysis = l3.analyze_state(doc_id)
    return {"doc_id": doc_id, "analysis": analysis}

@app.post("/step")
def execute_step(request: StepRequest):
    result = l4.step(request.doc_id, request.new_state, request.action_result)
    return result

@app.get("/explain/{doc_id}")
def explain(doc_id: str):
    jvg = store.get(doc_id)
    if not jvg:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return {"explanation": l5.explain(doc_id, jvg)}

@app.get("/search/{query}")
def search_get(query: str, top_k: int = 5):
    results = ranking.search(query, top_k=top_k)
    return {"query": query, "results": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
