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


def insert_transaction(
    connection,
    transaction_type,
    amount,
    description,
    date,
):
    cursor = connection.execute(
        """
        INSERT INTO transactions (
            type,
            amount,
            description,
            date
        )
        VALUES (?,?,?,?)
        """,
        (
            transaction_type,
            amount,
            description,
            date,
        ),
    )

    connection.commit()
    return cursor.lastrowid
