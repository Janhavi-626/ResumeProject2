from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.database import initialize_db

initialize_db()

app = FastAPI(title="Retail Return Eligibility Agent", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    initialize_db()


app.include_router(router)


@app.get("/")
def root() -> dict:
    return {"message": "Retail Return Eligibility Agent is running."}
