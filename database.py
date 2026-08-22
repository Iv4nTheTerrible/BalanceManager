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


def create_account_table(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            balance INTEGER NOT NULL
        )
        """)


def connect_database(database_path="balance_manager.db"):
    connection = sqlite3.connect(database_path)
    create_transaction_table(connection)
    create_account_table(connection)
    return connection


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


def get_transaction_by_id(connection, transaction_id):
    return connection.execute(
        """
        SELECT id, type, amount, description, date
        FROM transactions
        WHERE id = ?
        """,
        (transaction_id,),
    ).fetchone()


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


def insert_account(connection, name, balance):
    cursor = connection.execute(
        """
        INSERT INTO accounts (
        name,
        balance
        )
        VALUES (?,?)
        """,
        (
            name,
            balance,
        ),
    )

    connection.commit()
    return cursor.rowcount > 0


def get_accounts(connection):
    return connection.execute("""
        SELECT id , name, balance
        FROM accounts
        ORDER BY id DESC
        """).fetchall()


def get_account_by_id(connection, account_id):
    return connection.execute(
        """
        SELECT id, name, balance
        FROM accounts
        WHERE id = ?
        """,
        (account_id,),
    ).fetchone()


def update_account_field(
    connection,
    account_id,
    field,
    new_value,
):
    allowed_fields = {
        "name",
        "balance",
    }

    if field not in allowed_fields:
        return False

    cursor = connection.execute(
        f"""
        UPDATE accounts
        SET {field} = ?
        WHERE id = ?
        """,
        (
            new_value,
            account_id,
        ),
    )

    connection.commit()
    return cursor.rowcount > 0


def delete_account(connection, account_id):
    cursor = connection.execute(
        """
        DELETE FROM accounts
        WHERE id = ?
        """,
        (account_id,),
    )

    connection.commit()
    return cursor.rowcount > 0
