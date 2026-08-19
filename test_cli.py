import unittest
from unittest.mock import patch

import cli as balance_manager


class BalanceManagerTests(unittest.TestCase):
    def test_calculate_balance(self):
        connection = object()
        transactions = [
            (1, "income", 1000, "Salary", "2026/08/09 10:00"),
            (2, "expense", 250, "Lunch", "2026/08/09 12:00"),
        ]

        with patch.object(
            balance_manager,
            "get_transactions",
            return_value=transactions,
        ) as get_transactions:
            result = balance_manager.calculate_balance(connection)

        self.assertEqual(result, 750)
        get_transactions.assert_called_once_with(connection)

    def test_calculate_balance_with_no_transactions(self):
        connection = object()

        with patch.object(
            balance_manager,
            "get_transactions",
            return_value=[],
        ):
            result = balance_manager.calculate_balance(connection)

        self.assertEqual(result, 0)

    def test_get_int_retries_after_invalid_input(self):
        with patch("builtins.input", side_effect=["not a number", "42"]):
            self.assertEqual(balance_manager.get_int("Number:"), 42)

    def test_get_amount_rejects_negative_numbers(self):
        with patch.object(balance_manager, "get_int", side_effect=[-10, 0]):
            self.assertEqual(balance_manager.get_amount(), 0)

    def test_get_type_retries_after_invalid_input(self):
        with patch("builtins.input", side_effect=["wrong", "e"]):
            self.assertEqual(balance_manager.get_type(), "expense")

    def test_add_passes_user_input_to_insert_transaction(self):
        connection = object()

        with (
            patch.object(balance_manager, "get_type", return_value="expense"),
            patch.object(balance_manager, "get_amount", return_value=800),
            patch("builtins.input", return_value="Lunch"),
            patch.object(
                balance_manager,
                "get_current_datetime",
                return_value="2026/08/07 12:00",
            ),
            patch.object(balance_manager, "insert_transaction") as insert_transaction,
        ):
            balance_manager.add(connection)

        insert_transaction.assert_called_once_with(
            connection,
            "expense",
            800,
            "Lunch",
            "2026/08/07 12:00",
        )

    def test_delete_transaction_after_confirmation(self):
        connection = object()
        transaction = (
            1,
            "expense",
            800,
            "Lunch",
            "2026/08/09 12:00",
        )

        with (
            patch.object(
                balance_manager,
                "selecting_transaction",
                return_value=(1, transaction),
            ),
            patch("builtins.input", return_value="y"),
            patch.object(
                balance_manager,
                "delete_transaction_by_id",
            ) as delete_transaction_by_id,
        ):
            balance_manager.delete_transaction(connection)

        delete_transaction_by_id.assert_called_once_with(connection, 1)

    def test_delete_transaction_can_be_cancelled(self):
        connection = object()
        transaction = (
            1,
            "expense",
            800,
            "Lunch",
            "2026/08/09 12:00",
        )

        with (
            patch.object(
                balance_manager,
                "selecting_transaction",
                return_value=(1, transaction),
            ),
            patch("builtins.input", return_value="n"),
            patch.object(
                balance_manager,
                "delete_transaction_by_id",
            ) as delete_transaction_by_id,
        ):
            balance_manager.delete_transaction(connection)

        delete_transaction_by_id.assert_not_called()

    def test_selecting_transaction_returns_selected_item(self):
        connection = object()
        transaction = (
            1,
            "income",
            1000,
            "Salary",
            "2026/07/17 10:00",
        )

        with (
            patch("builtins.input", return_value="1"),
            patch.object(
                balance_manager,
                "get_transaction_by_id",
                return_value=transaction,
            ) as get_transaction_by_id,
        ):
            result = balance_manager.selecting_transaction(connection, "edit")

        self.assertEqual(result, (1, transaction))
        get_transaction_by_id.assert_called_once_with(connection, 1)

    def test_selecting_transaction_can_exit(self):
        connection = object()

        with (
            patch("builtins.input", return_value="x"),
            patch.object(
                balance_manager,
                "get_transaction_by_id",
            ) as get_transaction_by_id,
        ):
            result = balance_manager.selecting_transaction(connection, "edit")

        self.assertIsNone(result)
        get_transaction_by_id.assert_not_called()

    def test_selecting_field_passes_description_to_update_transaction(self):
        connection = object()

        with (
            patch(
                "builtins.input",
                side_effect=["description", "New salary", "x"],
            ),
            patch.object(
                balance_manager,
                "update_transaction_field",
            ) as update_transaction_field,
        ):
            balance_manager.selecting_field(connection, 1)

        update_transaction_field.assert_called_once_with(
            connection,
            1,
            "description",
            "New salary",
        )

    def test_format_transaction_contains_important_fields(self):
        transaction = (
            1,
            "income",
            1000,
            "Salary",
            "2026/07/17 10:00",
        )
        result = balance_manager.format_transaction(transaction)

        self.assertIn("ID: 1", result)
        self.assertIn("Type: income", result)
        self.assertIn("Amount: 1000", result)
        self.assertIn("Description: Salary", result)

    def test_show_transactions_reads_and_displays_database_transactions(self):
        connection = object()
        transaction = (
            1,
            "expense",
            800,
            "Lunch",
            "2026/08/07 12:00",
        )

        with (
            patch.object(
                balance_manager,
                "get_transactions",
                return_value=[transaction],
            ) as get_transactions,
            patch.object(
                balance_manager,
                "format_transaction",
                return_value="Formatted transaction",
            ) as format_transaction,
            patch("builtins.print") as print_mock,
        ):
            result = balance_manager.show_transactions(connection)

        self.assertTrue(result)
        get_transactions.assert_called_once_with(connection)
        format_transaction.assert_called_once_with(transaction)
        print_mock.assert_any_call("Formatted transaction")

    def test_show_transactions_reports_when_database_is_empty(self):
        connection = object()

        with (
            patch.object(
                balance_manager,
                "get_transactions",
                return_value=[],
            ) as get_transactions,
            patch("builtins.print") as print_mock,
        ):
            result = balance_manager.show_transactions(connection)

        self.assertFalse(result)
        get_transactions.assert_called_once_with(connection)
        print_mock.assert_called_once_with(
            "No transactions found, try adding a transaction."
        )

    def test_sub_menu_displays_transactions_once(self):
        connection = object()

        with (
            patch.object(
                balance_manager,
                "show_transactions",
                return_value=True,
            ) as show_transactions,
            patch.object(balance_manager, "get_int", return_value=3),
        ):
            balance_manager.sub_menu(connection)

        show_transactions.assert_called_once_with(connection)

    def test_delete_transaction_can_exit_after_invalid_id(self):
        connection = object()

        with (
            patch.object(
                balance_manager,
                "selecting_transaction",
                return_value=None,
            ),
            patch.object(
                balance_manager,
                "delete_transaction_by_id",
            ) as delete_transaction_by_id,
        ):
            balance_manager.delete_transaction(connection)

        delete_transaction_by_id.assert_not_called()


if __name__ == "__main__":
    unittest.main()
