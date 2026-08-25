from __future__ import annotations

import json
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class CaseRepository:
    """Small SQLite repository for case summaries and append-only audit events."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._setup()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def _setup(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    autonomy_profile TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    pending_gate_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    actor_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    FOREIGN KEY(case_id) REFERENCES cases(case_id)
                );
                """
            )

    @staticmethod
    def _dump(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, default=str)

    @staticmethod
    def _load(value: str | None, default: Any) -> Any:
        return json.loads(value) if value else default

    def create(self, state: dict[str, Any]) -> None:
        now = utc_now()
        questionnaire = state.get("questionnaire", {})
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO cases (
                    case_id, title, status, autonomy_profile, state_json,
                    pending_gate_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, NULL, ?, ?)
                """,
                (
                    state["case_id"],
                    questionnaire.get("use_case_name", state["case_id"]),
                    state.get("status", "DRAFT"),
                    state.get("autonomy_profile", "human_governed"),
                    self._dump(state),
                    now,
                    now,
                ),
            )

    def save(self, case_id: str, state: dict[str, Any], pending_gate: dict | None) -> None:
        now = utc_now()
        questionnaire = state.get("questionnaire", {})
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                UPDATE cases
                   SET title = ?, status = ?, autonomy_profile = ?, state_json = ?,
                       pending_gate_json = ?, updated_at = ?
                 WHERE case_id = ?
                """,
                (
                    questionnaire.get("use_case_name", case_id),
                    state.get("status", "UNKNOWN"),
                    state.get("autonomy_profile", "human_governed"),
                    self._dump(state),
                    self._dump(pending_gate) if pending_gate else None,
                    now,
                    case_id,
                ),
            )

    def get(self, case_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,)).fetchone()
        if not row:
            return None
        state = self._load(row["state_json"], {})
        return {
            "case_id": row["case_id"],
            "title": row["title"],
            "status": row["status"],
            "autonomy_profile": row["autonomy_profile"],
            "state": state,
            "pending_gate": self._load(row["pending_gate_json"], None),
            "pending_event": state.get("active_external_event"),
            "lifecycle_status": state.get("lifecycle_status"),
            "domain_phase": state.get("domain_phase"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def list(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT case_id, title, status, autonomy_profile, state_json, pending_gate_json,
                       created_at, updated_at
                  FROM cases
                 ORDER BY updated_at DESC
                """
            ).fetchall()
        results = []
        for row in rows:
            state = self._load(row["state_json"], {})
            results.append(
                {
                    "case_id": row["case_id"],
                    "title": row["title"],
                    "status": row["status"],
                    "autonomy_profile": row["autonomy_profile"],
                    "pending_gate": self._load(row["pending_gate_json"], None),
                    "pending_event": state.get("active_external_event"),
                    "lifecycle_status": state.get("lifecycle_status"),
                    "domain_phase": state.get("domain_phase"),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            )
        return results

    def add_audit(
        self,
        case_id: str,
        actor_type: str,
        actor: str,
        action: str,
        details: dict[str, Any],
    ) -> None:
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO audit_events (
                    case_id, occurred_at, actor_type, actor, action, details_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (case_id, utc_now(), actor_type, actor, action, self._dump(details)),
            )

    def audit(self, case_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT event_id, occurred_at, actor_type, actor, action, details_json
                  FROM audit_events
                 WHERE case_id = ?
                 ORDER BY event_id
                """,
                (case_id,),
            ).fetchall()
        return [
            {
                "event_id": row["event_id"],
                "occurred_at": row["occurred_at"],
                "actor_type": row["actor_type"],
                "actor": row["actor"],
                "action": row["action"],
                "details": self._load(row["details_json"], {}),
            }
            for row in rows
        ]
