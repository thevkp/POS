import sqlite3

# --- DATABASE INITIAL SETUP ---
def init_db():
  conn = sqlite3.connect("pos.db")
  cursor = conn.cursor()
  
  cursor.execute("""
    CREATE TABLE IF NOT EXISTS items(
      id INTEGERE PRIMARY KEY,
      name TEXT,
      price REAL
    )
    """)
  
  # Insert sample data (Only if empty)
  cursor.execute("SELECT COUNT(*) FROM items")
  count = cursor.fetchone()[0]
  
  if count == 0:
    cursor.execute("INSERT INTO items(name, price) VALUES ('Chocoloate', 10)")
    cursor.execute("INSERT INTO items(name, price) VALUES ('Chips', 20)")
    
  
  conn.commit()
  conn.close()
  
  
  
# --- REUSABLE FUNCTIONS ---
def get_connection():
  return sqlite3.connect("pos.db")

def add_item(name, price):
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("INSERT INTO items(name, price) VALUES(?, ?)", (name, price))
  conn.commit()
  conn.close()


def get_items():
  conn = get_connection()
  cursor = conn.cursor()
  cursor.execute("SELECT name, price FROM items")
  data = cursor.fetchall()
  conn.close()
  return data