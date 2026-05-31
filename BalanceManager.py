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

for item in transactions:
    print("="*20)
    print(f"{item['type']} \nAmount: {item['amount']} \nDescription: {item['description']}")
    print("="*20)