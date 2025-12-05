import sqlite3
from datetime import datetime, timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))


DB = "company.db"


def connect():
  return sqlite3.connect(DB)



# INSERT
# ---------- INSERT ----------
def add_employee(first, last, pay, join_year):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO employees (first, last, pay, join_year, last_raise_year)
        VALUES (?, ?, ?, ?, NULL)
        """,
        (first, last, pay, join_year)
    )
    
    emp_id = cur.lastrowid # ID of the newly added employee
  
    cur.execute("""
      INSERT INTO salary_logs (emp_id, old_pay, new_pay, change_time) 
      VALUES (?, ?, ?, ?)""", (emp_id, 0, pay, datetime.now(IST))
    )
    
    
    conn.commit()
    conn.close()
    print("✔ Employee added.")
  
  
  
# Fetch all
def get_all_employees():
  conn = connect()
  cur = conn.cursor()
  cur.execute("SELECT * FROM employees")
  rows = cur.fetchall()
  conn.close()
  return rows



# UPDATE PAY
def update_pay(emp_id, new_pay):
  conn = connect()
  cur = conn.cursor()
  cur.execute(
    "UPDATE employees SET pay = ? WHERE id = ?",
    (new_pay, emp_id)
  )
  
  conn.commit()
  conn.close()
  print("Salary updated.")
  
  
# GIVE RAISE
def give_raise(percent):
  conn = connect()
  cur = conn.cursor()
  cur.execute(
    "UPDATE employees SET pay = pay * (1 + ?)",
    (percent,)
  )
  
  conn.commit()
  conn.close()


def update_salary(emp_id, new_salary):
  conn = connect()
  cur = conn.cursor()
  
  # 1. Fetch current salary
  cur.execute("SELECT pay FROM employees WHERE id=?", (emp_id,))
  row = cur.fetchone()
  
  if not row:
    print("Employee not found.")
    conn.close()
    return

  old_salary = row[0]
  
  
  # 2. Update salary
  cur.execute("UPDATE employees SET pay=? WHERE id=?", (new_salary, emp_id))
  
  # 3. Add log entry
  cur.execute("""
    INSERT INTO salary_logs (emp_id, old_pay, new_pay, change_time)
    VALUES (?, ?, ?, ?)               
 """, (emp_id, old_salary, new_salary, datetime.now(IST)))
  
  conn.commit()
  conn.close()
  print("Salary updated & log stored.")
  
  
def get_salary_history(emp_id):
  conn = connect()
  cur = conn.cursor()
  
  cur.execute("""
    SELECT id, old_pay, new_pay, change_time FROM salary_logs
    WHERE emp_id=? ORDER BY change_time DESC
  """, (emp_id,))
  
  logs = cur.fetchall()
  conn.close()
  return logs


# Convert everythin to aware datetimes(with IST)
def parse_timestamp(ts):
  dt = datetime.fromisoformat(ts)
  if dt.tzinfo is None: # naive->make aware in IST
    dt = dt.replace(tzinfo=IST)
  else: # aware->convert to IST
    dt = dt.astimezone(IST)
  return dt

def get_all_logs():
  conn = connect()
  cur = conn.cursor()
  
  cur.execute("""
  SELECT emp_id, old_pay, new_pay, change_time
  FROM salary_logs ORDER BY change_time
  """)
  
  rows = cur.fetchall()
  conn.close()
  return rows

def print_logs_table(desc=False):
  logs = get_all_logs()
  # logs = logs[::-1]
  
  if not logs:
    print("No logs to display.")
    return 
  
  logs_sorted = sorted(logs, key=lambda x: parse_timestamp(x[3]), reverse=desc)
  
  # Header 
  print(f"{'Emp ID': <8} {'Old Pay': <10} {'New Pay': <10} {'Change Time': <25}")
  print("-" * 60)
  
  for emp_id, old, new, ts in logs:
    # Convert timestamp string
    try:
      dt = datetime.fromisoformat(ts)
      ts_clean = parse_timestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except:
      ts_clean = ts # fallback
      
    print(f"{emp_id:<8} {old:<10} {new:<10} {ts_clean:<25}")
    
def print_sorted_logs(desc=False):
    logs = get_all_logs()

    if not logs:
        print("No logs to display.")
        return

    # Sort logs
    logs = sorted(logs, key=lambda x: parse_timestamp(x[3]), reverse=desc)

    # Print table header
    print(f"{'Emp ID':<8} {'Old Pay':<10} {'New Pay':<10} {'Change Time':<25}")
    print("-" * 60)

    # Print each row
    for emp_id, old, new, ts in logs:
      # dt = datetime.fromisoformat(ts)
      ts_clean = parse_timestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
      print(f"{emp_id:<8} {old:<10} {new:<10} {ts_clean:<25}")





# Just to fix the past mistakes
def delete_all_employees():
  conn = connect()
  cur = conn.cursor()
  cur.execute("DELETE FROM employees")
  cur.execute("DELETE FROM salary_logs")
  cur.execute("DELETE FROM sqlite_sequence WHERE name='employees'")  # reset AUTOINCREMENT
  conn.commit()
  conn.close()
