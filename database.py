import sqlite3


def create_transaction_table(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL
        )
        """)
