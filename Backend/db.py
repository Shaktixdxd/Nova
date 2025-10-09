import csv
import sqlite3
import os

# Connect to database
con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

# Create contacts table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200),
        mobile_no VARCHAR(255),
        email VARCHAR(255) NULL
    )
''')

# -------- Read from CSV and insert into database --------
with open('contacts.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        if len(row) >= 2:  # Make sure we have both name and mobile number
            name = row[0].strip()
            mobile_no = row[1].strip()
            cursor.execute(
                "INSERT INTO contacts (name, mobile_no, email) VALUES (?, ?, NULL)",
                (name, mobile_no)
            )

# Commit changes
con.commit()


# -------- Example search query --------
query = 'ronie'
query = query.strip().lower()

cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", 
               ('%' + query + '%', query + '%'))
results = cursor.fetchall()

if results:
    print("Mobile number:", results[0][0])
else:
    print("Contact not found.")

# Close connection


# delete contacts all -------------------
# cursor.execute("DELETE FROM contacts")
# con.commit()
# print("✅ All contacts deleted.")


con.close()