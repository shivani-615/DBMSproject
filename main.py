import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# --- DATABASE SETUP ---
def create_tables():
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()

    # Customer Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Customer (
        Cust_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Address TEXT,
        PhoneNumber TEXT UNIQUE
    )
    ''')

    # Employee Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Employee (
        Emp_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Role TEXT,
        Email TEXT UNIQUE,
        PhoneNumber TEXT UNIQUE
    )
    ''')

    # Medicine Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Medicine (
        Med_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        SupplierID INTEGER,
        Brand TEXT,
        Price REAL,
        ExpiryDate TEXT,
        ManufactureDate TEXT
    )
    ''')

    # Sales Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sales (
        Sale_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Cust_ID INTEGER,
        Med_ID INTEGER,
        SaleDate TEXT,
        Quantity INTEGER,
        TotalAmount REAL,
        FOREIGN KEY(Cust_ID) REFERENCES Customer(Cust_ID),
        FOREIGN KEY(Med_ID) REFERENCES Medicine(Med_ID)
    )
    ''')

    # Stock Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Stock (
        Med_ID INTEGER PRIMARY KEY,
        StockQuantity INTEGER,
        LastUpdated TEXT,
        FOREIGN KEY(Med_ID) REFERENCES Medicine(Med_ID)
    )
    ''')

    conn.commit()
    conn.close()
    print("All tables created successfully!")

create_tables()

# --- HELPER FUNCTION TO VIEW TABLES ---
def view_table(title, table_name, columns):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("700x400")

    tree = ttk.Treeview(win, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill=tk.BOTH, expand=True)

    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", tk.END, values=row)

# --- CUSTOMER FUNCTIONS ---
def add_customer():
    name = customer_name.get()
    address = customer_address.get()
    phone = customer_phone.get()
    if not name or not phone:
        messagebox.showwarning("Input Error", "Name and Phone are required")
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
        messagebox.showerror("Error", "Phone number already exists")
    customer_name.delete(0, tk.END)
    customer_address.delete(0, tk.END)
    customer_phone.delete(0, tk.END)

# --- EMPLOYEE FUNCTIONS ---
def add_employee():
    name = emp_name.get()
    role = emp_role.get()
    email = emp_email.get()
    phone = emp_phone.get()
    if not name:
        messagebox.showwarning("Input Error", "Name is required")
        return
    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Employee (Name, Role, Email, PhoneNumber) VALUES (?, ?, ?, ?)",
                       (name, role, email, phone))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Employee added successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Email or Phone already exists")
    emp_name.delete(0, tk.END)
    emp_role.delete(0, tk.END)
    emp_email.delete(0, tk.END)
    emp_phone.delete(0, tk.END)

# --- MEDICINE FUNCTIONS ---
def add_medicine():
    supplier = med_supplier.get()
    brand = med_brand.get()
    price = med_price.get()
    exp = med_expiry.get()
    manu = med_manu.get()
    if not brand or not price:
        messagebox.showwarning("Input Error", "Brand and Price are required")
        return
    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Medicine (SupplierID, Brand, Price, ExpiryDate, ManufactureDate) VALUES (?, ?, ?, ?, ?)",
                       (supplier, brand, price, exp, manu))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Medicine added successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    med_supplier.delete(0, tk.END)
    med_brand.delete(0, tk.END)
    med_price.delete(0, tk.END)
    med_expiry.delete(0, tk.END)
    med_manu.delete(0, tk.END)

# --- SALES FUNCTIONS ---
def add_sale():
    cust_id_val = sale_cust.get()
    med_id_val = sale_med.get()
    qty_val = sale_qty.get()
    if not cust_id_val or not med_id_val or not qty_val:
        messagebox.showwarning("Input Error", "All fields are required")
        return
    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Price FROM Medicine WHERE Med_ID=?", (med_id_val,))
        price_row = cursor.fetchone()
        if not price_row:
            messagebox.showerror("Error", "Medicine not found")
            return
        total = int(qty_val) * float(price_row[0])
        cursor.execute("INSERT INTO Sales (Cust_ID, Med_ID, SaleDate, Quantity, TotalAmount) VALUES (?, ?, ?, ?, ?)",
                       (cust_id_val, med_id_val, datetime.now().strftime("%Y-%m-%d"), qty_val, total))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Sale added! Total Amount: {total}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    sale_cust.delete(0, tk.END)
    sale_med.delete(0, tk.END)
    sale_qty.delete(0, tk.END)

# --- STOCK FUNCTIONS ---
def add_stock():
    medid = stock_med.get()
    qty = stock_qty.get()
    if not medid or not qty:
        messagebox.showwarning("Input Error", "All fields are required")
        return
    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO Stock (Med_ID, StockQuantity, LastUpdated) VALUES (?, ?, ?)",
                       (medid, qty, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Stock updated successfully")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    stock_med.delete(0, tk.END)
    stock_qty.delete(0, tk.END)

# --- GUI SETUP ---
root = tk.Tk()
root.title("Pharmacy Management System")
root.geometry("650x700")

tabControl = ttk.Notebook(root)

# --- CUSTOMER TAB ---
customer_tab = ttk.Frame(tabControl)
tabControl.add(customer_tab, text='Customer')
tk.Label(customer_tab, text="Name").grid(row=0, column=0, padx=10, pady=5)
customer_name = tk.Entry(customer_tab)
customer_name.grid(row=0, column=1)
tk.Label(customer_tab, text="Address").grid(row=1, column=0, padx=10, pady=5)
customer_address = tk.Entry(customer_tab)
customer_address.grid(row=1, column=1)
tk.Label(customer_tab, text="Phone").grid(row=2, column=0, padx=10, pady=5)
customer_phone = tk.Entry(customer_tab)
customer_phone.grid(row=2, column=1)
tk.Button(customer_tab, text="Add Customer", command=add_customer, bg="green", fg="white").grid(row=3, column=0, columnspan=2, pady=5)
tk.Button(customer_tab, text="View Customers", command=lambda: view_table("All Customers", "Customer", ["Cust_ID","Name","Address","PhoneNumber"]), bg="blue", fg="white").grid(row=4, column=0, columnspan=2, pady=5)

# --- EMPLOYEE TAB ---
employee_tab = ttk.Frame(tabControl)
tabControl.add(employee_tab, text='Employee')
tk.Label(employee_tab, text="Name").grid(row=0, column=0, padx=10, pady=5)
emp_name = tk.Entry(employee_tab)
emp_name.grid(row=0, column=1)
tk.Label(employee_tab, text="Role").grid(row=1, column=0, padx=10, pady=5)
emp_role = tk.Entry(employee_tab)
emp_role.grid(row=1, column=1)
tk.Label(employee_tab, text="Email").grid(row=2, column=0, padx=10, pady=5)
emp_email = tk.Entry(employee_tab)
emp_email.grid(row=2, column=1)
tk.Label(employee_tab, text="Phone").grid(row=3, column=0, padx=10, pady=5)
emp_phone = tk.Entry(employee_tab)
emp_phone.grid(row=3, column=1)
tk.Button(employee_tab, text="Add Employee", command=add_employee, bg="green", fg="white").grid(row=4, column=0, columnspan=2, pady=5)
tk.Button(employee_tab, text="View Employees", command=lambda: view_table("All Employees", "Employee", ["Emp_ID","Name","Role","Email","PhoneNumber"]), bg="blue", fg="white").grid(row=5, column=0, column
