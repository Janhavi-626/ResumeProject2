from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "return_demo.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS return_requests (
                id TEXT PRIMARY KEY,
                customer_id TEXT,
                order_id TEXT,
                product_id TEXT,
                status TEXT,
                classification TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS workflow_traces (
                workflow_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                status TEXT NOT NULL,
                user_query TEXT NOT NULL,
                trace_json TEXT NOT NULL,
                human_approval TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS business_actions (
                id TEXT PRIMARY KEY,
                workflow_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                status TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def save_workflow_trace(workflow_id: str, session_id: str, state: dict[str, Any]) -> None:
    status = state.get("workflow_status", "RUNNING")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO workflow_traces (workflow_id, session_id, status, user_query, trace_json, human_approval, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(workflow_id) DO UPDATE SET
                session_id = excluded.session_id,
                status = excluded.status,
                user_query = excluded.user_query,
                trace_json = excluded.trace_json,
                human_approval = excluded.human_approval,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                workflow_id,
                session_id,
                status,
                state.get("user_query", ""),
                json.dumps(state, default=str),
                state.get("human_approval"),
            ),
        )


def get_workflow_trace(workflow_id: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM workflow_traces WHERE workflow_id = ?",
            (workflow_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "workflow_id": row["workflow_id"],
        "session_id": row["session_id"],
        "status": row["status"],
        "user_query": row["user_query"],
        "trace": json.loads(row["trace_json"]),
        "human_approval": row["human_approval"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def record_business_action(workflow_id: str, action_type: str, payload: dict[str, Any]) -> str:
    action_id = f"{action_type.upper()}-{workflow_id}-{len(payload)}"
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO business_actions (id, workflow_id, action_type, status, payload_json, created_at) VALUES (?, ?, ?, 'created', ?, CURRENT_TIMESTAMP)",
            (action_id, workflow_id, action_type, json.dumps(payload)),
        )
    return action_id


def approve_workflow_trace(workflow_id: str, action: str, notes: str | None = None) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE workflow_traces SET human_approval = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE workflow_id = ?",
            (action, "RESOLVED" if action == "approve" else "REJECTED", workflow_id),
        )
