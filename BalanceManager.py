import json

def add():

    transaction_type = input('Type:')
    amount = int(input('Amount:'))
    description = input('description:')
    new_transaction = {
    'type':transaction_type,
    'amount':amount,
    'description': description
    }       
    transactions.append(new_transaction)
    with open("transactions.json","w") as file:
        json.dump(transactions, file)

def show_transactions(transactions):
    for item in transactions:
        print("="*20)
        print(f"{item['type']} \nAmount: {item['amount']} \nDescription: {item['description']}")
        print("="*20)

def calculate_balance(transactions):
    balance = 0
    for item in transactions:
        if item['type'] == 'income':
                balance += item['amount']
        else:
                balance -= item['amount']
    return balance

try:
    with open("transactions.json","r") as file:
            transactions = json.load(file)
except FileNotFoundError: 
    transactions = []

while True:
    print('Hi user! \n1. Add transaction \n2. Show transactions\n3. Show balance\n4. Exit')
    user_input = int(input('>'))
    if user_input == 1:
        add()
    elif user_input == 2:
        show_transactions(transactions)
    elif user_input == 3:
        print(calculate_balance(transactions))
    elif user_input == 4:
        break