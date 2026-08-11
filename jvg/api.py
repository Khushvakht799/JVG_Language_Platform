"""
jvg/api.py — REST API для JVG Runtime
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from jvg.runtime.runtime import JVGRuntime

app = FastAPI(title="JVG Platform API", version="0.1.0")
runtime = JVGRuntime(storage_dir="jvg_store")

class StepRequest(BaseModel):
    doc_id: str
    new_state: Optional[str] = None
    action_result: Optional[str] = None

class StepResponse(BaseModel):
    status: str
    result: Dict[str, Any]

@app.get("/")
def root():
    return {"message": "JVG Platform API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/step", response_model=StepResponse)
def step(request: StepRequest):
    result = runtime.step(request.doc_id, request.new_state, request.action_result)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("error"))
    return StepResponse(status="success", result=result)

@app.get("/doc/{doc_id}")
def get_doc(doc_id: str):
    from jvg.store import JVGStore
    store = JVGStore(storage_dir="jvg_store")
    doc = store.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return doc
