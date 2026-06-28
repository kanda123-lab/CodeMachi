import sqlite3
from datetime import date

DB_PATH = "codemachi.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                mode TEXT NOT NULL DEFAULT 'tanglish',
                daily_count INTEGER NOT NULL DEFAULT 0,
                last_reset_date TEXT,
                is_pro INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (date('now'))
            )
        """)
        conn.commit()


def get_user(telegram_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return dict(row) if row else None


def upsert_user(telegram_id: int, mode: str = "tanglish"):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO users (telegram_id, mode, created_at)
            VALUES (?, ?, date('now'))
            ON CONFLICT(telegram_id) DO NOTHING
        """, (telegram_id, mode))
        conn.commit()


def set_mode(telegram_id: int, mode: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET mode = ? WHERE telegram_id = ?", (mode, telegram_id)
        )
        conn.commit()


def get_mode(telegram_id: int) -> str:
    user = get_user(telegram_id)
    return user["mode"] if user else "tanglish"


def check_and_increment_usage(telegram_id: int) -> dict:
    """
    Returns {"allowed": bool, "count": int, "is_pro": bool}.
    Resets daily_count if last_reset_date is not today (IST midnight boundary).
    Increments count only when allowed.
    """
    today = str(date.today())
    FREE_LIMIT = 5

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()

        if not row:
            # TODO: shouldn't happen if upsert_user is called on /start, but guard anyway
            return {"allowed": True, "count": 0, "is_pro": False}

        user = dict(row)

        if user["is_pro"]:
            conn.execute(
                "UPDATE users SET daily_count = daily_count + 1, last_reset_date = ? WHERE telegram_id = ?",
                (today, telegram_id)
            )
            conn.commit()
            return {"allowed": True, "count": user["daily_count"] + 1, "is_pro": True}

        if user["last_reset_date"] != today:
            conn.execute(
                "UPDATE users SET daily_count = 0, last_reset_date = ? WHERE telegram_id = ?",
                (today, telegram_id)
            )
            conn.commit()
            user["daily_count"] = 0

        if user["daily_count"] >= FREE_LIMIT:
            return {"allowed": False, "count": user["daily_count"], "is_pro": False}

        conn.execute(
            "UPDATE users SET daily_count = daily_count + 1 WHERE telegram_id = ?",
            (telegram_id,)
        )
        conn.commit()
        return {"allowed": True, "count": user["daily_count"] + 1, "is_pro": False}


def get_usage(telegram_id: int) -> dict:
    today = str(date.today())
    FREE_LIMIT = 5

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()

        if not row:
            return {"count": 0, "remaining": FREE_LIMIT, "is_pro": False}

        user = dict(row)

        if user["is_pro"]:
            return {"count": user["daily_count"], "remaining": -1, "is_pro": True}

        count = user["daily_count"] if user["last_reset_date"] == today else 0
        return {
            "count": count,
            "remaining": max(0, FREE_LIMIT - count),
            "is_pro": False,
        }