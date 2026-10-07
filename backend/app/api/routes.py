from __future__ import annotations

import time
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.agents.triage import TriageAgent
from app.database import approve_workflow_trace, get_workflow_trace, record_business_action, save_workflow_trace
from app.graph.workflow import ReturnWorkflow
from app.models.schemas import ApprovalRequest, ChatRequest, ReturnClassificationRequest
from app.rag.retriever import KnowledgeRetriever
from app.services.classification_service import classification_service
from app.services.memory_service import memory_service

router = APIRouter(prefix="/api")


@router.get("/health")
def health_check() -> Dict[str, Any]:
    return {"status": "ok", "service": "return-agent"}


@router.get("/metrics")
def metrics() -> Dict[str, Any]:
    return {"requests": 1, "status": "ok", "latency_ms": 120}


@router.post("/chat")
def chat(request: ChatRequest) -> Dict[str, Any]:
    session_id = request.session_id or "session-demo"
    memory_service.add_message(session_id, "user", request.user_message)
    triage = TriageAgent().run(request.user_message)
    wf = ReturnWorkflow()
    workflow = wf.run(request.user_message, session_id=session_id)
    memory_service.save_workflow_state(workflow["workflow_id"], workflow)
    return {"session_id": session_id, "triage": triage.model_dump(), "workflow": workflow}


@router.post("/agent/run")
def run_agent(request: ChatRequest) -> Dict[str, Any]:
    start = time.time()
    workflow = ReturnWorkflow().run(request.user_message, session_id=request.session_id or "session-agent")
    memory_service.save_workflow_state(workflow["workflow_id"], workflow)
    save_workflow_trace(workflow["workflow_id"], workflow["session_id"], workflow)
    return {"workflow": workflow, "latency_ms": round((time.time() - start) * 1000, 2)}


@router.post("/returns/classify")
def classify_return(request: ReturnClassificationRequest) -> Dict[str, Any]:
    result = classification_service.classify(request.model_dump())
    return {"result": result}


@router.post("/returns/investigate")
def investigate_return(request: ReturnClassificationRequest) -> Dict[str, Any]:
    result = classification_service.classify(request.model_dump())
    return {"status": "investigated", "classification": result}


@router.post("/documents/upload")
def upload_document() -> Dict[str, Any]:
    return {"status": "uploaded", "document_id": "doc-101"}


@router.post("/documents/ingest")
def ingest_documents() -> Dict[str, Any]:
    from pathlib import Path

    knowledge_root = Path(__file__).resolve().parents[2] / "knowledge_base"
    retriever = KnowledgeRetriever(str(knowledge_root), persist_directory="backend/.chroma")
    documents = retriever.ingest()
    return {"status": "ingested", "documents": documents, "indexed": True}


@router.get("/sessions/{session_id}")
def get_session(session_id: str) -> Dict[str, Any]:
    return {"session_id": session_id, "history": memory_service.get_session_history(session_id)}


@router.get("/workflows/{workflow_id}")
def get_workflow(workflow_id: str) -> Dict[str, Any]:
    state = memory_service.get_workflow_state(workflow_id)
    if not state:
        return {"workflow_id": workflow_id, "status": "not_found"}
    trace = get_workflow_trace(workflow_id)
    return {"workflow_id": workflow_id, "state": state, "trace": trace}


@router.post("/approval/{workflow_id}")
def approval(workflow_id: str, request: ApprovalRequest) -> Dict[str, Any]:
    if request.action not in {"approve", "reject"}:
        raise HTTPException(status_code=400, detail="Only approve or reject are supported")
    state = memory_service.get_workflow_state(workflow_id)
    if not state:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if state.get("workflow_status") != "PENDING_HUMAN_REVIEW":
        raise HTTPException(status_code=409, detail="Workflow is not awaiting human approval")

    resumed = ReturnWorkflow().resume_approval(state, request.action)
    state.update(resumed)
    state["human_approval"] = request.action
    state["approval_notes"] = request.notes
    memory_service.save_workflow_state(workflow_id, state)
    save_workflow_trace(workflow_id, state["session_id"], state)
    approve_workflow_trace(workflow_id, request.action, request.notes)
    return {
        "workflow_id": workflow_id,
        "approval": request.action,
        "status": state.get("workflow_status"),
        "final_response": state.get("final_response"),
    }
