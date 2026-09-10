import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from database import (
    connect_database,
    delete_account as delete_account_by_id,
    delete_transaction_by_id,
    get_account_by_id,
    get_accounts,
    get_transaction_by_id,
    get_transactions,
    insert_account,
    insert_transaction,
    update_account_field,
    update_transaction,
)

TRANSACTION_TYPES = ("income", "expense")
NO_ACCOUNT_LABEL = "No account"


def get_current_datetime():
    return datetime.now().strftime("%Y/%m/%d %H:%M")


def validate_transaction_input(transaction_type, amount_text, description, date):
    transaction_type = transaction_type.strip().lower()
    description = description.strip()
    date = date.strip()

    if transaction_type not in TRANSACTION_TYPES:
        raise ValueError("Select income or expense.")

    try:
        amount = int(amount_text)
    except ValueError as error:
        raise ValueError("Amount must be a whole number.") from error

    if amount < 0:
        raise ValueError("Amount must be greater than or equal to zero.")
    if not date:
        raise ValueError("Date cannot be empty.")

    return transaction_type, amount, description, date


def validate_account_input(name, balance_text):
    name = name.strip()

    if not name:
        raise ValueError("Account name cannot be empty.")

    try:
        balance = int(balance_text)
    except ValueError as error:
        raise ValueError("Balance must be a whole number.") from error

    return name, balance


def build_account_options(accounts):
    options = {NO_ACCOUNT_LABEL: None}
    for account_id, name, _balance in accounts:
        label = name
        if label == NO_ACCOUNT_LABEL:
            label = f"{name} (ID {account_id})"
        options[label] = account_id
    return options


