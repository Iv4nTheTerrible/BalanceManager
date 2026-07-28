import sqlite3
import unittest


from database import create_transaction_table, insert_transaction, get_transactions


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        create_transaction_table(self.connection)

    def test_create_transaction_table(self):

        table = self.connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'transactions'
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

    def tearDown(self):
        self.connection.close()


if __name__ == "__main__":
    unittest.main()
