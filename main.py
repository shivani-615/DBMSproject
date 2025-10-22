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
        Name TEXT NOT NULL CHECK(Name REGEXP '^[A-Za-z ]+$'),
        Address TEXT,
        PhoneNumber TEXT UNIQUE NOT NULL CHECK(PhoneNumber REGEXP '^[0-9]{10}$')
    )
    ''')

    # Employee Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Employee (
        Emp_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL CHECK(Name REGEXP '^[A-Za-z ]+$'),
        Role TEXT NOT NULL,
        Email TEXT UNIQUE NOT NULL CHECK(Email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
        PhoneNumber TEXT UNIQUE NOT NULL CHECK(PhoneNumber REGEXP '^[0-9]{10}$')
    )
    ''')

    # Supplier Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Supplier (
        Supplier_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL CHECK(Name REGEXP '^[A-Za-z ]+$'),
        Contact TEXT CHECK(Contact REGEXP '^[0-9]{10}$')
    )
    ''')

    # Medicine Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Medicine (
        Med_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        SupplierID INTEGER NOT NULL,
        Brand TEXT NOT NULL,
        Price REAL NOT NULL CHECK(Price > 0),
        ExpiryDate TEXT NOT NULL,
        ManufactureDate TEXT NOT NULL,
        CHECK(date(ExpiryDate) > date(ManufactureDate)),
        FOREIGN KEY(SupplierID) REFERENCES Supplier(Supplier_ID)
    )
    ''')

    # Sales Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sales (
        Sale_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Cust_ID INTEGER NOT NULL,
        Med_ID INTEGER NOT NULL,
        SaleDate TEXT NOT NULL,
        Quantity INTEGER NOT NULL CHECK(Quantity > 0),
        TotalAmount REAL NOT NULL CHECK(TotalAmount >= 0),
        FOREIGN KEY(Cust_ID) REFERENCES Customer(Cust_ID),
        FOREIGN KEY(Med_ID) REFERENCES Medicine(Med_ID)
    )
    ''')

    # Stock Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Stock (
        Med_ID INTEGER PRIMARY KEY,
        StockQuantity INTEGER NOT NULL CHECK(StockQuantity >= 0),
        LastUpdated TEXT NOT NULL,
        FOREIGN KEY(Med_ID) REFERENCES Medicine(Med_ID)
    )
    ''')

    conn.commit()
    conn.close()


create_tables()


# --- HELPER FUNCTION TO VIEW TABLES ---
def view_table(title, table_name, columns):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("700x400")

    tree = ttk.Treeview(win, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
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
    name = customer_name.get().strip()
    address = customer_address.get().strip()
    phone = customer_phone.get().strip()
    
    if not name or not phone:
        messagebox.showwarning("Input Error", "Name and Phone are required")
        return
        
    # Validate name (letters and spaces only)
    if not all(c.isalpha() or c.isspace() for c in name):
        messagebox.showwarning("Input Error", "Name must contain only letters and spaces")
        return
    
    # Validate phone (10 digits)
    if not (phone.isdigit() and len(phone) == 10):
        messagebox.showwarning("Input Error", "Phone number must be exactly 10 digits")
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
def validate_email(email):
    import re
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(pattern, email) is not None

def add_employee():
    name = emp_name.get().strip()
    role = emp_role.get().strip()
    email = emp_email.get().strip()
    phone = emp_phone.get().strip()
    
    # Required fields
    if not all([name, role, email, phone]):
        messagebox.showwarning("Input Error", "All fields are required")
        return
        
    # Validate name (letters and spaces only)
    if not all(c.isalpha() or c.isspace() for c in name):
        messagebox.showwarning("Input Error", "Name must contain only letters and spaces")
        return
        
    # Validate email format
    if not validate_email(email):
        messagebox.showwarning("Input Error", "Invalid email format")
        return
        
    # Validate phone (10 digits)
    if not (phone.isdigit() and len(phone) == 10):
        messagebox.showwarning("Input Error", "Phone number must be exactly 10 digits")
        return
        
    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Employee (Name, Role, Email, PhoneNumber) VALUES (?, ?, ?, ?)",
                       (name, role, email, phone))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Employee added successfully!")
    except sqlite3.IntegrityError as e:
        if "Email" in str(e):
            messagebox.showerror("Error", "Email address already exists")
        else:
            messagebox.showerror("Error", "Phone number already exists")
    emp_name.delete(0, tk.END)
    emp_role.delete(0, tk.END)
    emp_email.delete(0, tk.END)
    emp_phone.delete(0, tk.END)


