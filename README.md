# BalanceManager

BalanceManager is a personal-finance learning project. Its **current, working
application is written in Python**: a Tkinter desktop interface and a CLI use a
local SQLite database to track accounts, income, and expenses.

A separate **Flutter/Dart application is planned**, starting with Android and
Windows. It will keep an active local database so viewing and editing work
offline. Supabase synchronization and iOS support are later stages, not current
features. There is no required Java backend. See [ROADMAP.md](ROADMAP.md) for the
planned sequence and financial rules.

## What works today

- Create and edit accounts, and record income and expenses against them.
- View transactions and account balances in the Tkinter desktop interface.
- Edit and delete transactions.
- Use the command-line interface for transaction operations.
- Store data locally in SQLite.
- Run automated tests for the current Python behavior.

The current application does **not** yet have transfers, balance adjustments,
monthly reports, cloud synchronization, or a Flutter client.

## Run the current Python application

Requirements: Python 3.10 or newer. No third-party packages are required for
the current Python app.

```bash
git clone https://github.com/Iv4nTheTerrible/BalanceManager.git
cd BalanceManager
python desktop_ui.py
```

To use the CLI instead:

```bash
python cli.py
```

On Windows, `py` may work in place of `python`. The application creates
`balance_manager.db` when it starts. That file is ignored by Git; a Git commit
does not back up personal finance data.

## Tests

```bash
python -m unittest -v
```

The existing tests use in-memory databases and mock data, not the user's
`balance_manager.db` file.

## Development direction

Keep the Python application available while building and verifying the Flutter
replacement. The Flutter app will use local SQLite first, implement the agreed
ledger and monthly-report behavior, and only then add Supabase synchronization.
iOS remains a goal when macOS/Xcode access is available for building and
testing; Android and Windows do not wait on that access.
