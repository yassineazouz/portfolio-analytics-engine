from datetime import datetime, timezone
from threading import Lock

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent import creer_agent
from init_db import initialiser_base


class AgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Question en langage naturel")


class AgentQueryResponse(BaseModel):
    status: str
    query: str
    response: str
    timestamp: str


app = FastAPI(
    title="Portfolio Analytics Agent API",
    version="1.0.0",
    description="API REST pour interroger l'agent financier en langage naturel.",
)

_agent_lock = Lock()
_agent_instance = None


def _ensure_agent():
    global _agent_instance
    if _agent_instance is not None:
        return _agent_instance

    with _agent_lock:
        if _agent_instance is None:
            load_dotenv()
            initialiser_base()
            _agent_instance = creer_agent()

    return _agent_instance


def _invoke_agent(query: str) -> str:
    agent = _ensure_agent()
    result = agent.invoke({"input": query})
    return str(result.get("output", ""))


@app.get("/health")
def healthcheck() -> dict:
    return {
        "status": "ok",
        "service": "portfolio-analytics-agent-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/agent/query", response_model=AgentQueryResponse)
def query_agent(payload: AgentQueryRequest) -> AgentQueryResponse:
    question = payload.query.strip()
    if not question:
        raise HTTPException(status_code=400, detail="La requête ne peut pas être vide")

    try:
        output = _invoke_agent(question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur agent: {exc}") from exc

    return AgentQueryResponse(
        status="success",
        query=question,
        response=output,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
