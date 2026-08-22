import unittest

from desktop_ui import validate_account_input, validate_transaction_input


class DesktopUIValidationTests(unittest.TestCase):
    def test_valid_transaction_input_is_normalized(self):
        result = validate_transaction_input(
            " Income ",
            "1200",
            " Freelance work ",
            " 2026/08/09 12:00 ",
        )

        self.assertEqual(
            result,
            ("income", 1200, "Freelance work", "2026/08/09 12:00"),
        )

    def test_amount_must_be_a_whole_number(self):
        with self.assertRaisesRegex(ValueError, "whole number"):
            validate_transaction_input(
                "expense",
                "12.50",
                "Lunch",
                "2026/08/09 12:00",
            )

    def test_amount_cannot_be_negative(self):
        with self.assertRaisesRegex(ValueError, "greater than or equal to zero"):
            validate_transaction_input(
                "expense",
                "-1",
                "Lunch",
                "2026/08/09 12:00",
            )

    def test_description_can_be_empty(self):
        result = validate_transaction_input(
            "expense",
            "800",
            "  ",
            "2026/08/09 12:00",
        )

        self.assertEqual(result[2], "")

    def test_valid_account_input_is_normalized(self):
        result = validate_account_input(" Physical Cash ", "50000")

        self.assertEqual(result, ("Physical Cash", 50000))

    def test_account_name_cannot_be_empty(self):
        with self.assertRaisesRegex(ValueError, "name"):
            validate_account_input("  ", "50000")

    def test_account_balance_must_be_a_whole_number(self):
        with self.assertRaisesRegex(ValueError, "whole number"):
            validate_account_input("Physical Cash", "50.50")


if __name__ == "__main__":
    unittest.main()
