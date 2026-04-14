from __future__ import annotations

import os
import secrets
import time
from collections import defaultdict
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.calculator import analyze_budget
from app.database import PlanDatabase
from app.schemas import BudgetRequest, LoadedPlanResponse, SavedPlanResponse

load_dotenv()

DATABASE_PATH = os.getenv("DATABASE_PATH", "bridgebudget.db")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://127.0.0.1:5500").rstrip("/")
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "20"))
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000",
    ).split(",")
    if origin.strip()
]

db = PlanDatabase(DATABASE_PATH)
rate_limit_store: dict[str, list[float]] = defaultdict(list)

app = FastAPI(
    title="BridgeBudget API",
    description="Budget triage and recovery-plan API for households under financial pressure.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def enforce_rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "anonymous"
    now = time.time()
    requests = rate_limit_store[client_ip]
    valid_after = now - RATE_LIMIT_WINDOW_SECONDS
    rate_limit_store[client_ip] = [timestamp for timestamp in requests if timestamp > valid_after]

    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute and try again.")

    rate_limit_store[client_ip].append(now)


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok", "service": "bridgebudget-api"}


@app.post("/api/analyze")
def analyze(payload: BudgetRequest, request: Request) -> dict:
    enforce_rate_limit(request)
    return analyze_budget(payload.model_dump())


@app.post("/api/plans", response_model=SavedPlanResponse)
def save_plan(payload: BudgetRequest, request: Request) -> SavedPlanResponse:
    enforce_rate_limit(request)
    parsed_payload = payload.model_dump()
    analysis = analyze_budget(parsed_payload)
    plan_id = secrets.token_urlsafe(8).replace("-", "").replace("_", "")
    created_at = datetime.now(timezone.utc).isoformat()
    db.save_plan(
        plan_id=plan_id,
        created_at=created_at,
        zip_code=parsed_payload["location_zip"],
        payload=parsed_payload,
        result=analysis,
    )
    share_url = f"{FRONTEND_BASE_URL}/?plan={plan_id}"
    return SavedPlanResponse(plan_id=plan_id, share_url=share_url, analysis=analysis)


@app.get("/api/plans/{plan_id}", response_model=LoadedPlanResponse)
def get_plan(plan_id: str) -> LoadedPlanResponse:
    stored = db.get_plan(plan_id)
    if stored is None:
        raise HTTPException(status_code=404, detail="This saved plan could not be found.")
    return LoadedPlanResponse(**stored)
