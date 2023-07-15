import streamlit as st
import sqlite3

def calculate_simple_interest(principal, rate, time):
    interest = (principal * rate * time) / 100
    return interest

def calculate_compound_interest(principal, rate, time):
    amount = principal * (1 + rate/100) ** time
    interest = amount - principal
    return interest

conn = sqlite3.connect("bank_database.db")
cursor = conn.cursor()

st.title("Interest Calculator")

account_number = st.text_input("Enter account number")
rate = st.number_input("Enter interest rate (%)", value=5.0, step=0.1)
time = st.number_input("Enter time period (years)", value=1, step=1)



if st.button("Calculate Interest"):
    cursor.execute(f"SELECT Balance FROM customers WHERE Account_number={account_number}")
    balance = cursor.fetchone()[0]
    
    st.markdown("""<br><hr>""",unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center;  font-size:40px'>Current balance: {balance}</h1><br><hr>", unsafe_allow_html=True) 

    simple_interest = calculate_simple_interest(balance, rate, time)
    compound_interest = calculate_compound_interest(balance, rate, time)

    st.markdown("<h1 style='text-align: center; color : white; font-size:45px'>Simple Interest</h1><br>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color : #E8570E; font-size:40px'> {simple_interest}</h1><br><hr>", unsafe_allow_html=True)  
    
    st.markdown("<h1 style='text-align: center; color : white; font-size:45px'>Compound Interest</h1><br>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color : #E8570E; font-size:40px'> {compound_interest}</h1><br><hr>", unsafe_allow_html=True)  