# --- MEDICINE FUNCTIONS ---
def validate_date_format(date_str):
    import re
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', date_str))
    
def is_valid_date_order(manu_date, exp_date):
    from datetime import datetime
    try:
        manu = datetime.strptime(manu_date, '%Y-%m-%d')
        exp = datetime.strptime(exp_date, '%Y-%m-%d')
        return exp > manu
    except ValueError:
        return False

def add_medicine():
    supplier_text = med_supplier_combo.get()
    if supplier_text == "Select Supplier" or not supplier_text:
        messagebox.showwarning("Input Error", "Please select a supplier")
        return
    
    # Extract supplier ID from the combo box selection (format: "ID: Name")
    supplier_id = supplier_text.split(':')[0]
    
    brand = med_brand.get().strip()
    price = med_price.get().strip()
    exp = med_expiry.get().strip()
    manu = med_manu.get().strip()
    
    # Validate required fields
    if not all([brand, price, exp, manu]):
        messagebox.showwarning("Input Error", "All fields are required")
        return
        
    # Validate price is positive number
    try:
        price_float = float(price)
        if price_float <= 0:
            raise ValueError()
    except ValueError:
        messagebox.showwarning("Input Error", "Price must be a positive number")
        return
        
    # Validate date formats
    if not (validate_date_format(exp) and validate_date_format(manu)):
        messagebox.showwarning("Input Error", "Dates must be in YYYY-MM-DD format")
        return
        
    # Validate expiry is after manufacture
    if not is_valid_date_order(manu, exp):
        messagebox.showwarning("Input Error", "Expiry date must be after manufacture date")
        return
        
    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        
        # Check if supplier exists
        cursor.execute("SELECT 1 FROM Supplier WHERE Supplier_ID = ?", (supplier,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Invalid Supplier ID")
            conn.close()
            return
            
        cursor.execute("""
            INSERT INTO Medicine 
            (SupplierID, Brand, Price, ExpiryDate, ManufactureDate) 
            VALUES (?, ?, ?, ?, ?)""",
            (supplier, brand, price_float, exp, manu))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Medicine added successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Database constraint violation")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        
    med_supplier_combo.set("Select Supplier")
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
        qty_int = int(qty_val)
        if qty_int <= 0:
            raise ValueError()
    except Exception:
        messagebox.showerror("Error", "Quantity must be a positive integer")
        return

    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        # get price
        cursor.execute("SELECT Price FROM Medicine WHERE Med_ID=?", (med_id_val,))
        price_row = cursor.fetchone()
        if not price_row:
            messagebox.showerror("Error", "Medicine not found")
            conn.close()
            return

        # check stock
        cursor.execute("SELECT StockQuantity FROM Stock WHERE Med_ID=?", (med_id_val,))
        stock_row = cursor.fetchone()
        if not stock_row:
            messagebox.showerror("Error", "No stock record found for this medicine")
            conn.close()
            return
        available = int(stock_row[0])
        if available < qty_int:
            messagebox.showerror("Insufficient Stock", f"Requested {qty_int} but only {available} in stock")
            conn.close()
            return

        total = qty_int * float(price_row[0])
        cursor.execute("INSERT INTO Sales (Cust_ID, Med_ID, SaleDate, Quantity, TotalAmount) VALUES (?, ?, ?, ?, ?)",
                       (cust_id_val, med_id_val, datetime.now().strftime("%Y-%m-%d"), qty_int, total))

        # decrement stock
        cursor.execute("UPDATE Stock SET StockQuantity = StockQuantity - ?, LastUpdated = ? WHERE Med_ID = ?",
                       (qty_int, datetime.now().strftime("%Y-%m-%d"), med_id_val))

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
    medid = stock_med.get().strip()
    qty = stock_qty.get().strip()
    
    # Validate required fields
    if not medid or not qty:
        messagebox.showwarning("Input Error", "All fields are required")
        return
        
    # Validate quantity is non-negative integer
    try:
        qty_int = int(qty)
        if qty_int < 0:
            raise ValueError()
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a non-negative integer")
        return

    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        
        # Check if medicine exists
        cursor.execute("SELECT 1 FROM Medicine WHERE Med_ID = ?", (medid,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Invalid Medicine ID")
            conn.close()
            return
            
        # Update or insert stock record
        cursor.execute("SELECT StockQuantity FROM Stock WHERE Med_ID=?", (medid,))
        row = cursor.fetchone()
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        if row:
            cursor.execute("""
                UPDATE Stock 
                SET StockQuantity = ?, LastUpdated = ? 
                WHERE Med_ID = ?""", (qty_int, current_date, medid))
            action = "updated"
        else:
            cursor.execute("""
                INSERT INTO Stock (Med_ID, StockQuantity, LastUpdated) 
                VALUES (?, ?, ?)""", (medid, qty_int, current_date))
            action = "created"
            
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Stock record {action} successfully")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Database constraint violation")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        
    stock_med.delete(0, tk.END)
    stock_qty.delete(0, tk.END)


# --- LOW STOCK VIEWER ---
def view_low_stock(threshold=5):
    win = tk.Toplevel(root)
    win.title(f"Low Stock (<{threshold})")
    win.geometry("700x300")

    tree = ttk.Treeview(win, columns=("Med_ID", "Brand", "StockQuantity", "LastUpdated"), show='headings')
    for col in ("Med_ID", "Brand", "StockQuantity", "LastUpdated"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill=tk.BOTH, expand=True)

    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.Med_ID, m.Brand, s.StockQuantity, s.LastUpdated
        FROM Stock s JOIN Medicine m ON s.Med_ID = m.Med_ID
        WHERE s.StockQuantity < ?
        ORDER BY s.StockQuantity ASC
    ''', (threshold,))
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", tk.END, values=row)


# --- DELETE FUNCTIONS ---
def delete_customer():
    cid = del_cust_id.get()
    if not cid:
        messagebox.showwarning("Input Error", "Customer ID required")
        return
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Customer WHERE Cust_ID=?", (cid,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Deleted", f"Customer {cid} deleted (if existed)")
    del_cust_id.delete(0, tk.END)


def delete_employee():
    eid = del_emp_id.get()
    if not eid:
        messagebox.showwarning("Input Error", "Employee ID required")
        return
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Employee WHERE Emp_ID=?", (eid,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Deleted", f"Employee {eid} deleted (if existed)")
    del_emp_id.delete(0, tk.END)


def delete_medicine():
    mid = del_med_id.get()
    if not mid:
        messagebox.showwarning("Input Error", "Medicine ID required")
        return
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    # remove stock record if present
    cursor.execute("DELETE FROM Stock WHERE Med_ID=?", (mid,))
    cursor.execute("DELETE FROM Medicine WHERE Med_ID=?", (mid,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Deleted", f"Medicine {mid} and its stock removed (if existed)")
    del_med_id.delete(0, tk.END)


# --- SUPPLIER FUNCTIONS ---
def add_supplier():
    name = supplier_name.get().strip()
    contact = supplier_contact.get().strip()
    
    if not name:
        messagebox.showwarning("Input Error", "Supplier name is required")
        return
        
    # Validate name (letters and spaces only)
    if not all(c.isalpha() or c.isspace() for c in name):
        messagebox.showwarning("Input Error", "Name must contain only letters and spaces")
        return
    
    # Validate contact if provided
    if contact and not (contact.isdigit() and len(contact) == 10):
        messagebox.showwarning("Input Error", "Contact must be 10 digits")
        return
        
    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Supplier (Name, Contact) VALUES (?, ?)",
                       (name, contact if contact else None))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Supplier added successfully!")
        # Refresh supplier list in medicine tab
        update_supplier_list()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Supplier already exists")
    supplier_name.delete(0, tk.END)
    supplier_contact.delete(0, tk.END)

def update_supplier_list():
    # Update the supplier dropdown in medicine tab
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Supplier_ID, Name FROM Supplier ORDER BY Name")
    suppliers = cursor.fetchall()
    conn.close()
    
    # Update the ComboBox values
    supplier_choices = [f"{sid}: {name}" for sid, name in suppliers]
    med_supplier_combo['values'] = supplier_choices
    if supplier_choices:
        med_supplier_combo.set("Select Supplier")

# --- GUI SETUP ---
root = tk.Tk()
root.title("Pharmacy Management System")
root.geometry("760x700")

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
tk.Button(customer_tab, text="View Customers", command=lambda: view_table("All Customers", "Customer", ["Cust_ID", "Name", "Address", "PhoneNumber"]), bg="blue", fg="white").grid(row=4, column=0, columnspan=2, pady=5)

# delete customer
tk.Label(customer_tab, text="Delete Customer ID").grid(row=5, column=0, padx=10, pady=5)
del_cust_id = tk.Entry(customer_tab)
del_cust_id.grid(row=5, column=1)
tk.Button(customer_tab, text="Delete Customer", command=delete_customer, bg="red", fg="white").grid(row=6, column=0, columnspan=2, pady=5)

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
tk.Button(employee_tab, text="View Employees",
          command=lambda: view_table("All Employees", "Employee",
                                     ["Emp_ID", "Name", "Role", "Email", "PhoneNumber"]),
          bg="blue", fg="white").grid(row=5, column=0, columnspan=2, pady=5)

# delete employee
tk.Label(employee_tab, text="Delete Employee ID").grid(row=6, column=0, padx=10, pady=5)
del_emp_id = tk.Entry(employee_tab)
del_emp_id.grid(row=6, column=1)
tk.Button(employee_tab, text="Delete Employee", command=delete_employee, bg="red", fg="white").grid(row=7, column=0, columnspan=2, pady=5)

# --- SUPPLIER TAB ---
supplier_tab = ttk.Frame(tabControl)
tabControl.add(supplier_tab, text='Supplier')

tk.Label(supplier_tab, text="Name").grid(row=0, column=0, padx=10, pady=5)
supplier_name = tk.Entry(supplier_tab)
supplier_name.grid(row=0, column=1)

tk.Label(supplier_tab, text="Contact (10 digits)").grid(row=1, column=0, padx=10, pady=5)
supplier_contact = tk.Entry(supplier_tab)
supplier_contact.grid(row=1, column=1)

tk.Button(supplier_tab, text="Add Supplier", command=add_supplier, bg="green", fg="white").grid(row=2, column=0, columnspan=2, pady=5)
tk.Button(supplier_tab, text="View Suppliers",
          command=lambda: view_table("All Suppliers", "Supplier", ["Supplier_ID", "Name", "Contact"]),
          bg="blue", fg="white").grid(row=3, column=0, columnspan=2, pady=5)

# --- MEDICINE TAB ---
medicine_tab = ttk.Frame(tabControl)
tabControl.add(medicine_tab, text='Medicine')

tk.Label(medicine_tab, text="Supplier").grid(row=0, column=0, padx=10, pady=5)
med_supplier_combo = ttk.Combobox(medicine_tab, state="readonly")
med_supplier_combo.grid(row=0, column=1)
update_supplier_list()  # Populate supplier dropdown

tk.Label(medicine_tab, text="Brand").grid(row=1, column=0, padx=10, pady=5)
med_brand = tk.Entry(medicine_tab)
med_brand.grid(row=1, column=1)

tk.Label(medicine_tab, text="Price").grid(row=2, column=0, padx=10, pady=5)
med_price = tk.Entry(medicine_tab)
med_price.grid(row=2, column=1)

tk.Label(medicine_tab, text="Expiry Date (YYYY-MM-DD)").grid(row=3, column=0, padx=10, pady=5)
med_expiry = tk.Entry(medicine_tab)
med_expiry.grid(row=3, column=1)

tk.Label(medicine_tab, text="Manufacture Date (YYYY-MM-DD)").grid(row=4, column=0, padx=10, pady=5)
med_manu = tk.Entry(medicine_tab)
med_manu.grid(row=4, column=1)

tk.Button(medicine_tab, text="Add Medicine", command=add_medicine, bg="green", fg="white").grid(row=5, column=0, columnspan=2, pady=5)
tk.Button(medicine_tab, text="View Medicines",
          command=lambda: view_table("All Medicines", "Medicine", ["Med_ID", "SupplierID", "Brand", "Price", "ExpiryDate", "ManufactureDate"]),
          bg="blue", fg="white").grid(row=6, column=0, columnspan=2, pady=5)

# delete medicine
tk.Label(medicine_tab, text="Delete Medicine ID").grid(row=7, column=0, padx=10, pady=5)
del_med_id = tk.Entry(medicine_tab)
del_med_id.grid(row=7, column=1)
tk.Button(medicine_tab, text="Delete Medicine", command=delete_medicine, bg="red", fg="white").grid(row=8, column=0, columnspan=2, pady=5)


# --- STOCK TAB ---
stock_tab = ttk.Frame(tabControl)
tabControl.add(stock_tab, text='Stock')

tk.Label(stock_tab, text="Medicine ID").grid(row=0, column=0, padx=10, pady=5)
stock_med = tk.Entry(stock_tab)
stock_med.grid(row=0, column=1)

tk.Label(stock_tab, text="Quantity").grid(row=1, column=0, padx=10, pady=5)
stock_qty = tk.Entry(stock_tab)
stock_qty.grid(row=1, column=1)

tk.Button(stock_tab, text="Set/Update Stock", command=add_stock, bg="green", fg="white").grid(row=2, column=0, columnspan=2, pady=5)
tk.Button(stock_tab, text="View Stock", command=lambda: view_table("Stock", "Stock", ["Med_ID", "StockQuantity", "LastUpdated"]), bg="blue", fg="white").grid(row=3, column=0, columnspan=2, pady=5)
tk.Button(stock_tab, text="View Low Stock", command=lambda: view_low_stock(5), bg="orange", fg="black").grid(row=4, column=0, columnspan=2, pady=5)


# --- SALES TAB ---
sales_tab = ttk.Frame(tabControl)
tabControl.add(sales_tab, text='Sales')

tk.Label(sales_tab, text="Customer ID").grid(row=0, column=0, padx=10, pady=5)
sale_cust = tk.Entry(sales_tab)
sale_cust.grid(row=0, column=1)

tk.Label(sales_tab, text="Medicine ID").grid(row=1, column=0, padx=10, pady=5)
sale_med = tk.Entry(sales_tab)
sale_med.grid(row=1, column=1)

tk.Label(sales_tab, text="Quantity").grid(row=2, column=0, padx=10, pady=5)
sale_qty = tk.Entry(sales_tab)
sale_qty.grid(row=2, column=1)

tk.Button(sales_tab, text="Add Sale", command=add_sale, bg="green", fg="white").grid(row=3, column=0, columnspan=2, pady=5)
tk.Button(sales_tab, text="View Sales",
          command=lambda: view_table("All Sales", "Sales", ["Sale_ID", "Cust_ID", "Med_ID", "SaleDate", "Quantity", "TotalAmount"]),
          bg="blue", fg="white").grid(row=4, column=0, columnspan=2, pady=5)


tabControl.pack(expand=1, fill="both")
root.mainloop()


