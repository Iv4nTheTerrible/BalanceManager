import json


from datetime import datetime

calendar_and_clock = datetime.now().strftime("%Y/%m/%d %H:%M")


def saving():
    with open("data.json", "w") as file:
        json.dump(data, file, indent=2)


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
    user_input = input("Select type INCOME or EXPENSE.\n[I/E]:")
    while True:
        if user_input.lower() == "i":
            return "income"
        elif user_input.lower() == "e":
            return "expense"
        else:
            user_input = input(
                "Invalid input. Enter I for INCOME or E for EXPENSE\n[I/E]:"
            )


def add():
    new_id = data["next_id"]
    transaction_type = get_type()
    amount = get_amount()
    description = input("Description:")
    calendar_and_clock = datetime.now().strftime("%Y/%m/%d %H:%M")

    data["transactions"][str(new_id)] = {
        "type": transaction_type,
        "amount": amount,
        "description": description,
        "date": calendar_and_clock,
    }

    data["next_id"] += 1

    saving()


def show_transactions(data):
    for transaction_id, item in data["transactions"].items():
        print("=" * 21)
        print(
            f"ID: {transaction_id} \nType: {item['type']} \nAmount: {item['amount']} \nDescription: {item['description']} \nDate: {item['date']}"
        )
        print("=" * 21)


def calculate_balance(data):
    balance = 0
    for item in data["transactions"].values():
        if item["type"].lower() == "income":
            balance += item["amount"]
        else:
            balance -= item["amount"]
    return balance


def delete_transaction():
    transaction_ID = input(
        "Which transaction would you like to delete?\nTransaction ID:"
    )
    transaction = data["transactions"].get(transaction_ID)
    if transaction is None:
        print("Transaction not found. Try again.")
    else:
        while True:
            user_input = (
                input("Do you really want to delete this transaction?\n[Y/N]:")
                .strip()
                .lower()
            )
            if user_input == "y" or user_input == "n":
                break
            else:
                print("Invalid input. Please insert Y for YES and N for NO.")
        if user_input == "y":
            del data["transactions"][transaction_ID]
            saving()


def edit():
    transaction_ID = input("Which transaction would you like to edit?\nID:")
    transaction = data["transactions"].get(transaction_ID)
    if transaction is None:
        pass
    else:
        print("=" * 21)
        print(
            f"ID: {transaction_ID} \nType: {transaction['type']} \nAmount: {transaction['amount']} \nDescription: {transaction['description']} \nDate: {transaction['date']}"
        )
        print("=" * 21)
        print("What would you like to edit?\nPress X to return.")
        while True:
            user_input = input(">").lower()
            if user_input == "x":
                return
            elif user_input == "amount":
                transaction[user_input] = get_amount()
                saving()
            elif user_input == "type":
                transaction[user_input] = get_type()
                saving()
            elif user_input in transaction:
                transaction[user_input] = input(">")
                saving()


try:
    with open("data.json", "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = {"next_id": 1, "transactions": {}}


while True:
    print("Hi user! \n1. Add transaction \n2. Show data\n3. Show balance\n4. Exit")
    user_input = get_int(">")
    if user_input == 1:
        add()
    elif user_input == 2:
        show_transactions(data)
        while True:
            print("1. Edit \n2. Delete \n3. Return")
            user_input = get_int(">")
            if user_input == 1:
                edit()
            elif user_input == 2:
                delete_transaction()
            elif user_input == 3:
                break
    elif user_input == 3:
        print(calculate_balance(data))
    elif user_input == 4:
        break
