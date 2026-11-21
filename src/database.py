import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import DATABASE_PATH


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with closing(connect()) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                sources_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id, id);
            """
        )
        connection.commit()


def list_conversations() -> list[dict[str, Any]]:
    with closing(connect()) as connection:
        rows = connection.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def create_conversation(title: str = "New conversation") -> int:
    now = utc_now()
    with closing(connect()) as connection:
        cursor = connection.execute(
            """
            INSERT INTO conversations (title, created_at, updated_at)
            VALUES (?, ?, ?)
            """,
            (title, now, now),
        )
        connection.commit()
        return int(cursor.lastrowid)


def delete_conversation(conversation_id: int) -> None:
    with closing(connect()) as connection:
        connection.execute(
            "DELETE FROM messages WHERE conversation_id = ?",
            (conversation_id,),
        )
        connection.execute(
            "DELETE FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        connection.commit()


def get_messages(conversation_id: int) -> list[dict[str, Any]]:
    with closing(connect()) as connection:
        rows = connection.execute(
            """
            SELECT id, role, content, sources_json, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()

    messages = []
    for row in rows:
        item = dict(row)
        item["sources"] = json.loads(item.pop("sources_json") or "[]")
        messages.append(item)
    return messages


def add_message(
    conversation_id: int,
    role: str,
    content: str,
    sources: list[dict[str, Any]] | None = None,
) -> int:
    now = utc_now()
    with closing(connect()) as connection:
        cursor = connection.execute(
            """
            INSERT INTO messages
                (conversation_id, role, content, sources_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                role,
                content,
                json.dumps(sources or [], ensure_ascii=False),
                now,
            ),
        )
        connection.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (now, conversation_id),
        )
        connection.commit()
        return int(cursor.lastrowid)


def update_conversation_title(conversation_id: int, title: str) -> None:
    with closing(connect()) as connection:
        connection.execute(
            """
            UPDATE conversations
            SET title = ?, updated_at = ?
            WHERE id = ?
            """,
            (title, utc_now(), conversation_id),
        )
        connection.commit()