class TransactionDialog(tk.Toplevel):
    def __init__(self, parent, title, initial_values=None, account_options=None):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)

        initial_values = initial_values or (
            "expense",
            "",
            "",
            get_current_datetime(),
            None,
        )
        if len(initial_values) == 4:
            initial_values = (*initial_values, None)

        self.account_options = account_options or {NO_ACCOUNT_LABEL: None}
        selected_account = next(
            (
                label
                for label, account_id in self.account_options.items()
                if account_id == initial_values[4]
            ),
            NO_ACCOUNT_LABEL,
        )

        self.type_var = tk.StringVar(value=initial_values[0])
        self.amount_var = tk.StringVar(value=str(initial_values[1]))
        self.description_var = tk.StringVar(value=initial_values[2])
        self.date_var = tk.StringVar(value=initial_values[3])
        self.account_var = tk.StringVar(value=selected_account)
        self.error_var = tk.StringVar()

        content = ttk.Frame(self, padding=20)
        content.grid(sticky="nsew")
        content.columnconfigure(1, weight=1)

        ttk.Label(content, text="Type").grid(row=0, column=0, sticky="w", pady=6)
        type_input = ttk.Combobox(
            content,
            textvariable=self.type_var,
            values=TRANSACTION_TYPES,
            state="readonly",
            width=28,
        )
        type_input.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Amount").grid(row=1, column=0, sticky="w", pady=6)
        amount_input = ttk.Entry(content, textvariable=self.amount_var, width=30)
        amount_input.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Description").grid(row=2, column=0, sticky="w", pady=6)
        description_input = ttk.Entry(
            content,
            textvariable=self.description_var,
            width=30,
        )
        description_input.grid(row=2, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Date").grid(row=3, column=0, sticky="w", pady=6)
        date_input = ttk.Entry(content, textvariable=self.date_var, width=30)
        date_input.grid(row=3, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Account").grid(row=4, column=0, sticky="w", pady=6)
        ttk.Combobox(
            content,
            textvariable=self.account_var,
            values=tuple(self.account_options),
            state="readonly",
            width=28,
        ).grid(row=4, column=1, sticky="ew", pady=6)

        ttk.Label(
            content,
            textvariable=self.error_var,
            foreground="#b42318",
            wraplength=280,
        ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 2))

        buttons = ttk.Frame(content)
        buttons.grid(row=6, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(buttons, text="Save", command=self.save).pack(side="left")

        self.bind("<Return>", lambda _event: self.save())
        self.bind("<Escape>", lambda _event: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        description_input.focus_set()
        self.grab_set()
        self.wait_window()

    def save(self):
        try:
            transaction = validate_transaction_input(
                self.type_var.get(),
                self.amount_var.get(),
                self.description_var.get(),
                self.date_var.get(),
            )
        except ValueError as error:
            self.error_var.set(str(error))
            return

        account_id = self.account_options[self.account_var.get()]
        self.result = (*transaction, account_id)
        self.destroy()


class AccountDialog(tk.Toplevel):
    def __init__(self, parent, title, initial_values=None, on_save=None):
        super().__init__(parent)
        self.result = None
        self.on_save = on_save
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)

        initial_values = initial_values or ("", 0)

        self.name_var = tk.StringVar(value=initial_values[0])
        self.balance_var = tk.StringVar(value=str(initial_values[1]))
        self.error_var = tk.StringVar()

        content = ttk.Frame(self, padding=20)
        content.grid(sticky="nsew")
        content.columnconfigure(1, weight=1)

        ttk.Label(content, text="Account name").grid(
            row=0, column=0, sticky="w", pady=6
        )
        name_input = ttk.Entry(content, textvariable=self.name_var, width=30)
        name_input.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(content, text="Current balance").grid(
            row=1, column=0, sticky="w", pady=6
        )
        ttk.Entry(content, textvariable=self.balance_var, width=30).grid(
            row=1, column=1, sticky="ew", pady=6
        )

        ttk.Label(
            content,
            textvariable=self.error_var,
            foreground="#b42318",
            wraplength=280,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 2))

        buttons = ttk.Frame(content)
        buttons.grid(row=3, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(buttons, text="Save", command=self.save).pack(side="left")

        self.bind("<Return>", lambda _event: self.save())
        self.bind("<Escape>", lambda _event: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        name_input.focus_set()
        self.grab_set()
        self.wait_window()

    def save(self):
        try:
            result = validate_account_input(
                self.name_var.get(),
                self.balance_var.get(),
            )
            if self.on_save is not None:
                self.on_save(*result)
        except (ValueError, sqlite3.IntegrityError) as error:
            self.error_var.set(str(error))
            return

        self.result = result
        self.destroy()


class BalanceManagerApp:
    def __init__(self, root, connection):
        self.root = root
        self.connection = connection
        self.balance_var = tk.StringVar(value="¥0")
        self.status_var = tk.StringVar(value="Ready")

        self.root.title("BalanceManager")
        self.root.geometry("980x620")
        self.root.minsize(760, 480)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.configure_styles()
        self.build_layout()
        self.refresh()

    def configure_styles(self):
        style = ttk.Style(self.root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", foreground="#667085")
        style.configure("Balance.TLabel", font=("Segoe UI", 28, "bold"))
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def build_layout(self):
        container = ttk.Frame(self.root, padding=24)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="BalanceManager", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text="Your local income and expense tracker",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        balance_panel = ttk.Frame(header)
        balance_panel.grid(row=0, column=1, rowspan=2, sticky="e")
        ttk.Label(balance_panel, text="CURRENT BALANCE", style="Subtitle.TLabel").pack(
            anchor="e"
        )
        ttk.Label(
            balance_panel,
            textvariable=self.balance_var,
            style="Balance.TLabel",
        ).pack(anchor="e")

        notebook = ttk.Notebook(container)
        notebook.grid(row=1, column=0, sticky="nsew", pady=(24, 0))

        self.transactions_tab = ttk.Frame(notebook, padding=14)
        self.accounts_tab = ttk.Frame(notebook, padding=14)
        notebook.add(self.transactions_tab, text="Transactions")
        notebook.add(self.accounts_tab, text="Accounts")

        self.build_transactions_tab()
        self.build_accounts_tab()

        ttk.Separator(container).grid(row=2, column=0, sticky="ew", pady=(14, 8))
        ttk.Label(
            container,
            textvariable=self.status_var,
            style="Subtitle.TLabel",
        ).grid(row=3, column=0, sticky="w")

    def build_transactions_tab(self):
        self.transactions_tab.columnconfigure(0, weight=1)
        self.transactions_tab.rowconfigure(2, weight=1)

        toolbar = ttk.Frame(self.transactions_tab)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        ttk.Button(toolbar, text="Add transaction", command=self.add_transaction).pack(
            side="left"
        )
        ttk.Button(toolbar, text="Edit selected", command=self.edit_transaction).pack(
            side="left", padx=8
        )
        ttk.Button(
            toolbar,
            text="Delete selected",
            command=self.delete_transaction,
        ).pack(side="left")
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side="right")

        self.empty_label = ttk.Label(
            self.transactions_tab,
            text="No transactions yet. Add your first income or expense.",
            style="Subtitle.TLabel",
        )
        self.empty_label.grid(row=1, column=0, sticky="w", pady=(0, 8))

        table_frame = ttk.Frame(self.transactions_tab)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("id", "type", "amount", "description", "account", "date")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Type")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("description", text="Description")
        self.tree.heading("account", text="Account")
        self.tree.heading("date", text="Date")
        self.tree.column("id", width=55, minwidth=45, anchor="center", stretch=False)
        self.tree.column("type", width=100, minwidth=90, anchor="center", stretch=False)
        self.tree.column("amount", width=130, minwidth=100, anchor="e", stretch=False)
        self.tree.column("description", width=260, minwidth=150)
        self.tree.column("account", width=150, minwidth=110)
        self.tree.column(
            "date", width=165, minwidth=145, anchor="center", stretch=False
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", lambda _event: self.edit_transaction())

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def build_accounts_tab(self):
        self.accounts_tab.columnconfigure(0, weight=1)
        self.accounts_tab.rowconfigure(2, weight=1)

        toolbar = ttk.Frame(self.accounts_tab)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        ttk.Button(toolbar, text="Add account", command=self.add_account).pack(
            side="left"
        )
        ttk.Button(toolbar, text="Edit selected", command=self.edit_account).pack(
            side="left", padx=8
        )
        ttk.Button(
            toolbar,
            text="Delete selected",
            command=self.delete_selected_account,
        ).pack(side="left")
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side="right")

        self.accounts_empty_label = ttk.Label(
            self.accounts_tab,
            text="No accounts yet. Add where you currently keep your money.",
            style="Subtitle.TLabel",
        )
        self.accounts_empty_label.grid(row=1, column=0, sticky="w", pady=(0, 8))

        table_frame = ttk.Frame(self.accounts_tab)
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("id", "name", "balance")
        self.accounts_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.accounts_tree.heading("id", text="ID")
        self.accounts_tree.heading("name", text="Account")
        self.accounts_tree.heading("balance", text="Balance")
        self.accounts_tree.column(
            "id", width=70, minwidth=55, anchor="center", stretch=False
        )
        self.accounts_tree.column("name", width=420, minwidth=180)
        self.accounts_tree.column(
            "balance", width=180, minwidth=120, anchor="e", stretch=False
        )
        self.accounts_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.accounts_tree.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.accounts_tree.configure(yscrollcommand=scrollbar.set)
        self.accounts_tree.bind(
            "<Double-1>",
            lambda _event: self.edit_account(),
        )

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        transactions = get_transactions(self.connection)
        for (
            transaction_id,
            transaction_type,
            amount,
            description,
            date,
            _account_id,
            account_name,
        ) in transactions:
            sign = "+" if transaction_type == "income" else "−"
            self.tree.insert(
                "",
                "end",
                iid=str(transaction_id),
                values=(
                    transaction_id,
                    transaction_type.title(),
                    f"{sign}¥{amount:,}",
                    description,
                    account_name or NO_ACCOUNT_LABEL,
                    date,
                ),
            )

        if transactions:
            self.empty_label.grid_remove()
        else:
            self.empty_label.grid()

        for item in self.accounts_tree.get_children():
            self.accounts_tree.delete(item)

        accounts = get_accounts(self.connection)
        for account_id, name, balance in accounts:
            sign = "−" if balance < 0 else ""
            self.accounts_tree.insert(
                "",
                "end",
                iid=str(account_id),
                values=(
                    account_id,
                    name,
                    f"{sign}¥{abs(balance):,}",
                ),
            )

        if accounts:
            self.accounts_empty_label.grid_remove()
        else:
            self.accounts_empty_label.grid()

        total_balance = sum(balance for _, _, balance in accounts)
        total_sign = "−" if total_balance < 0 else ""
        self.balance_var.set(f"{total_sign}¥{abs(total_balance):,}")
        self.status_var.set(
            f"{len(transactions)} transaction(s) · {len(accounts)} account(s)"
        )

    def add_account(self):
        dialog = AccountDialog(
            self.root,
            "Add account",
            on_save=lambda name, balance: insert_account(
                self.connection,
                name,
                balance,
            ),
        )
        if dialog.result is None:
            return

        self.refresh()
        self.status_var.set("Account added")

    def selected_account_id(self):
        selection = self.accounts_tree.selection()
        if not selection:
            messagebox.showinfo(
                "Select an account",
                "Select an account from the list first.",
                parent=self.root,
            )
            return None
        return int(selection[0])

    def edit_account(self):
        account_id = self.selected_account_id()
        if account_id is None:
            return

        account = get_account_by_id(self.connection, account_id)
        if account is None:
            messagebox.showerror(
                "Account unavailable",
                "That account no longer exists. The list will be refreshed.",
                parent=self.root,
            )
            self.refresh()
            return

        _, name, balance = account

        def save_account(updated_name, updated_balance):
            update_account_field(
                self.connection,
                account_id,
                "name",
                updated_name,
            )
            update_account_field(
                self.connection,
                account_id,
                "balance",
                updated_balance,
            )

        dialog = AccountDialog(
            self.root,
            "Edit account",
            (name, balance),
            on_save=save_account,
        )
        if dialog.result is None:
            return

        self.refresh()
        self.status_var.set("Account updated")

    def delete_selected_account(self):
        account_id = self.selected_account_id()
        if account_id is None:
            return

        account = get_account_by_id(self.connection, account_id)
        if account is None:
            self.refresh()
            return

        _, name, balance = account
        sign = "−" if balance < 0 else ""
        confirmed = messagebox.askyesno(
            "Delete account",
            f"Permanently delete {name} with a balance of " f"{sign}¥{abs(balance):,}?",
            parent=self.root,
        )
        if not confirmed:
            return

        delete_account_by_id(self.connection, account_id)
        self.refresh()
        self.status_var.set("Account deleted")

    def selected_transaction_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(
                "Select a transaction",
                "Select a transaction from the list first.",
                parent=self.root,
            )
            return None
        return int(selection[0])

    def add_transaction(self):
        account_options = build_account_options(get_accounts(self.connection))
        dialog = TransactionDialog(
            self.root,
            "Add transaction",
            account_options=account_options,
        )
        if dialog.result is None:
            return

        transaction_type, amount, description, date, account_id = dialog.result
        try:
            insert_transaction(
                self.connection,
                transaction_type,
                amount,
                description,
                date,
                account_id,
            )
        except sqlite3.IntegrityError as error:
            messagebox.showerror(
                "Account unavailable",
                str(error),
                parent=self.root,
            )
            return
        self.refresh()
        self.status_var.set("Transaction added")

    def edit_transaction(self):
        transaction_id = self.selected_transaction_id()
        if transaction_id is None:
            return

        transaction = get_transaction_by_id(self.connection, transaction_id)
        if transaction is None:
            messagebox.showerror(
                "Transaction unavailable",
                "That transaction no longer exists. The list will be refreshed.",
                parent=self.root,
            )
            self.refresh()
            return

        (
            _,
            transaction_type,
            amount,
            description,
            date,
            account_id,
            _,
        ) = transaction
        account_options = build_account_options(get_accounts(self.connection))
        dialog = TransactionDialog(
            self.root,
            "Edit transaction",
            (transaction_type, amount, description, date, account_id),
            account_options,
        )
        if dialog.result is None:
            return

        (
            updated_type,
            updated_amount,
            updated_description,
            updated_date,
            updated_account_id,
        ) = dialog.result
        try:
            update_transaction(
                self.connection,
                transaction_id,
                updated_type,
                updated_amount,
                updated_description,
                updated_date,
                updated_account_id,
            )
        except sqlite3.IntegrityError as error:
            messagebox.showerror(
                "Account unavailable",
                str(error),
                parent=self.root,
            )
            return

        self.refresh()
        self.status_var.set("Transaction updated")

    def delete_transaction(self):
        transaction_id = self.selected_transaction_id()
        if transaction_id is None:
            return

        transaction = get_transaction_by_id(self.connection, transaction_id)
        if transaction is None:
            self.refresh()
            return

        _, transaction_type, amount, description, _, _, _ = transaction
        confirmed = messagebox.askyesno(
            "Delete transaction",
            f"Delete {transaction_type} “{description}” for ¥{amount:,}?",
            parent=self.root,
        )
        if not confirmed:
            return

        delete_transaction_by_id(self.connection, transaction_id)
        self.refresh()
        self.status_var.set("Transaction deleted")

    def close(self):
        self.connection.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    connection = connect_database()
    BalanceManagerApp(root, connection)
    root.mainloop()


if __name__ == "__main__":
    main()
