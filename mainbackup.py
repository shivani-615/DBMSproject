import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# --- Database Setup ---
def create_db():
    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Customer (
            Cust_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Address TEXT,
            PhoneNumber TEXT UNIQUE
        )
        ''')
        conn.commit()
        conn.close()
        print("Database and table ready!")
    except Exception as e:
        print("Error while creating database:", e)

create_db()

# --- Function to Add Customer ---
def add_customer():
    name = name_entry.get()
    address = address_entry.get()
    phone = phone_entry.get()

    if not name or not phone:
        messagebox.showwarning("Input Error", "Name and Phone are required!")
        return

    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Customer (Name, Address, PhoneNumber) VALUES (?, ?, ?)",
                       (name, address, phone))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer added successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Phone number already exists!")

    name_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)

# --- Function to View Customers ---
def view_customers():
    # Create new window
    
    view_win = tk.Toplevel(root)
    view_win.title("View All Customers")
    view_win.geometry("500x300")

    # Treeview (table)
    tree = ttk.Treeview(view_win, columns=("ID", "Name", "Address", "Phone"), show='headings')
    tree.heading("ID", text="Customer ID")
    tree.heading("Name", text="Name")
    tree.heading("Address", text="Address")
    tree.heading("Phone", text="Phone Number")
    tree.column("ID", width=80)
    tree.column("Name", width=120)
    tree.column("Address", width=150)
    tree.column("Phone", width=100)
    tree.pack(fill=tk.BOTH, expand=True)

    # Fetch data from DB
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customer")
    rows = cursor.fetchall()
    conn.close()

    # Insert data into Treeview
    for row in rows:
        tree.insert("", tk.END, values=row)

# --- GUI Window ---
root = tk.Tk()
root.title("Pharmacy Management System")
root.geometry("400x300")

tk.Label(root, text="Customer Name").grid(row=0, column=0, padx=10, pady=10)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

tk.Label(root, text="Address").grid(row=1, column=0, padx=10, pady=10)
address_entry = tk.Entry(root)
address_entry.grid(row=1, column=1)

tk.Label(root, text="Phone Number").grid(row=2, column=0, padx=10, pady=10)
phone_entry = tk.Entry(root)
phone_entry.grid(row=2, column=1)

# Buttons
tk.Button(root, text="Add Customer", command=add_customer, bg="green", fg="white").grid(row=3, column=0, columnspan=2, pady=10)
tk.Button(root, text="View Customers", command=view_customers, bg="blue", fg="white").grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
