import sqlite3
from datetime import datetime


conn = sqlite3.connect('emp5.db')

cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS emp5(
  id INTEGER PRIMARY KEY,
  first TEXT NOT NULL,
  last TEXT NOT NULL,
  pay REAL
  )""")

try:
  cur.execute("""
    ALTER TABLE emp5
    ADD COLUMN last_raise_year INTEGER DEFAULT NULL  
""")
except sqlite3.OperationalError:
  # Column already exists -> ignore the error
  pass

def add_employees(id, first, last, pay):
  cur.execute("INSERT OR IGNORE INTO emp5(id, first, last, pay) VALUES(?, ?, ?, ?)", (id, first, last, pay))
  conn.commit()
  
def get_all_employees():
  cur.execute("SELECT * FROM emp5")
  return cur.fetchall()

def get_employee_by_lastname(last):
  cur.execute("SELECT * FROM emp5 WHERE last=?", (last,))
  return cur.fetchone()

def update_pay(emp_id, new_pay):
  cur.execute("UPDATE emp5 SET pay=? WHERE id=?", (new_pay, emp_id))
  conn.commit()
  
  
def delete_employee(emp_id):
  cur.execute("DELETE FROM emp5 WHERE id=?", (emp_id,))
  conn.commit()
  
def give_raise(percent):
  current_year = datetime.now().year
  
  # Only employees who haven't received a raise this year
  cur.execute("""
    UPDATE emp5
    SET pay = pay * ?, last_raise_year = ?
    WHERE last_raise_year IS NULL OR last_raise_year < ?
  """, (1 + percent, current_year, current_year))
  
  conn.commit()
  
# created a mess and salaries touched moon
# def give_raise_to_all(percent):
#   cur.execute("UPDATE emp5 SET pay = pay * ?", (1 + percent,))
#   conn.commit()
  
  
# for i in range(5):
#   id = int(input(f"Enter employee{i + 1} id: "))
#   first = input(f"Enter first name: ")
#   last = input(f"Enter last name: ")
#   pay = int(input(f"Enter pay: "))
  
#   add_employees(id, first, last, pay)
  
# add_employees(1, 'Vishal', 'Kumar', 70000)

cur.execute("UPDATE emp5 SET first=?, last=? WHERE id=?", ('Vishal', 'Kumar', 1))
cur.execute("UPDATE emp5 SET first=?, last=? WHERE id=?", ('Archana', 'Puran', 5))
conn.commit()
# give_raise_to_all(0)
give_raise(0.10)


# print(get_all_employees())
cur.execute("SELECT * FROM emp5")
rows = cur.fetchall()
for emp in rows:
  print(emp)
  

# Bringing salaries in original state
cur.execute("SELECT * FROM emp5")
rows = cur.fetchall()
for emp in rows:
  emp_id = emp[0]
  cur.execute("UPDATE emp5 SET pay=? WHERE id=?", (60000, emp_id))

conn.commit()

# cleaner way
cur.execute("UPDATE emp5 SET pay = 80000")
conn.commit()

  
# print(cur.fetchone())

conn.close()