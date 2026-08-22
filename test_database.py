import unittest


from database import (
    insert_transaction,
    get_transactions,
    get_transaction_by_id,
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

    def test_delete_account_non_valid_id(self):
        deleted = delete_account(self.connection, 999)

        self.assertFalse(deleted)

    def tearDown(self):
        self.connection.close()


if __name__ == "__main__":
    unittest.main()
