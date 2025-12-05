import sqlite3
from datetime import datetime
from typing import List, Tuple

DB_FILE = "pos.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS items(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      price REAL NOT NULL,
      stock INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills(
      bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT,
      total REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bill_items(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      bill_id INTEGER,
      item_id INTEGER,
      quantity INTEGER,
      price REAL,
      FOREIGN KEY(bill_id) REFERENCES bills(bill_id),
      FOREIGN KEY(item_id) REFERENCES items(id)
    )
    """)

    conn.commit()
    conn.close()

# initialize DB at import time (safe: creates tables only)
init_db()

# --- Item functions ---
def add_item(name: str, price: float, stock: int = 0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO items(name, price, stock) VALUES (?, ?, ?)",
                (name, price, stock))
    conn.commit()
    conn.close()

def get_items() -> List[Tuple]:
    """Return list of (id, name, price, stock)"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM items ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_item_by_id(item_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM items WHERE id = ?", (item_id,))
    row = cur.fetchone()
    conn.close()
    return row

def update_stock(item_id: int, delta: int):
    """Adjust stock by delta (can be negative)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE items SET stock = stock + ? WHERE id = ?", (delta, item_id))
    conn.commit()
    conn.close()

# --- Billing ---
def create_bill(items: List[Tuple[int, int]]):
    """
    items: list of tuples (item_id, quantity)
    Returns bill_id
    """
    conn = get_connection()
    cur = conn.cursor()

    # Calculate total and snapshot price
    total = 0.0
    item_snapshots = []
    for item_id, qty in items:
        cur.execute("SELECT price FROM items WHERE id = ?", (item_id,))
        row = cur.fetchone()
        if row is None:
            conn.close()
            raise ValueError(f"Item id {item_id} not found")
        price = float(row[0])
        total += price * qty
        item_snapshots.append((item_id, qty, price))

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO bills(date, total) VALUES(?, ?)", (date, total))
    bill_id = cur.lastrowid

    for item_id, qty, price in item_snapshots:
        cur.execute(
            "INSERT INTO bill_items(bill_id, item_id, quantity, price) VALUES (?, ?, ?, ?)",
            (bill_id, item_id, qty, price)
        )
        # Optionally reduce stock:
        # cur.execute("UPDATE items SET stock = stock - ? WHERE id = ?", (qty, item_id))

    conn.commit()
    conn.close()
    return bill_id

def get_bill(bill_id: int):
    """Return bill header and items"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT bill_id, date, total FROM bills WHERE bill_id = ?", (bill_id,))
    header = cur.fetchone()
    cur.execute("SELECT item_id, quantity, price FROM bill_items WHERE bill_id = ?", (bill_id,))
    items = cur.fetchall()
    conn.close()
    return header, items
