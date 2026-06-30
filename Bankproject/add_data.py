import sqlite3

def add_new_customer():
    # Get user input for customer details
    name = input("Enter customer name: ")
    email = input("Enter customer email: ")
    address = input("Enter customer address: ")
    
    # Connect to the database
    conn = sqlite3.connect('bank_system.db')
    cursor = conn.cursor()
    
    try:
        # Insert the data into the customers table
        cursor.execute("INSERT INTO customers (name, email, address) VALUES (?, ?, ?)", (name, email, address))
        conn.commit()
        print("Customer added successfully!")
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_new_customer()
