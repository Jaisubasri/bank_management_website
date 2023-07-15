import sqlite3
import streamlit as st

def check_loan_eligibility(account_number, loan_amount, loan_type):
    with sqlite3.connect('bank_database.db') as bank_db:
        cursor = bank_db.cursor()
        # check if customer exists
        cursor.execute(f"SELECT balance FROM customers WHERE Account_number = {account_number}")
        customer = cursor.fetchone()
        if not customer:
            st.error("Customer not found")
        else:
            balance = customer[0]
            # check if customer is eligible for loan
            if loan_type == "Personal":
                if balance >= loan_amount * 2:
                    st.success("Loan approved")
                else:
                    st.error("Loan denied")
            elif loan_type == "Business":
                if balance >= loan_amount * 3:
                    st.success("Loan approved")
                else:
                    st.error("Loan denied")
            else:
                st.warning("Invalid loan type")


# Streamlit form for checking loan eligibility
st.write("# Bank Loan")
account_number = st.text_input("Account Number:")
loan_amount = st.number_input("Loan Amount:", step=0.01, min_value=0.01)
loan_type = st.selectbox("Loan Type:", ["Personal", "Business"])
if st.button("Check Eligibility"):
    if not account_number:
        st.warning("Please enter account number")
    elif not loan_amount:
        st.warning("Please enter loan amount")
    elif loan_amount <= 0:
        st.warning("Loan amount must be greater than zero")
    else:
        try:
            account_number = int(account_number)
            check_loan_eligibility(account_number, loan_amount, loan_type)
        except ValueError:
            st.warning("Invalid account number")