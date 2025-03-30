import sqlite3
from typing import Any, Optional

import pandas as pd
from pathlib import Path

database_path = Path(__file__).parent / "finance_tracker.db"

# Database setup
def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    # Create tables if they don't exist
    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        amount REAL,
        category TEXT,
        description TEXT,
        transaction_type TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        type TEXT
    )
    """)

    # Add default categories if none exist
    c.execute("SELECT COUNT(*) FROM categories")
    if c.fetchone()[0] == 0:
        default_categories: list[tuple[str, str]] = [
            ("Groceries", "expense"),
            ("Rent", "expense"),
            ("Utilities", "expense"),
            ("Transportation", "expense"),
            ("Entertainment", "expense"),
            ("Dining Out", "expense"),
            ("Shopping", "expense"),
            ("Healthcare", "expense"),
            ("Salary", "income"),
            ("Bonus", "income"),
            ("Investment", "income"),
            ("Gifts", "income"),
        ]
        c.executemany(
            "INSERT INTO categories (name, type) VALUES (?, ?)", default_categories
        )

    conn.commit()
    return conn


# Helper functions
def add_transaction(
    date: str, amount: float, category: str, description: str, transaction_type: str
) -> None:
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute(
        "INSERT INTO transactions (date, amount, category, description, transaction_type) VALUES (?, ?, ?, ?, ?)",
        (date, amount, category, description, transaction_type),
    )
    conn.commit()
    conn.close()


def get_transaction_by_id(transaction_id: int) -> Optional[dict[str, Any]]:
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    transaction = c.fetchone()
    conn.close()
    if transaction:
        return {
            "id": transaction[0],
            "date": transaction[1],
            "amount": transaction[2],
            "category": transaction[3],
            "description": transaction[4],
            "transaction_type": transaction[5],
        }
    return None


def update_transaction(
    transaction_id: int,
    date: str,
    amount: float,
    category: str,
    description: str,
    transaction_type: str,
) -> None:
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute(
        "UPDATE transactions SET date = ?, amount = ?, category = ?, description = ?, transaction_type = ? WHERE id = ?",
        (date, amount, category, description, transaction_type, transaction_id),
    )
    conn.commit()
    conn.close()


def delete_transaction(transaction_id: int) -> None:
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()


def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
) -> pd.DataFrame:
    conn = sqlite3.connect(database_path)
    query = "SELECT * FROM transactions WHERE 1=1"
    params: list[str] = []

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if transaction_type and transaction_type != "All":
        query += " AND transaction_type = ?"
        params.append(transaction_type)

    query += " ORDER BY date DESC"

    df = pd.read_sql_query(query, conn, params=tuple(params))
    conn.close()
    return df


def get_categories(type: Optional[str] = None) -> list[str]:
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    if type:
        c.execute("SELECT name FROM categories WHERE type = ?", (type,))
    else:
        c.execute("SELECT name FROM categories")

    categories = [row[0] for row in c.fetchall()]
    conn.close()
    return categories


def add_category(name: str, type: str) -> bool:
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO categories (name, type) VALUES (?, ?)", (name, type))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success
