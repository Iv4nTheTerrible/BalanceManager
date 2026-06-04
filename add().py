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

try:
    with open("transactions.json","r") as file:
            transactions = json.load(file)
except FileNotFoundError:
    transactions = []

while True:
    add()
    print(transactions)