import json
import os
import sqlite3

DB_PATH = os.getenv("AUDIT_DB_PATH", "screening_audit.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS screenings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_id TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            input_data TEXT NOT NULL,
            result_data TEXT NOT NULL,
            agent_states TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            screening_id INTEGER NOT NULL,
            correct INTEGER NOT NULL,
            override_recommendation TEXT,
            comment TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (screening_id) REFERENCES screenings(id)
        )
    """)
    conn.commit()
    conn.close()


def log_screening(applicant_id: str, input_data: dict, result_data: dict, agent_states: dict | None = None) -> int:
    conn = _get_conn()
    cursor = conn.execute(
        "INSERT INTO screenings (applicant_id, input_data, result_data, agent_states) VALUES (?, ?, ?, ?)",
        (
            applicant_id,
            json.dumps(input_data, default=str),
            json.dumps(result_data, default=str),
            json.dumps(agent_states, default=str) if agent_states else None,
        ),
    )
    screening_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return screening_id


def save_feedback(screening_id: int, correct: bool, override_recommendation: str | None = None, comment: str | None = None):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO feedback (screening_id, correct, override_recommendation, comment) VALUES (?, ?, ?, ?)",
        (screening_id, 1 if correct else 0, override_recommendation, comment),
    )
    conn.commit()
    conn.close()


def get_screenings(applicant_id: str) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        """SELECT s.*, f.correct, f.override_recommendation, f.comment as feedback_comment
           FROM screenings s
           LEFT JOIN feedback f ON f.id = (
               SELECT MAX(f2.id) FROM feedback f2 WHERE f2.screening_id = s.id
           )
           WHERE s.applicant_id = ? ORDER BY s.created_at DESC""",
        (applicant_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_screenings(limit: int = 50, offset: int = 0) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        """SELECT s.*, f.correct, f.override_recommendation, f.comment as feedback_comment
           FROM screenings s
           LEFT JOIN feedback f ON f.id = (
               SELECT MAX(f2.id) FROM feedback f2 WHERE f2.screening_id = s.id
           )
           ORDER BY s.created_at DESC LIMIT ? OFFSET ?""",
        (limit, offset),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _count_outcomes(conn) -> tuple[int, dict, dict]:
    total = conn.execute("SELECT COUNT(*) FROM screenings").fetchone()[0]
    rows = conn.execute("SELECT result_data FROM screenings").fetchall()
    outcomes = {"Proceed": 0, "Need More Info": 0, "Reject / Not Eligible": 0, "High Risk Review": 0}
    flag_counts: dict[str, int] = {}
    for r in rows:
        try:
            rd = json.loads(r["result_data"])
            rec = rd.get("recommendation", "Unknown")
            if rec in outcomes:
                outcomes[rec] += 1
            for flag in rd.get("risk_flags", []):
                flag_counts[flag] = flag_counts.get(flag, 0) + 1
        except (json.JSONDecodeError, KeyError):
            pass
    return total, outcomes, flag_counts


def _count_feedback(conn) -> tuple[int, list, int]:
    fb_total = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
    agreed = conn.execute("SELECT COUNT(*) FROM feedback WHERE correct = 1").fetchone()[0]
    agreement = round(agreed / fb_total * 100) if fb_total > 0 else 0

    top_override_rows = conn.execute(
        "SELECT override_recommendation, COUNT(*) as cnt FROM feedback WHERE correct = 0 GROUP BY override_recommendation ORDER BY cnt DESC LIMIT 3"
    ).fetchall()
    top_overrides = [{"outcome": r["override_recommendation"], "count": r["cnt"]} for r in top_override_rows]

    return agreement, top_overrides, fb_total - agreed


def _recent_overrides(conn) -> list:
    rows = conn.execute(
        """SELECT s.applicant_id, f.override_recommendation, f.comment, f.created_at,
                  json_extract(s.result_data, '$.recommendation') as ai_rec
           FROM feedback f
           JOIN screenings s ON s.id = f.screening_id
           WHERE f.correct = 0
           ORDER BY f.created_at DESC LIMIT 5"""
    ).fetchall()
    return [
        {
            "applicant_id": r["applicant_id"],
            "ai_rec": r["ai_rec"],
            "override": r["override_recommendation"],
            "comment": r["comment"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]


def get_summary() -> dict:
    conn = _get_conn()

    total, outcomes, flag_counts = _count_outcomes(conn)
    agreement, top_overrides, overrides_count = _count_feedback(conn)
    recent_overrides = _recent_overrides(conn)

    conn.close()
    return {
        "total": total,
        "by_outcome": outcomes,
        "agreement_pct": agreement,
        "top_overrides": top_overrides,
        "top_risk_flags": sorted(flag_counts.items(), key=lambda x: -x[1])[:5],
        "overrides_count": overrides_count,
        "recent_overrides": recent_overrides,
    }
