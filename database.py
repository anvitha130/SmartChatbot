import sqlite3

# Connect to (or create) the database
def get_connection():
    return sqlite3.connect("sdc_project.db")

# Create the table (run automatically when app starts)
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            question TEXT,
            response TEXT,
            mode TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Insert a new record into the table
def insert_query(username, question, response, mode):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO queries (username, question, response, mode)
        VALUES (?, ?, ?, ?)
    """, (username, question, response, mode))
    conn.commit()
    conn.close()

# Optional: Fetch previous queries for display
def get_queries(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question, response, mode, timestamp FROM queries WHERE username=?", (username,))
    data = cursor.fetchall()
    conn.close()
    return data
