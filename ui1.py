import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import db1  # <-- imported your DB functions
from datetime import datetime

def create_bill(items):
  """
  items = list of tuples(item_id, quantity, price)
  """
  
  conn = sqlite3.connect("pos.db")
  cursor = conn.cursor()
  
  # Step1: Insert bill header
  date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  total = sum(qty * price for (_, qty, price) in items)
  cursor.execute("INSERT INTO bills(date, total) VALUES (?, ?)", (date, total))
  bill_id = cursor.lastrowid # get generated bill ID
  
  # Step 2: Insert each item
  for item_id, qty, price in items:
    cursor.execute(
      "INSERT INTO bill_items(bill_id, item_id, quantity, price) VALUES(?, ?, ?, ?)",
      (bill_id, item_id, qty, price)
    )
    
  conn.commit()
  conn.close()
  return bill_id
  

def show_items():
    data = db1.get_items()
    messagebox.showinfo("Items", str(data))
  
def open_items_table():
  win = tk.Toplevel(root)
  win.title("Items List")
  win.geometry("600x400-50-50")
  
  # Create Treeview
  columns = ("name", "price")
  tree = ttk.Treeview(win, columns=columns, show="headings")
  scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
  tree.configure(yscrollcommand=scrollbar.set)
  
  scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
  tree.pack(fill=tk.BOTH, expand=True)
                            
  
  tree.heading("name", text="Item Name")
  tree.heading("price", text="Price")
  
  tree.column("name", width=200)
  tree.column("price", width=100)
  
  tree.pack(fill=tk.BOTH, expand=True)
  
  # Fetch items from DB
  data = db1.get_items()
  
  # Insert items into table
  for item in data:
    tree.insert("", tk.END, values=item)
    

root = tk.Tk()

try:
  from ctypes import windll
  windll.shcore.SetProcessDpiAwareness(1)
except:
  pass

root.title("Mini POS")
root.geometry("600x400-50-50")

def open_add_window():
  win = tk.Toplevel(root)
  try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
  except:
    pass
  win.title("Add Item")
  win.geometry("600x400-50-50")
  
  tk.Label(win, text="Item Name").pack()
  name_entry = tk.Entry(win)
  name_entry.pack()
  
  tk.Label(win, text="Item Price").pack()
  price_entry = tk.Entry(win)
  price_entry.pack()
  
  def save_item():
    name = name_entry.get()
    price = price_entry.get()
    
    if name.strip() == "" or price.strip() == "":
      messagebox.showwarning("Error", "Please fill all fields.")
      return 
  
    try:
      price = float(price)
    except:
      messagebox.showwarning("Error", "Price must be a number.")
      return

    db1.add_item(name, price)
    messagebox.showinfo("Success", "Item added!")
    win.destroy()
  tk.Button(win, text="Save Item", comman=save_item).pack(pady=10)
  
button = tk.Button(root, text="Show Items", command=show_items)
button.pack(pady=20)

add_btn = tk.Button(root, text="Add Item", command=lambda: open_add_window())
add_btn.pack(pady=10)

table_btn = tk.Button(root, text="Show Items Table", command=open_items_table)
table_btn.pack(pady=10)

root.mainloop()