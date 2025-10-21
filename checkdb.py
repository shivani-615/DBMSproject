import sqlite3

conn = sqlite3.connect('pharmacy.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM Customer")
rows = cursor.fetchall()
conn.close()

print("Customer table contents:")
print(rows)
