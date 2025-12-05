import sqlite3

conn = sqlite3.connect('employees.db')

cur = conn.cursor()


cur.execute("""CREATE TABLE IF NOT EXISTS employees(
  id INTEGER PRIMARY KEY,
  first TEXT NOT NULL,
  last TEXT NOT NULL,
  pay REAL
  )
  """)

cur.execute("INSERT OR IGNORE INTO employees VALUES (1, 'Vishal', 'Patel', 50000)")
cur.execute("INSERT OR IGNORE INTO employees VALUES (2, 'Rohan', 'Verma', 60000)")

conn.commit()


cur.execute("SELECT * FROM employees")
rows = cur.fetchall()
# print(rows)

for emp in rows:
  print(emp)
  

def add_employees(first, last, pay):
  cur.execute("INSERT INTO employees(first, last, pay) VALUES (?, ?, ?)", (first, last, pay))
  conn.commit()
  
def get_all_employees():
  cur.execute("SELECT * FROM employees")
  return cur.fetchall()

def get_employee_by_lastname(last):
  cur.execute("SELECT * FROM employees WHERE last=?", (last,))
  return cur.fetchone()

def update_pay(emp_id, new_pay):
  cur.execute("UPDATE employees SET pay=? where id=?", (new_pay, emp_id))
  conn.commit()
  
def delete_employee(emp_id):
  cur.execute("DELETE FROM employees WHERE id=?", (emp_id,))
  conn.commit()
  
delete_employee(8)
print("Here after deletion")

update_pay(7, 51000)
for emp in rows:
  print(emp)
  


conn.close()