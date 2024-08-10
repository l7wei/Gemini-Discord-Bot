import sqlite3
from datetime import datetime


class ChatHistory:
    def __init__(self, channel_id, db_name="chat_history.db"):
        self.channel_id = channel_id
        self.table_name = f"channel_{self.channel_id}"
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """
        )
        self.cursor.execute(
            f"CREATE INDEX IF NOT EXISTS idx_user_id_{self.channel_id} ON {self.table_name} (user_id)"
        )
        self.conn.commit()

    def insert_message(self, user_id, message, role):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            f"""
            INSERT INTO {self.table_name} (user_id, message, timestamp, role)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, message, timestamp, role),
        )
        self.conn.commit()

    def insert_user_reply(self, user_id, message):
        self.insert_message(user_id, message, role="user")

    def insert_bot_reply(self, user_id, message):
        self.insert_message(user_id, message, role="model")

    def get_history(self):
        self.cursor.execute(f"SELECT * FROM {self.table_name}")
        return self.cursor.fetchall()

    def reset_history(self):
        self.cursor.execute(f"DELETE FROM {self.table_name}")
        self.conn.commit()

    def get_history_gemini_format(self):
        history = self.get_history()
        formatted_history = []
        for record in history:
            id, user_id, message, timestamp, role = record
            formatted_history.append({"role": role, "parts": [message]})
        return formatted_history

    def close(self):
        self.conn.close()
