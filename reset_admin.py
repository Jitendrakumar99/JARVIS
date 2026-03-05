"""Quick Admin Reset - No heavy imports"""
import sqlite3
from werkzeug.security import generate_password_hash

# Connect to database
db_path = 'college_portal.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if admin table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin'")
    if not cursor.fetchone():
        # Create admin table
        cursor.execute('''CREATE TABLE admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL
        )''')
        print("Created admin table")
    
    # Delete existing admins
    cursor.execute("DELETE FROM admin")
    
    # Create new admin
    password_hash = generate_password_hash('admin123')
    cursor.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)", 
                   ('admin', password_hash))
    
    conn.commit()
    print("✅ Admin reset successfully!")
    print("   Username: admin")
    print("   Password: admin123")
    print("\nNow restart Flask and login!")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
