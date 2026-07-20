# BalanceManager

BalanceManager is a command-line personal finance application written in Python. It records income and expenses in a local JSON file and calculates the user's current balance.

This project began as a Python learning exercise and is being developed gradually into a larger personal finance application.

## Features

- Add income and expense transactions
- View saved transactions
- Calculate the current balance
- Edit transaction type, amount, description, and date
- Delete transactions with confirmation
- Validate menu choices, amounts, and transaction types
- Save data locally in JSON format
- Automated tests for the main behavior

## Requirements

- Python 3.10 or newer
- No third-party packages are required

## Running the application

Clone the repository and enter its directory:

```bash
git clone https://github.com/Iv4nTheTerrible/BalanceManager.git
cd BalanceManager
```

Run the program:

```bash
python BalanceManager.py
```

Depending on your Python installation, the command may instead be:

```bash
py BalanceManager.py
```

The application creates `data.json` when it first saves a transaction.

## Local data

Transactions are stored in `data.json` on the user's computer. This file is ignored by Git so personal financial information is not accidentally committed to the repository.

The repository includes `data.example.json` to demonstrate the expected data structure. It contains only fake example information and is not loaded by the application.

## Running the tests

Run the automated test suite with:

```bash
python -m unittest -v
```

The tests use temporary mock data and do not modify the user's real `data.json` file.

## Current version

Version 1.0 is the first complete command-line release. Future versions may introduce a database and graphical interface.
