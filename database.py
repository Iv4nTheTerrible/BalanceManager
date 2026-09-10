import sqlite3


def create_account_table(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            balance INTEGER NOT NULL
        )
        """)


def create_transaction_table(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL,
            account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL
        )
        """)

    columns = {
        column[1]
        for column in connection.execute("PRAGMA table_info(transactions)").fetchall()
    }
    if "account_id" not in columns:
        connection.execute("""
            ALTER TABLE transactions
            ADD COLUMN account_id INTEGER
                REFERENCES accounts(id) ON DELETE SET NULL
            """)


def connect_database(database_path="balance_manager.db"):
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    create_account_table(connection)
    create_transaction_table(connection)
    connection.commit()
    return connection


def transaction_balance_change(transaction_type, amount):
    if transaction_type == "expense":
        return -amount
    return amount


def insert_transaction(
    connection,
    transaction_type,
    amount,
    description,
    date,
    account_id=None,
):
    try:
        cursor = connection.execute(
            """
            INSERT INTO transactions (
                type,
                amount,
                description,
                date,
                account_id
            )
            VALUES (?,?,?,?,?)
            """,
            (
                transaction_type,
                amount,
                description,
                date,
                account_id,
            ),
        )
        if account_id is not None:
            change = transaction_balance_change(transaction_type, amount)
            if not adjust_account_balance(connection, account_id, change):
                raise sqlite3.IntegrityError("The selected account does not exist.")

        connection.commit()
    except Exception:
        connection.rollback()
        raise

    return cursor.lastrowid


def get_transactions(connection):
    return connection.execute("""
        SELECT
            transactions.id,
            transactions.type,
            transactions.amount,
            transactions.description,
            transactions.date,
            transactions.account_id,
            accounts.name
        FROM transactions
        LEFT JOIN accounts
            ON transactions.account_id = accounts.id
        ORDER BY
            transactions.id DESC""").fetchall()


def get_transaction_by_id(connection, transaction_id):
    return connection.execute(
        """
        SELECT
            transactions.id,
            transactions.type,
            transactions.amount,
            transactions.description,
            transactions.date,
            transactions.account_id,
            accounts.name
        FROM transactions
        LEFT JOIN accounts
            ON transactions.account_id = accounts.id
        WHERE transactions.id = ?
        """,
        (transaction_id,),
    ).fetchone()


def update_transaction(
    connection,
    transaction_id,
    transaction_type,
    amount,
    description,
    date,
    account_id=None,
):
    old_transaction = get_transaction_by_id(connection, transaction_id)
    if old_transaction is None:
        return False

    _, old_type, old_amount, _, _, old_account_id, _ = old_transaction

    try:
        if old_account_id is not None:
            old_change = transaction_balance_change(old_type, old_amount)
            if not adjust_account_balance(
                connection,
                old_account_id,
                -old_change,
            ):
                raise sqlite3.IntegrityError(
                    "The transaction's previous account does not exist."
                )

        cursor = connection.execute(
            """
            UPDATE transactions
            SET type = ?,
                amount = ?,
                description = ?,
                date = ?,
                account_id = ?
            WHERE id = ?
            """,
            (
                transaction_type,
                amount,
                description,
                date,
                account_id,
                transaction_id,
            ),
        )

        if account_id is not None:
            new_change = transaction_balance_change(transaction_type, amount)
            if not adjust_account_balance(connection, account_id, new_change):
                raise sqlite3.IntegrityError("The selected account does not exist.")

        connection.commit()
    except Exception:
        connection.rollback()
        raise

    return cursor.rowcount > 0


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
        "account_id",
    }

    if field not in allowed_fields:
        return False

    transaction = get_transaction_by_id(connection, transaction_id)
    if transaction is None:
        return False

    values = {
        "type": transaction[1],
        "amount": transaction[2],
        "description": transaction[3],
        "date": transaction[4],
        "account_id": transaction[5],
    }
    values[field] = new_value

    return update_transaction(
        connection,
        transaction_id,
        values["type"],
        values["amount"],
        values["description"],
        values["date"],
        values["account_id"],
    )


def delete_transaction_by_id(connection, transaction_id):
    transaction = get_transaction_by_id(connection, transaction_id)
    if transaction is None:
        return False

    _, transaction_type, amount, _, _, account_id, _ = transaction

    try:
        if account_id is not None:
            change = transaction_balance_change(transaction_type, amount)
            if not adjust_account_balance(connection, account_id, -change):
                raise sqlite3.IntegrityError(
                    "The transaction's account does not exist."
                )

        cursor = connection.execute(
            """
            DELETE FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        )

        connection.commit()
    except Exception:
        connection.rollback()
        raise

    return cursor.rowcount > 0


def insert_account(connection, name, balance):
    name = name.strip()
    duplicate = connection.execute(
        """
        SELECT name
        FROM accounts
        WHERE name = ? COLLATE NOCASE
        """,
        (name,),
    ).fetchone()

    if duplicate is not None:
        raise sqlite3.IntegrityError(
            f'An account named "{duplicate[0]}" already exists. '
            "Please choose a different name."
        )

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

    if field == "name":
        if get_account_by_id(connection, account_id) is None:
            return False

        new_value = new_value.strip()
        duplicate = connection.execute(
            """
            SELECT name
            FROM accounts
            WHERE name = ? COLLATE NOCASE
            AND id != ?
            """,
            (new_value, account_id),
        ).fetchone()

        if duplicate is not None:
            raise sqlite3.IntegrityError(
                f'An account named "{duplicate[0]}" already exists. '
                "Please choose a different name."
            )

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


def adjust_account_balance(
    connection,
    account_id,
    change,
):

    cursor = connection.execute(
        """
        UPDATE accounts
        SET balance = balance + ?
        WHERE id = ?
        """,
        (
            change,
            account_id,
        ),
    )

    return cursor.rowcount > 0
