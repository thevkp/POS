import sqlite3

conn = sqlite3.connect("company.db")
cur = conn.cursor()

# Create main employees table
cur.execute("""
  CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first TEXT NOT NULL,
    last TEXT NOT NULL,
    pay REAL NOT NULL,
    join_year INTEGER,
    last_raise_year INTEGER DEFAULT NULL
  )            
""")

# salary_logs table
cur.execute("""
  CREATE TABLE IF NOT EXISTS salary_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,
    old_pay REAL NOT NULL,
    new_pay REAL NOT NULL,
    change_time TEXT,
    FOREIGN KEY (emp_id) REFERENCES employees (id)
  )
""")

  
conn.commit()
conn.close()

print("Database + Tables created successfully.")