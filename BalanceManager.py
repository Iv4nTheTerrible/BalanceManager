import json


def add():
    try:
        new_ID = transactions[-1]["id"] + 1
    except IndexError:
        new_ID = 1
    transaction_type = input("Type:")
    amount = int(input("Amount:"))
    description = input("Description:")
    # date = input('Date:')
    new_transaction = {
        "id": new_ID,
        "type": transaction_type,
        "amount": amount,
        "description": description,
        # 'date': date
    }
    transactions.append(new_transaction)
    with open("transactions.json", "w") as file:
        json.dump(transactions, file, indent=2)


def show_transactions(transactions):
    for item in transactions:
        print("=" * 20)
        print(
            f"ID: {item['id']} \nType: {item['type']} \nAmount: {item['amount']} \nDescription: {item['description']}"
        )
        print("=" * 20)


def delete_transaction():
    for index in range(len(transactions)):
        print(index + 1, "=" * 20)
        print(
            f"{transactions[index]['type']} \nAmount: {transactions[index]['amount']} \nDescription: {transactions[index]['description']}"
        )
        print("=" * 20)
    print("Which transaction would you like to delete?")
    user_input2 = int(input(">")) - 1
    transactions.pop(user_input2)
    with open("transactions.json", "w") as file:
        json.dump(transactions, file, indent=2)


def calculate_balance(transactions):
    balance = 0
    for item in transactions:
        if item["type"].lower() == "income":
            balance += item["amount"]
        else:
            balance -= item["amount"]
    return balance


try:
    with open("transactions.json", "r") as file:
        transactions = json.load(file)
except FileNotFoundError:
    transactions = []

while True:
    print(
        "Hi user! \n1. Add transaction \n2. Show transactions\n3. Show balance\n4. Delete transaction\n5. Exit"
    )
    user_input = int(input(">"))
    if user_input == 1:
        add()
    elif user_input == 2:
        show_transactions(transactions)
    elif user_input == 3:
        print(calculate_balance(transactions))
    elif user_input == 4:
        delete_transaction()
    elif user_input == 5:
        break
