import streamlit as st
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('bank_database.db')
cursor = conn.cursor()

# Create the transfers table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS transfers (
                    transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_account INTEGER NOT NULL,
                    recipient_account INTEGER NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    transfer_date DATE NOT NULL DEFAULT CURRENT_DATE
                );''')

# Define the transfer_funds function
def transfer_funds(sender_account, recipient_account, amount):
    """
    Transfers funds from the sender's account to the recipient's account.
    Returns True if the transfer is successful, False otherwise.
    """
    try:
        # Begin a transaction
        conn.execute("BEGIN")

        # Check if the sender has sufficient funds
        cursor.execute("SELECT balance FROM customers WHERE account_number=?", (sender_account,))
        sender_balance = cursor.fetchone()[0]
        if sender_balance < amount:
            return False

        # Deduct the amount from the sender's balance
        cursor.execute("UPDATE customers SET balance=balance-? WHERE account_number=?", (amount, sender_account))

        # Add the amount to the recipient's balance
        cursor.execute("UPDATE customers SET balance=balance+? WHERE account_number=?", (amount, recipient_account))

        # Insert a new record into the transfers table
        cursor.execute("INSERT INTO transfers (sender_account, recipient_account, amount) VALUES (?, ?, ?)",
                       (sender_account, recipient_account, amount))
        generate_transaction_report(sender_account);
        # Commit the transaction
        conn.commit()

        return True

    except Exception as e:
        # Rollback the transaction on error
        conn.rollback()
        print("Error occurred during transfer:", str(e))
        return False


# Define the function for generating the transaction report
def generate_transaction_report(account_number):
    """
    Generates a transaction report for a particular account number.
    Returns a DataFrame containing the report.
    """
    # Connect to the database
    conn = sqlite3.connect('bank_database.db')
    cursor = conn.cursor()

    # Query the transfers table for all transfers involving the account number
    cursor.execute("SELECT sender_account, recipient_account, amount, transfer_date FROM transfers WHERE sender_account=? OR recipient_account=? ORDER BY transfer_date DESC", (account_number, account_number))
    rows = cursor.fetchall()

    # If there are no transfers, return a message saying so
    if not rows:
        return pd.DataFrame({"message": [f"No transfers found for account number {account_number}."]})

    # If there are transfers, create a DataFrame summarizing all transfers
    df = pd.DataFrame(rows, columns=["sender_account", "recipient_account", "amount", "timestamp"])
    print("Initial DataFrame:")

    # Assign type column
    df["type"] = ""
    df.loc[df["sender_account"] == int(account_number), "type"] = "Sent"
    df.loc[df["recipient_account"] == int(account_number), "type"] = "Received"
    print("DataFrame with type column:")
    print(df)

    # Format columns
    df["amount"] = df["amount"].apply(lambda x: f"${x:.2f}")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df[["type", "amount", "timestamp"]]

    return df

# Define the Streamlit app
st.set_page_config(page_title="Transaction Report", page_icon=":money_with_wings:")

# Streamlit app code
st.title("Bank Transfer App")

# Get input values from user
sender = st.text_input("Sender account number:")
recipient = st.text_input("Recipient account number:")
amount = st.number_input("Amount to transfer:", step=0.01)

# Transfer funds on button press
if st.button("Transfer"):
    result = transfer_funds(sender, recipient, amount)
    if result:
        st.markdown("""<br><hr>""",unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color : white; font-size:45px'>Transaction Report</h1><hr><br>", unsafe_allow_html=True)
        df = generate_transaction_report(sender)
        st.table(df)
        st.success("Transfer successful!")
    else:
        st.error("Transfer failed.")

# Generate the transaction report and display it
