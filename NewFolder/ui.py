import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import db
from decimal import Decimal, InvalidOperation

# Utility: set DPI awareness on Windows (optional)
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

root = tk.Tk()
root.title("Mini POS")
root.geometry("720x480")

# Global cart: list of (item_id, name, qty, price)
cart = []

# --- UI: Items Treeview ---
items_frame = tk.Frame(root)
items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

cols = ("id", "name", "price", "stock")
tree = ttk.Treeview(items_frame, columns=cols, show="headings", selectmode="browse")
for c, text, w in zip(cols, ("ID", "Name", "Price", "Stock"), (60, 300, 100, 80)):
    tree.heading(c, text=text)
    tree.column(c, width=w, anchor=tk.CENTER if c == "id" else tk.W)

vsb = ttk.Scrollbar(items_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
vsb.pack(side=tk.RIGHT, fill=tk.Y)
tree.pack(fill=tk.BOTH, expand=True)

def refresh_items():
    for r in tree.get_children():
        tree.delete(r)
    for row in db.get_items():
        item_id, name, price, stock = row
        tree.insert("", tk.END, values=(item_id, name, f"{price:.2f}", stock))

refresh_items()

# --- Buttons ---
btn_frame = tk.Frame(root)
btn_frame.pack(fill=tk.X, padx=10, pady=6)

def open_add_item_window():
    win = tk.Toplevel(root)
    win.title("Add Item")
    win.geometry("360x220")

    tk.Label(win, text="Name").pack(anchor=tk.W, padx=8, pady=(8,0))
    name_e = tk.Entry(win)
    name_e.pack(fill=tk.X, padx=8)

    tk.Label(win, text="Price").pack(anchor=tk.W, padx=8, pady=(8,0))
    price_e = tk.Entry(win)
    price_e.pack(fill=tk.X, padx=8)

    tk.Label(win, text="Stock (optional)").pack(anchor=tk.W, padx=8, pady=(8,0))
    stock_e = tk.Entry(win)
    stock_e.insert(0, "0")
    stock_e.pack(fill=tk.X, padx=8)

    def save():
        name = name_e.get().strip()
        price_s = price_e.get().strip()
        stock_s = stock_e.get().strip()
        if not name or not price_s:
            messagebox.showwarning("Error", "Name and price required")
            return
        try:
            price = float(Decimal(price_s))
            stock = int(stock_s) if stock_s else 0
        except (InvalidOperation, ValueError):
            messagebox.showwarning("Error", "Price must be a number and stock must be integer")
            return
        db.add_item(name, price, stock)
        messagebox.showinfo("OK", "Item added")
        win.destroy()
        refresh_items()

    tk.Button(win, text="Save Item", command=save).pack(pady=12)

tk.Button(btn_frame, text="Add Item", command=open_add_item_window).pack(side=tk.LEFT, padx=6)
tk.Button(btn_frame, text="Refresh Items", command=refresh_items).pack(side=tk.LEFT, padx=6)

def add_selected_to_cart():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Please select an item first")
        return
    values = tree.item(sel[0], "values")
    item_id = int(values[0])
    name = values[1]
    price = float(values[2])
    # ask qty
    qty = simpledialog.askinteger("Quantity", f"Enter quantity for '{name}':", parent=root, minvalue=1)
    if not qty:
        return
    # append to cart (merge if same item exists)
    for i, (iid, nm, q, p) in enumerate(cart):
        if iid == item_id:
            cart[i] = (iid, nm, q + qty, p)
            break
    else:
        cart.append((item_id, name, qty, price))
    messagebox.showinfo("Cart", f"Added {qty} x {name} to cart")

tk.Button(btn_frame, text="Add to Cart", command=add_selected_to_cart).pack(side=tk.LEFT, padx=6)

def open_cart_window():
    win = tk.Toplevel(root)
    win.title("Cart")
    win.geometry("520x360")

    cart_cols = ("item_id", "name", "qty", "price", "line_total")
    cart_tree = ttk.Treeview(win, columns=cart_cols, show="headings", selectmode="browse")
    for c, txt, w in zip(cart_cols, ("ID","Name","Qty","Price","Total"), (60,240,60,80,80)):
        cart_tree.heading(c, text=txt)
        cart_tree.column(c, width=w, anchor=tk.W)

    vs = ttk.Scrollbar(win, orient="vertical", command=cart_tree.yview)
    cart_tree.configure(yscrollcommand=vs.set)
    vs.pack(side=tk.RIGHT, fill=tk.Y)
    cart_tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def refresh_cart_view():
        for r in cart_tree.get_children():
            cart_tree.delete(r)
        for iid, name, qty, price in cart:
            cart_tree.insert("", tk.END, values=(iid, name, qty, f"{price:.2f}", f"{price*qty:.2f}"))
        total = sum(qty * price for _, _, qty, price in cart)
        total_label.config(text=f"Total: {total:.2f}")

    # Bottom controls
    bottom = tk.Frame(win)
    bottom.pack(fill=tk.X, padx=6, pady=6)
    total_label = tk.Label(bottom, text="Total: 0.00")
    total_label.pack(side=tk.LEFT)

    def remove_selected():
        sel = cart_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select cart row to remove")
            return
        vals = cart_tree.item(sel[0], "values")
        item_id = int(vals[0])
        # remove from cart list
        for i, (iid, nm, q, p) in enumerate(cart):
            if iid == item_id:
                cart.pop(i)
                break
        refresh_cart_view()

    def checkout():
        if not cart:
            messagebox.showwarning("Cart empty", "Add items to cart first")
            return
        # prepare items for db.create_bill -> list of (item_id, qty)
        items_for_db = [(iid, qty) for iid, _, qty, _ in cart]
        try:
            bill_id = db.create_bill(items_for_db)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create bill: {e}")
            return
        total = sum(qty * price for _, _, qty, price in cart)
        receipt_lines = [f"Bill ID: {bill_id}", "-"*30]
        for iid, name, qty, price in cart:
            receipt_lines.append(f"{name} x{qty} @ {price:.2f} = {price*qty:.2f}")
        receipt_lines.append("-"*30)
        receipt_lines.append(f"TOTAL: {total:.2f}")
        messagebox.showinfo("Receipt", "\n".join(receipt_lines))
        cart.clear()
        refresh_cart_view()

    tk.Button(bottom, text="Remove Selected", command=remove_selected).pack(side=tk.RIGHT, padx=6)
    tk.Button(bottom, text="Checkout", command=checkout).pack(side=tk.RIGHT, padx=6)

    refresh_cart_view()

tk.Button(btn_frame, text="Open Cart", command=open_cart_window).pack(side=tk.LEFT, padx=6)

# Optional: show single item details on double-click
def on_item_double_click(event):
    sel = tree.selection()
    if not sel:
        return
    v = tree.item(sel[0], "values")
    messagebox.showinfo("Item", f"ID: {v[0]}\nName: {v[1]}\nPrice: {v[2]}\nStock: {v[3]}")

tree.bind("<Double-1>", on_item_double_click)

root.mainloop()
