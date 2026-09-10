import sqlite3
import unittest


from database import (
    create_account_table,
    create_transaction_table,
    insert_transaction,
    get_transactions,
    get_transaction_by_id,
    update_transaction,
    update_transaction_field,
    delete_transaction_by_id,
    connect_database,
    delete_account,
    get_account_by_id,
    get_accounts,
    insert_account,
    update_account_field,
)


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.connection = connect_database(":memory:")

    def test_connect_database_creates_transaction_table(self):

        table = self.connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'transactions'
            """).fetchone()

        self.assertIsNotNone(table)

    def test_connect_database_creates_account_table(self):

        table = self.connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'accounts'
            """).fetchone()

        self.assertIsNotNone(table)

    def test_connect_database_enables_foreign_keys(self):
        enabled = self.connection.execute("PRAGMA foreign_keys").fetchone()

        self.assertEqual(enabled, (1,))

    def test_existing_transaction_table_receives_account_column(self):
        connection = sqlite3.connect(":memory:")
        connection.execute("""
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL
            )
            """)
        connection.execute(
            """
            INSERT INTO transactions (type, amount, description, date)
            VALUES (?, ?, ?, ?)
            """,
            ("expense", 800, "Lunch", "2026/07/23 12:00"),
        )
        create_account_table(connection)
        create_transaction_table(connection)

        columns = {
            column[1]
            for column in connection.execute(
                "PRAGMA table_info(transactions)"
            ).fetchall()
        }
        account_id = connection.execute(
            "SELECT account_id FROM transactions WHERE id = 1"
        ).fetchone()
        connection.close()

        self.assertIn("account_id", columns)
        self.assertEqual(account_id, (None,))

    def test_insert_transaction(self):
        transaction_id = insert_transaction(
            self.connection,
            "expense",
            800,
            "Lunch",
            "2026/07/23 12:00",
        )

        transaction = self.connection.execute(
            """
            SELECT id, type, amount, description, date
            FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        ).fetchone()

        self.assertEqual(transaction_id, 1)
        self.assertEqual(
            transaction,
            (
                1,
                "expense",
                800,
                "Lunch",
                "2026/07/23 12:00",
            ),
        )

    def test_insert_income_updates_selected_account_balance(self):
        insert_account(self.connection, "Bank A", 1000)

        transaction_id = insert_transaction(
            self.connection,
            "income",
            500,
            "Salary",
            "2026/07/23 12:00",
            1,
        )

        self.assertEqual(get_account_by_id(self.connection, 1), (1, "Bank A", 1500))
        self.assertEqual(
            get_transaction_by_id(self.connection, transaction_id),
            (
                transaction_id,
                "income",
                500,
                "Salary",
                "2026/07/23 12:00",
                1,
                "Bank A",
            ),
        )

    def test_insert_expense_updates_selected_account_balance(self):
        insert_account(self.connection, "Digital Wallet", 1000)

        insert_transaction(
            self.connection,
            "expense",
            300,
            "Lunch",
            "2026/07/23 12:00",
            1,
        )

        self.assertEqual(
            get_account_by_id(self.connection, 1),
            (1, "Digital Wallet", 700),
        )

    def test_insert_transaction_without_account_does_not_change_accounts(self):
        insert_account(self.connection, "Cash", 1000)

        insert_transaction(
            self.connection,
            "expense",
            300,
            "Lunch",
            "2026/07/23 12:00",
        )

        self.assertEqual(get_account_by_id(self.connection, 1), (1, "Cash", 1000))

    def test_insert_transaction_rejects_nonexistent_account(self):
        with self.assertRaises(sqlite3.IntegrityError):
            insert_transaction(
                self.connection,
                "expense",
                300,
                "Lunch",
                "2026/07/23 12:00",
                999,
            )

        count = self.connection.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()
        self.assertEqual(count, (0,))

    def test_get_transactions_returns_newest_first(self):
        insert_transaction(
            self.connection,
            "income",
            1000,
            "Salary",
            "2026/07/25 10:00",
        )

        insert_transaction(
            self.connection,
            "expense",
            800,
            "Lunch",
            "2026/07/25 12:00",
        )

        transactions = get_transactions(self.connection)

        self.assertEqual(len(transactions), 2)
        self.assertEqual(
            transactions[0],
            (
                2,
                "expense",
                800,
                "Lunch",
                "2026/07/25 12:00",
                None,
                None,
            ),
        )
        self.assertEqual(
            transactions[1],
            (
                1,
                "income",
                1000,
                "Salary",
                "2026/07/25 10:00",
                None,
                None,
            ),
        )

    def test_get_transaction_by_id(self):
        transaction_id = insert_transaction(
            self.connection,
            "expense",
            800,
            "Lunch",
            "2026/07/28 12:00",
        )

        transaction = get_transaction_by_id(
            self.connection,
            transaction_id,
        )

        self.assertEqual(
            transaction,
            (
                transaction_id,
                "expense",
                800,
                "Lunch",
                "2026/07/28 12:00",
                None,
                None,
            ),
        )

    def test_get_transaction_by_id_non_valid_id(self):
        transaction = get_transaction_by_id(
            self.connection,
            999,
        )

        self.assertIsNone(transaction)

    def test_update_transaction_field(self):
        transaction_id = insert_transaction(
            self.connection,
            "expense",
            800,
            "Lunch",
            "2026/07/28 12:00",
        )

        result = update_transaction_field(
            self.connection,
            transaction_id,
            "description",
            "Dinner",
        )

        transaction = self.connection.execute(
            """
            SELECT description
            FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        ).fetchone()

        self.assertTrue(result)
        self.assertEqual(transaction, ("Dinner",))

    def test_update_transaction_field_non_valid_id(self):
        result = update_transaction_field(
            self.connection,
            999,
            "description",
            "Dinner",
        )

        self.assertFalse(result)

    def test_update_transaction_field_non_valid_field(self):
        transaction_id = insert_transaction(
            self.connection,
            "expense",
            800,
            "Lunch",
            "2026/07/28 12:00",
        )

        result = update_transaction_field(
            self.connection,
            transaction_id,
            "category",
            "Dinner",
        )

        transaction = self.connection.execute(
            """
            SELECT description
            FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        ).fetchone()

        self.assertFalse(result)
        self.assertEqual(transaction, ("Lunch",))

    def test_update_transaction_moves_balance_effect_between_accounts(self):
        insert_account(self.connection, "Cash", 1000)
        insert_account(self.connection, "Bank", 2000)
        transaction_id = insert_transaction(
            self.connection,
            "expense",
            100,
            "Purchase",
            "2026/07/28 12:00",
            1,
        )

        updated = update_transaction(
            self.connection,
            transaction_id,
            "income",
            250,
            "Refund",
            "2026/07/29 12:00",
            2,
        )

        self.assertTrue(updated)
        self.assertEqual(get_account_by_id(self.connection, 1), (1, "Cash", 1000))
        self.assertEqual(get_account_by_id(self.connection, 2), (2, "Bank", 2250))

    def test_update_transaction_rolls_back_for_nonexistent_account(self):
        insert_account(self.connection, "Cash", 1000)
        transaction_id = insert_transaction(
            self.connection,
            "expense",
            100,
            "Purchase",
            "2026/07/28 12:00",
            1,
        )

        with self.assertRaises(sqlite3.IntegrityError):
            update_transaction(
                self.connection,
                transaction_id,
                "expense",
                200,
                "Purchase",
                "2026/07/28 12:00",
                999,
            )

        self.assertEqual(get_account_by_id(self.connection, 1), (1, "Cash", 900))
        self.assertEqual(get_transaction_by_id(self.connection, transaction_id)[2], 100)

    def test_update_transaction_can_remove_account_assignment(self):
        insert_account(self.connection, "Cash", 1000)
        transaction_id = insert_transaction(
            self.connection,
            "expense",
            100,
            "Lunch",
            "2026/07/28 12:00",
            1,
        )

        updated = update_transaction(
            self.connection,
            transaction_id,
            "expense",
            100,
            "Lunch",
            "2026/07/28 12:00",
            None,
        )

        self.assertTrue(updated)
        self.assertEqual(get_account_by_id(self.connection, 1), (1, "Cash", 1000))
        self.assertIsNone(get_transaction_by_id(self.connection, transaction_id)[5])

    def test_transaction_displays_current_account_name_after_rename(self):
        insert_account(self.connection, "Digital A", 1000)
        transaction_id = insert_transaction(
            self.connection,
            "expense",
            100,
            "Lunch",
            "2026/07/28 12:00",
            1,
        )

        update_account_field(self.connection, 1, "name", "Main Wallet")

        transaction = get_transaction_by_id(self.connection, transaction_id)
        self.assertEqual(transaction[5:], (1, "Main Wallet"))

    def test_delete_transaction(self):
        transaction_id = insert_transaction(
            self.connection,
            "expense",
            800,
            "Lunch",
            "2026/07/28 12:00",
        )

        deleted = delete_transaction_by_id(
            self.connection,
            transaction_id,
        )

        transaction = self.connection.execute(
            """
            SELECT id
            FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        ).fetchone()

        self.assertTrue(deleted)
        self.assertIsNone(transaction)

    def test_delete_transaction_non_valid_id(self):
        deleted = delete_transaction_by_id(
            self.connection,
            999,
        )

        self.assertFalse(deleted)

    def test_delete_transaction_reverses_account_balance_effect(self):
        insert_account(self.connection, "Cash", 1000)
        transaction_id = insert_transaction(
            self.connection,
            "expense",
            100,
            "Lunch",
            "2026/07/28 12:00",
            1,
        )

        deleted = delete_transaction_by_id(self.connection, transaction_id)

        self.assertTrue(deleted)
        self.assertEqual(get_account_by_id(self.connection, 1), (1, "Cash", 1000))

    def test_insert_account(self):
        successful_creation = insert_account(
            self.connection,
            "Bank A",
            600000,
        )

        account = self.connection.execute(
            """
            SELECT id, name, balance
            FROM accounts
            WHERE name = ?
            """,
            ("Bank A",),
        ).fetchone()

        self.assertTrue(successful_creation)
        self.assertEqual(
            account,
            (
                1,
                "Bank A",
                600000,
            ),
        )

    def test_insert_account_rejects_duplicate_name_with_different_case(self):
        insert_account(self.connection, "DIGITAL", 20000)

        with self.assertRaises(sqlite3.IntegrityError):
            insert_account(self.connection, "digital", 30000)

        self.assertEqual(get_accounts(self.connection), [(1, "DIGITAL", 20000)])

    def test_get_accounts_returns_newest_first(self):
        insert_account(self.connection, "Bank A", 600000)
        insert_account(self.connection, "Physical Cash", 50000)

        accounts = get_accounts(self.connection)

        self.assertEqual(
            accounts,
            [
                (2, "Physical Cash", 50000),
                (1, "Bank A", 600000),
            ],
        )

    def test_get_account_by_id(self):
        insert_account(self.connection, "Bank A", 600000)

        account = get_account_by_id(self.connection, 1)

        self.assertEqual(account, (1, "Bank A", 600000))

    def test_get_account_by_id_non_valid_id(self):
        account = get_account_by_id(self.connection, 999)

        self.assertIsNone(account)

    def test_update_account_field(self):
        insert_account(self.connection, "Bank A", 600000)

        updated = update_account_field(
            self.connection,
            1,
            "balance",
            590000,
        )
        account = get_account_by_id(self.connection, 1)

        self.assertTrue(updated)
        self.assertEqual(account, (1, "Bank A", 590000))

    def test_update_account_name_rejects_duplicate_with_different_case(self):
        insert_account(self.connection, "DIGITAL", 20000)
        insert_account(self.connection, "Physical Cash", 50000)

        with self.assertRaises(sqlite3.IntegrityError):
            update_account_field(
                self.connection,
                2,
                "name",
                "digital",
            )

        self.assertEqual(
            get_account_by_id(self.connection, 2),
            (2, "Physical Cash", 50000),
        )

    def test_update_account_name_can_change_its_own_case(self):
        insert_account(self.connection, "DIGITAL", 20000)

        updated = update_account_field(
            self.connection,
            1,
            "name",
            "Digital",
        )

        self.assertTrue(updated)
        self.assertEqual(
            get_account_by_id(self.connection, 1),
            (1, "Digital", 20000),
        )

    def test_update_account_field_non_valid_id(self):
        updated = update_account_field(
            self.connection,
            999,
            "balance",
            590000,
        )

        self.assertFalse(updated)

    def test_update_account_field_non_valid_field(self):
        insert_account(self.connection, "Bank A", 600000)

        updated = update_account_field(
            self.connection,
            1,
            "currency",
            "JPY",
        )
        account = get_account_by_id(self.connection, 1)

        self.assertFalse(updated)
        self.assertEqual(account, (1, "Bank A", 600000))

    def test_delete_account(self):
        insert_account(self.connection, "Bank A", 600000)

        deleted = delete_account(self.connection, 1)
        account = get_account_by_id(self.connection, 1)

        self.assertTrue(deleted)
        self.assertIsNone(account)

    def test_delete_account_preserves_transaction_as_unassigned(self):
        insert_account(self.connection, "Cash", 1000)
        transaction_id = insert_transaction(
            self.connection,
            "expense",
            100,
            "Lunch",
            "2026/07/28 12:00",
            1,
        )

        delete_account(self.connection, 1)
        transaction = get_transaction_by_id(self.connection, transaction_id)

        self.assertIsNotNone(transaction)
        self.assertIsNone(transaction[5])
        self.assertIsNone(transaction[6])

    def test_delete_account_non_valid_id(self):
        deleted = delete_account(self.connection, 999)

        self.assertFalse(deleted)

    def tearDown(self):
        self.connection.close()


if __name__ == "__main__":
    unittest.main()
