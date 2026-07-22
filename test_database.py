import sqlite3
import unittest


from database import create_transaction_table


class DatabaseTests(unittest.TestCase):
    def test_create_transaction_table(self):
        connection = sqlite3.connect(":memory:")

        create_transaction_table(connection)

        table = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'transactions'
            """).fetchone()

        self.assertIsNotNone(table)

        connection.close()


if __name__ == "__main__":
    unittest.main()
