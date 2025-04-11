import sqlite3

# Step 1: Connect to the database
con = sqlite3.connect("edudocs.db")

# Step 2: Run the SQL command to add the 'category' column
try:
    con.execute("ALTER TABLE documents ADD COLUMN category TEXT;")
    print("✅ 'category' column added successfully.")
except sqlite3.OperationalError as e:
    print("⚠️ Error:", e)

# Step 3: Close the connection
con.close()
