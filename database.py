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


def get_transactions(connection):
    return connection.execute("""
        SELECT
            id, type, amount, description, date
        FROM
            transactions
        ORDER BY
            id DESC""").fetchall()


def update_transaction_field(
    connection,
    transaction_id,
    field,
    new_value,
):
    allowed_fields = {
        "type",
        "amount",
        "description",
        "date",
    }

    if field not in allowed_fields:
        return False

    cursor = connection.execute(
        f"""
        UPDATE transactions
        SET {field} = ?
        WHERE id = ?
        """,
        (
            new_value,
            transaction_id,
        ),
    )

    connection.commit()
    return cursor.rowcount > 0


def delete_transaction_by_id(connection, transaction_id):
    cursor = connection.execute(
        """
        DELETE FROM transactions
        WHERE id = ?
        """,
        (transaction_id,),
    )

    connection.commit()
    return cursor.rowcount > 0
