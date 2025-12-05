# from functions import add_employee, get_all_employees, update_pay, give_raise
from functions import *

print("\n=== COMPANY EMPLOYEE MANAGER ===\n")


while True:
  print("""
    1. Add Employee
    2. Show All Employees
    3. Update Pay
    4. Give Raise to All
    5. Update Salary
    6. Get salary history
    7. Exit  
  """)
  
  choice = input("Enter choice: ").strip()
  
  if choice == "1":
        first = input("First Name: ")
        last = input("Last Name: ")
        pay = float(input("Pay: "))
        join_year = int(input("Joining Year: "))
        add_employee(first, last, pay, join_year)
  elif choice == "2":
      rows = get_all_employees()
      print("\n----- Employees -----")
      for emp in rows:
          print(emp)
      print("---------------------\n")
  elif choice == "3":
      emp_id = int(input("Employee ID: "))
      new_pay = float(input("New Pay: "))
      update_pay(emp_id, new_pay)
  elif choice == "4":
      percent = float(input("Raise percent (0.10 for 10%): "))
      give_raise(percent)
  elif choice == "5":
    emp_id = int(input("Enter employee id: "))
    new_sal = int(input("Enter new salary: "))
    update_salary(emp_id, new_sal)
  elif choice == "6":
    emp_id = int(input("Enter employee id: "))
    print(get_salary_history(emp_id))
  elif choice == "7":
      print("Goodbye!")
      break
  else:
      print("Invalid choice.")
      
      
# delete_all_employees()

print_logs_table()
print()
print_sorted_logs()