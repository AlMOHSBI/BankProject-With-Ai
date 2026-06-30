import sqlite3

def clean_database():
    conn = sqlite3.connect('bank_system.db')
    cur = conn.cursor()
    
    
    cur.execute("DELETE FROM transactions WHERE type IN ('Dep', 'With')")
    
    conn.commit()
    conn.close()
    print("Database cleaned successfully! Old labels removed.")

if __name__ == "__main__":
    clean_database()
