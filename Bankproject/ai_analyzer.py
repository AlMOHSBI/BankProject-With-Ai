import sqlite3
import ollama

def analyze_customers():
    # Connect to the database
    conn = sqlite3.connect('bank_system.db')
    cursor = conn.cursor()
    
    # Fetch name and balance for all customers
    cursor.execute("SELECT name, balance FROM customers")
    customers = cursor.fetchall()
    conn.close()

    if not customers:
        print("Database is empty!")
        return

    # Prepare data for AI
    data_text = "\n".join([f"Customer: {c[0]}, Balance: ${c[1]}" for c in customers])
    prompt = f"Analyze the following bank data and provide a brief financial advice or status for each customer:\n{data_text}"

    # Send to Ollama
    print("Asking AI to analyze your bank data...")
    response = ollama.chat(model='llama3', messages=[
        {'role': 'user', 'content': prompt}
    ])
    
    print("\n--- AI Financial Report ---")
    print(response['message']['content'])

if __name__ == "__main__":
    analyze_customers()
