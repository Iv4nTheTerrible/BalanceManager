import json

from database import (
    insert_transaction,
    get_transactions,
    get_transaction_by_id,
    update_transaction_field,
    delete_transaction_by_id,
    connect_database,
)

from datetime import datetime

# Data storage
try:
    with open("data.json", "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = {"next_id": 1, "transactions": {}}


def saving():
    with open("data.json", "w") as file:
        json.dump(data, file, indent=2)


# General helpers
def get_current_datetime():
    return datetime.now().strftime("%Y/%m/%d %H:%M")


# Core transaction operations
def calculate_balance(data):
    balance = 0
    for item in data["transactions"].values():
        if item["type"].lower() == "income":
            balance += item["amount"]
        else:
            balance -= item["amount"]
    return balance


# CLI input helpers
def get_int(txt):
    while True:
        try:
            return int(input(txt))
        except ValueError:
            print("Error, value invalid. Try again.")


def get_amount():
    while True:
        num = get_int("Amount:")
        if num < 0:
            print("Invalid value. Please insert a number greater than or equal 0.")
        else:
            return num


def get_type():
    while True:
        user_input = input("Select type INCOME or EXPENSE.\n[I/E]:")
        if user_input.lower() == "i":
            return "income"
        elif user_input.lower() == "e":
            return "expense"
        else:
            print("Invalid input. Enter I for INCOME or E for EXPENSE.")


# CLI display helpers
def format_transaction(transaction):
    transaction_id, transaction_type, amount, description, date = transaction

    return f"ID: {transaction_id} \nType: {transaction_type} \nAmount: {amount} \nDescription: {description} \nDate: {date}"


def show_transactions(connection):
    transactions = get_transactions(connection)
    for transaction in transactions:
        print("=" * 21)
        print(format_transaction(transaction))
        print("=" * 21)


def show_balance():
    print(calculate_balance(data))


# CLI transaction workflows
def add(connection):
    transaction_type = get_type()
    amount = get_amount()
    description = input("Description:")

    insert_transaction(
        connection,
        transaction_type,
        amount,
        description,
        get_current_datetime(),
    )


def selecting_transaction(connection, action):
    while True:
        transaction_id = input(
            f"Which transaction would you like to {action}?\nPress X to return.\n>"
        )
        if transaction_id.strip().lower() == "x":
            return None
        try:
            transaction_id = int(transaction_id)
        except ValueError:
            print("Invalid ID. Please enter a number.")
            continue
        transaction = get_transaction_by_id(connection, transaction_id)
        if transaction is None:
            user_input = input(
                "Transaction not found. Press ENTER to try again or X to return."
            )
            if user_input.strip().lower() == "x":
                return None
        else:
            return transaction_id, transaction


def selecting_field(connection, transaction_id):
    allowed_fields = {
        "type",
        "amount",
        "description",
        "date",
    }
    while True:
        field = input(">").strip().lower()
        if field == "x":
            return
        elif field not in allowed_fields:
            print("Invalid field. Try type, amount, description, date or X.")
            continue
        if field == "amount":
            new_value = get_amount()
        elif field == "type":
            new_value = get_type()
        else:
            new_value = input(">")
        update_transaction_field(connection, transaction_id, field, new_value)
        print(
            "Transaction updated. What else would you like to edit?\nPress X to return."
        )


def edit(connection):
    selected = selecting_transaction(connection, "edit")
    if selected is None:
        return

    transaction_id, transaction = selected

    print("=" * 21)
    print(format_transaction(transaction))
    print("=" * 21)
    print("What would you like to edit?\nPress X to return.")
    selecting_field(connection, transaction_id)


def delete_transaction(connection):
    selected = selecting_transaction(connection, "delete")
    if selected is None:
        return

    transaction_id, transaction = selected

    print("=" * 21)
    print(format_transaction(transaction))
    print("=" * 21)

    while True:
        user_input = (
            input("Do you really want to delete this transaction?\n[Y/N]:")
            .strip()
            .lower()
        )
        if user_input == "y":
            delete_transaction_by_id(connection, transaction_id)
            break
        elif user_input == "n":
            break
        else:
            print("Invalid input. Please insert Y for YES and N for NO.")


# Menus and application entry point
def sub_menu(connection):
    show_transactions(connection)
    menu = {
        1: lambda: edit(connection),
        2: lambda: delete_transaction(connection),
    }
    while True:
        user_input = get_int("1. Edit \n2. Delete \n3. Return\n>")
        action = menu.get(user_input)
        if action is not None:
            action()
        elif user_input == 3:
            break
        else:
            print("Invalid input. Try again.")


def main():
    connection = connect_database()

    try:
        menu = {
            1: lambda: add(connection),
            2: lambda: sub_menu(connection),
            3: show_balance,
        }
        print("Hi user!")
        while True:
            user_input = get_int(
                "1. Add transaction \n2. Show data\n3. Show balance\n4. Exit\n>"
            )
            action = menu.get(user_input)
            if action is not None:
                action()
            elif user_input == 4:
                break
            else:
                print("Invalid input. Try again.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
