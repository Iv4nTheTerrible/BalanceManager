def show_transactions():
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

transactions = [
{
'type' : 'income',
'amount' : 60000,
'description' : 'baito'
},
{
'type' : 'expense',
'amount' : 9500,
'description' : 'les mis book'
},
{
'type' : 'expense',
'amount' : 1000,
'description' : 'food'
}
]

show_transactions()
current_balance = calculate_balance(transactions)
print(current_balance)