from datetime import datetime, timezone
from threading import Lock

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent import creer_agent
from init_db import initialiser_base


class AgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)


class AgentQueryResponse(BaseModel):
    status: str
    query: str
    response: str
    timestamp: str


app = FastAPI(title="Portfolio Analytics Agent API", version="1.0.0")

_agent_lock = Lock()
_agent = None


def get_agent():
    global _agent
    if _agent is not None:
        return _agent
    with _agent_lock:
        if _agent is None:
            load_dotenv()
            initialiser_base()
            _agent = creer_agent()
    return _agent


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/agent/query", response_model=AgentQueryResponse)
def query_agent(payload: AgentQueryRequest):
    question = payload.query.strip()
    if not question:
        raise HTTPException(status_code=400, detail="La requête ne peut pas être vide")
    try:
        result = get_agent().invoke({"input": question})
        output = str(result.get("output", ""))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur agent: {exc}")
    return AgentQueryResponse(
        status="success",
        query=question,
        response=output,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
