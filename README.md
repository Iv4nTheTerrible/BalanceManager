# BalanceManager

BalanceManager is a personal finance application written in Python. It records income and expenses in a local SQLite database and includes both a desktop interface and a command-line interface.

This project began as a Python learning exercise and is being developed gradually into a larger personal finance application.

## Features

- Add income and expense transactions
- View saved transactions
- Calculate the current balance
- Edit transaction type, amount, description, and date
- Delete transactions with confirmation
- Validate menu choices, amounts, and transaction types
- Save data locally in SQLite
- Use a desktop interface built with Tkinter
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

Run the desktop interface:

```bash
python desktop_ui.py
```

Run the command-line interface:

```bash
python BalanceManager.py
```

Depending on your Python installation, the command may instead be:

```bash
py BalanceManager.py
```

The application creates `balance_manager.db` automatically when it starts.

## Local data

Transactions are stored in `balance_manager.db` on the user's computer. This file is ignored by Git so personal financial information is not accidentally committed to the repository.

## Running the tests

Run the automated test suite with:

```bash
python -m unittest -v
```

The tests use in-memory databases and mock data. They do not modify the user's real `balance_manager.db` file.

## Current version

Version 1.0 is the first complete command-line release. The current development branch adds SQLite storage and a Tkinter desktop interface.
