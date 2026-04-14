import json
import sqlite3
from pathlib import Path


class PlanDatabase:
    def __init__(self, database_path: str) -> None:
        self.database_path = Path(database_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS saved_plans (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    zip_code TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    result_json TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def save_plan(self, plan_id: str, created_at: str, zip_code: str, payload: dict, result: dict) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO saved_plans (id, created_at, zip_code, payload_json, result_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    plan_id,
                    created_at,
                    zip_code,
                    json.dumps(payload),
                    json.dumps(result),
                ),
            )
            connection.commit()

    def get_plan(self, plan_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, payload_json, result_json FROM saved_plans WHERE id = ?",
                (plan_id,),
            ).fetchone()

        if row is None:
            return None

        return {
            "plan_id": row["id"],
            "input": json.loads(row["payload_json"]),
            "analysis": json.loads(row["result_json"]),
        }
