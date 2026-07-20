import unittest
from unittest.mock import patch

import BalanceManager as balance_manager


class BalanceManagerTests(unittest.TestCase):
    def setUp(self):
        self.original_data = balance_manager.data
        balance_manager.data = {
            "next_id": 3,
            "transactions": {
                "1": {
                    "type": "income",
                    "amount": 1000,
                    "description": "Salary",
                    "date": "2026/07/17 10:00",
                },
                "2": {
                    "type": "expense",
                    "amount": 250,
                    "description": "Lunch",
                    "date": "2026/07/17 12:00",
                },
            },
        }

    def tearDown(self):
        balance_manager.data = self.original_data

    def test_calculate_balance(self):
        self.assertEqual(balance_manager.calculate_balance(balance_manager.data), 750)

    def test_calculate_balance_with_no_transactions(self):
        empty_data = {"next_id": 1, "transactions": {}}
        self.assertEqual(balance_manager.calculate_balance(empty_data), 0)

    def test_get_int_retries_after_invalid_input(self):
        with patch("builtins.input", side_effect=["not a number", "42"]):
            self.assertEqual(balance_manager.get_int("Number:"), 42)

    def test_get_amount_rejects_negative_numbers(self):
        with patch.object(balance_manager, "get_int", side_effect=[-10, 0]):
            self.assertEqual(balance_manager.get_amount(), 0)

    def test_get_type_retries_after_invalid_input(self):
        with patch("builtins.input", side_effect=["wrong", "e"]):
            self.assertEqual(balance_manager.get_type(), "expense")

    def test_create_transaction_and_increment_next_id(self):
        with (
            patch.object(
                balance_manager,
                "get_current_datetime",
                return_value="2026/07/20 15:00",
            ),
            patch.object(balance_manager, "saving") as saving,
        ):
            balance_manager.create_transaction(
                "income",
                500,
                "Freelance",
            )

        self.assertEqual(balance_manager.data["next_id"], 4)
        self.assertEqual(
            balance_manager.data["transactions"]["3"],
            {
                "type": "income",
                "amount": 500,
                "description": "Freelance",
                "date": "2026/07/20 15:00",
            },
        )
        saving.assert_called_once()

    def test_add_passes_user_input_to_create_transaction(self):
        with (
            patch.object(balance_manager, "get_type", return_value="expense"),
            patch.object(balance_manager, "get_amount", return_value=800),
            patch("builtins.input", return_value="Lunch"),
            patch.object(balance_manager, "create_transaction") as create_transaction,
        ):
            balance_manager.add()

        create_transaction.assert_called_once_with(
            "expense",
            800,
            "Lunch",
        )

    def test_delete_transaction_after_confirmation(self):
        with (
            patch("builtins.input", side_effect=["2", "y"]),
            patch.object(balance_manager, "saving") as saving,
        ):
            balance_manager.delete_transaction()

        self.assertNotIn("2", balance_manager.data["transactions"])
        saving.assert_called_once()

    def test_delete_transaction_can_be_cancelled(self):
        with (
            patch("builtins.input", side_effect=["2", "n"]),
            patch.object(balance_manager, "saving") as saving,
        ):
            balance_manager.delete_transaction()

        self.assertIn("2", balance_manager.data["transactions"])
        saving.assert_not_called()

    def test_selecting_transaction_returns_selected_item(self):
        with patch("builtins.input", return_value="1"):
            transaction_id, transaction = balance_manager.selecting_transaction()

        self.assertEqual(transaction_id, "1")
        self.assertIs(transaction, balance_manager.data["transactions"]["1"])

    def test_selecting_transaction_can_exit(self):
        with patch("builtins.input", return_value="x"):
            self.assertIsNone(balance_manager.selecting_transaction())

    def test_editing_description_changes_transaction_and_saves(self):
        transaction = balance_manager.data["transactions"]["1"]
        with (
            patch("builtins.input", side_effect=["description", "New salary", "x"]),
            patch.object(balance_manager, "saving") as saving,
        ):
            balance_manager.editing_fields(transaction)

        self.assertEqual(transaction["description"], "New salary")
        saving.assert_called_once()

    def test_format_transaction_contains_important_fields(self):
        result = balance_manager.format_transaction(
            "1", balance_manager.data["transactions"]["1"]
        )

        self.assertIn("ID: 1", result)
        self.assertIn("Type: income", result)
        self.assertIn("Amount: 1000", result)
        self.assertIn("Description: Salary", result)

    def test_delete_transaction_can_exit_after_invalid_id(self):
        with (
            patch("builtins.input", side_effect=["999", "x"]),
            patch.object(balance_manager, "saving") as saving,
        ):
            balance_manager.delete_transaction()

        self.assertIn("1", balance_manager.data["transactions"])
        self.assertIn("2", balance_manager.data["transactions"])
        saving.assert_not_called()

    def test_remove_transaction_deletes_existing_transaction(self):
        with patch.object(balance_manager, "saving") as saving:
            result = balance_manager.remove_transaction("2")

        self.assertTrue(result)
        self.assertNotIn("2", balance_manager.data["transactions"])
        saving.assert_called_once()

    def test_remove_transaction_rejects_missing_transaction(self):
        with patch.object(balance_manager, "saving") as saving:
            result = balance_manager.remove_transaction("999")

        self.assertFalse(result)
        self.assertIn("1", balance_manager.data["transactions"])
        self.assertIn("2", balance_manager.data["transactions"])
        saving.assert_not_called()


if __name__ == "__main__":
    unittest.main()
