import json

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
def create_transaction(transaction_type, amount, description):
    new_id = data["next_id"]
    transaction_date = get_current_datetime()

    data["transactions"][str(new_id)] = {
        "type": transaction_type,
        "amount": amount,
        "description": description,
        "date": transaction_date,
    }

    data["next_id"] += 1
    saving()


def remove_transaction(transaction_id):
    if transaction_id not in data["transactions"]:
        return False

    del data["transactions"][transaction_id]
    saving()
    return True


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
def format_transaction(txt1, txt2):
    return f"ID: {txt1} \nType: {txt2['type']} \nAmount: {txt2['amount']} \nDescription: {txt2['description']} \nDate: {txt2['date']}"


def show_transactions(data):
    for transaction_id, item in data["transactions"].items():
        print("=" * 21)
        print(format_transaction(transaction_id, item))
        print("=" * 21)


def show_balance():
    print(calculate_balance(data))


# CLI transaction workflows
def add():
    transaction_type = get_type()
    amount = get_amount()
    description = input("Description:")

    create_transaction(transaction_type, amount, description)


def selecting_transaction():
    while True:
        transaction_id = input(
            "Which transaction would you like to edit?\nPress X to return.\n>"
        )
        if transaction_id.strip().lower() == "x":
            return None
        transaction = data["transactions"].get(transaction_id)
        if transaction is None:
            user_input = input(
                "Transaction not found. Press ENTER to try again or X to return."
            )
            if user_input.strip().lower() == "x":
                return None
        else:
            return transaction_id, transaction


def selecting_field(transaction):
    while True:
        field = input(">").strip().lower()
        if field == "x":
            return
        elif field not in transaction:
            print("Invalid field. Try type, amount, description, date or X.")
            continue
        if field == "amount":
            new_value = get_amount()
        elif field == "type":
            new_value = get_type()
        else:
            new_value = input(">")
        update_field(transaction, field, new_value)
        print(
            "Transaction updated. What else would you like to edit?\nPress X to return."
        )


def update_field(transaction, field, updated_value):
    if field not in transaction:
        return False

    transaction[field] = updated_value
    saving()
    return True


def edit():
    selected = selecting_transaction()
    if selected is None:
        return
    transaction_id, transaction = selected
    print("=" * 21)
    print(format_transaction(transaction_id, transaction))
    print("=" * 21)
    print("What would you like to edit?\nPress X to return.")
    selecting_field(transaction)


def delete_transaction():
    transaction_id = input(
        "Which transaction would you like to delete?\nPress X to return\nTransaction ID:"
    ).strip()
    while True:
        if transaction_id.lower() == "x":
            return
        transaction = data["transactions"].get(transaction_id)
        if transaction is None:
            transaction_id = input("Transaction not found. Try again.\nTransaction ID:")
            continue
        break
    while True:
        user_input = (
            input("Do you really want to delete this transaction?\n[Y/N]:")
            .strip()
            .lower()
        )
        if user_input == "y":
            remove_transaction(transaction_id)
            break
        elif user_input == "n":
            break
        else:
            print("Invalid input. Please insert Y for YES and N for NO.")


# Menus and application entry point
def sub_menu():
    show_transactions(data)
    menu = {1: edit, 2: delete_transaction}
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
    menu = {1: add, 2: sub_menu, 3: show_balance}
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


if __name__ == "__main__":
    main()
