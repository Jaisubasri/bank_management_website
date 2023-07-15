import streamlit as st
import csv
import random
import string
import os
import pandas as pd
import sqlite3
import datetime
import smtplib
from email.mime.text import MIMEText
from email.message import EmailMessage
import ssl
from Database import BankDB

st.set_page_config(layout="wide")

#Tile
styles = """
    /* Center align text */
    .center {
        text-align: center;
    }

    /* Add a shadow to the box */
    .shadow {
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.25);
    }

    /* Add a gradient background */
    body {
        background: linear-gradient(to bottom, #ffffff, #f2f2f2);
    }

    /* Style the header */
    .header {
        background: linear-gradient(to bottom, #000000, #2C3539);
        color: white;
        padding: 20px;
    }

    /* Style the footer */
    .footer {
        background: linear-gradient(to bottom, #4B0082, #800080);
        color: white;
        padding: 20px;
    }
"""
st.markdown(f'<style>{styles}</style>', unsafe_allow_html=True)
header_html = """
    <div class="header shadow">
        <h1 class="center rainbow-text">STATE BANK OF INDIA</h1>
    </div>
"""
st.markdown(header_html, unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

def send_email(to, account_number , subject , body):
    email_sender = '21pd24@psgtech.ac.in'
    email_password  = 'ujzmhtridttmetdj'
        
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = to
    em['subject'] = subject
    em.set_content(body)
        
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com' , 465 , context = context) as smtp:
        smtp.login(email_sender , email_password)
        smtp.sendmail(email_sender , to , em.as_string())

tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs(["Home" , "Create Account" , "Update Account" , "Delete Account" ,"Account Detail" , "Credit Balance" , "Debit Balance"])

with tab1:
    images = ["https://pbs.twimg.com/media/Dd4RqbYU0AMAXE0.jpg",
          "https://pbs.twimg.com/media/EceQOjPUEAMEInR.jpg",
          "https://pbs.twimg.com/media/FWp8hD1aIAAIgDK.jpg",
        ]

    image_html = ''
    for url in images:
          image_html += f'<img src="{url}" style="width:2000px; height:550px; object-fit: cover; display: block;margin-right: 20px;">'

    st.markdown(f"""<div style="display: flex; overflow-x: scroll; padding: 10px 0;">{image_html}</div>""", unsafe_allow_html=True )


with tab2:
    
    def generate_account_number():
        existing_account_numbers = []
        if os.path.exists('accounts.csv'):
            df = pd.read_csv('accounts.csv')
            existing_account_numbers = list(df['Account Number'])
        while True:
            account_number = ''.join(random.choices(string.digits, k=12))
            if account_number not in existing_account_numbers:
                return account_number
    
    form = st.form(key='account_creation_form',clear_on_submit=True)
    col1, col2 = form.columns(2)
    first_name = col1.text_input("First Name")
    last_name = col2.text_input("Last Name")
    gender = form.selectbox("Gender", ["Male", "Female"])
    address = form.text_area("Address")
    phone_number = form.text_input("Phone Number")    
    email = form.text_input("Email ID")
    initial_balance = form.number_input("Initial Balance", min_value=0.0)
    name = first_name + " " + last_name
    conn = sqlite3.connect('bank_database.db')
    
    # Validate the user input
    if form.form_submit_button("Submit"):
            # create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # create a trigger to set the DATE and TIME columns on insert
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS INST
        BEFORE INSERT ON CUSTOMERS
        FOR EACH ROW
        BEGIN
            UPDATE CUSTOMERS
            SET DATE = DATE('now'), TIME = TIME('now')
            WHERE rowid = NEW.rowid;
        END;
        """)

        cursor.execute("SELECT DATE('now') as current_date, TIME('now') as current_time")
        result = cursor.fetchone()

    # assign the values to temporary variables
        current_date = result[0]
        current_time = result[1]
    
        # commit the changes to the database and close the connection
        conn.commit()
        conn.close()
        
        if not all([first_name, last_name, phone_number, address, email]):
            st.warning("Please fill in all fields")
        elif not first_name.isalpha() or not last_name.isalpha():
            st.warning("Please enter only alphabets for First Name and Last Name")
        elif len(phone_number) != 10 or not phone_number.isnumeric():
            st.warning("Please enter a valid 10-digit phone number")
        elif not "@" in email or not "." in email or "@." in email:
            st.warning("Please enter a valid email address")
        else:
            st.success("Account created successfully!")
            account_number = generate_account_number()
            subject = "Account Created !"
            body = f"""Your account as been created with account number {account_number}"""
            with sqlite3.connect('bank_database.db') as bank_db:
                cursor = bank_db.cursor()
                #cursor.execute("CREATE TABLE customers (Account_number INTEGER, Name TEXT, Gender TEXT, Address TEXT, Phone_number TEXT, Email TEXT, Balance REAL, Date TEXT, Time TEXT)")
                cursor.execute("INSERT INTO customers VALUES ( ?, ?, ?, ?, ?, ?, ? , ? , ?)", (account_number,name, gender, address, phone_number, email, initial_balance,current_date,current_time))
                bank_db.commit()
                
                send_email(email , account_number , subject , body)
            
            st.write("## Account Details")
            st.write(f"**Account Number:** {account_number}")
            st.write(f"**Name:** {name}")
            st.write(f"**Gender:** {gender}")
            st.write(f"**Address:** {address}")
            st.write(f"**Phone Number:** {phone_number}")
            st.write(f"**Email:** {email}")
            st.write(f"**Initial Balance:** {initial_balance}")
            st.write(f"**Date:** {current_date}")
            st.write(f"**Time:** {current_time}")
            
            first_name = ""
            last_name = ""
            phone_number = ""
            address = ""
            email = ""
            name = ""
            initial_balance = 0.0
            form.empty() 
       
with tab3:
    
    def update_account(account_number, name , gender , address , phone_no , email , balance):
        with sqlite3.connect('bank_database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE customers SET Name=?, Gender=?, Address=?, Phone_number=?, Email=?, Balance=? WHERE Account_number=?',(name, gender, address, phone_no, email, balance, account_number))
            conn.commit()

        # Retrieve updated data from the database
        with sqlite3.connect('bank_database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT Account_number , Name , Gender , Address , Phone_number,Email FROM customers WHERE Account_number=?', (account_number,))
            data = cursor.fetchall()
            columns = ["Account Number", "Name", "Gender", "Address","Phone No" , "Email"]

            # Display the updated data in a table
            st.write("<h2 style='text-align: center;'>After Updating</h2>", unsafe_allow_html=True)
            st.write("<br><hr>", unsafe_allow_html=True)
            table = "<table><thead><tr>"
            for column in columns:
                table += f"<th>{column}</th>"
            table += "</tr></thead><tbody>"
            for row in data:
                table += "<tr>"
                for column in row:
                    table += f"<td>{column}</td>"
                table += "</tr>"         
            table += "</tbody></table>"
            st.write(f'<div style="display: flex; justify-content: center;">{table}</div>', unsafe_allow_html=True)
            st.write("<br><hr>", unsafe_allow_html=True)

    def get_account_info(account_number):
        # Create a connection to the SQLite database
        conn = sqlite3.connect('bank_database.db')
        cursor = conn.cursor()

        # Execute a SELECT query to retrieve the account information
        cursor.execute("SELECT * FROM customers WHERE Account_number = ?", (account_number,))
        row = cursor.fetchone()

        # Close the database connection
        conn.close()

        # Return the row of data (or None if no matching account was found)
        return row if row is not None else None
      
    form = st.form(key='update_creation_form',clear_on_submit=True)
    account_number=""
    account_number = form.text_input("Enter Account Number",value="")
    number = account_number
    account_number=""
    account_info = get_account_info(number)
    if form.form_submit_button("Get Account Info"):
        if account_info:
            data = [[account_info[0],account_info[1],account_info[2],account_info[3],account_info[4],account_info[5]]]
            columns = ["Account Number", "Name", "Gender", "Address","Phone No" , "Email"]

            st.write("<h2 style='text-align: center;'>Account Detail</h2>", unsafe_allow_html=True)
            st.write("<br><hr>", unsafe_allow_html=True)
            table = "<table><thead><tr>"
            for column in columns:
                table += f"<th>{column}</th>"
            table += "</tr></thead><tbody>"
            for row in data:
                table += "<tr>"
                for column in row:
                    table += f"<td>{column}</td>"
                table += "</tr>"
            table += "</tbody></table>"
            st.write(f'<div style="display: flex; justify-content: center;">{table}</div>', unsafe_allow_html=True)
            st.write("<br><hr>", unsafe_allow_html=True)

        else:
            st.warning("Account Not Found")
    
    if number != "": 
        
        st.write("<h2 style='font-size: 24px;'>Select an option</h2>",  unsafe_allow_html=True) 
        update = st.selectbox(" ", ["Name", "Gender" , "Address" , "Phone Number" , "Email"])

        if update == "Name":
            col1, col2 = st.columns(2)
            first_name = col1.text_input("First Name")
            last_name = col2.text_input("Last Name")
            name = first_name + " " + last_name
            if st.button("Update"):
                if not first_name.isalpha() or not last_name.isalpha():
                    st.warning("Please enter only alphabets for First Name and Last Name")
                else:
                    update_account(account_info[0] , name , account_info[2] , account_info[3] , account_info[4] ,account_info[5] , account_info[6] )
            
        elif update == "Gender":
            gender = st.selectbox("Gender  ", ["Male", "Female"])
            if st.button("Update "):
                update_account(account_info[0] , account_info[1] , gender , account_info[3] , account_info[4] ,account_info[5] , account_info[6] )
            
        elif update == "Address":
            address = st.text_area("Address")
            if st.button("Update  "):
                update_account(account_info[0] , account_info[1] , account_info[2] , address , account_info[4] ,account_info[5] , account_info[6] )
        
        elif update == "Phone Number":
            phone_number = st.text_input("Phone Number")
            if st.button("Update "):
                if len(phone_number) != 10 or not phone_number.isnumeric():
                    st.warning("Please enter a valid 10-digit phone number")
                else:
                    update_account(account_info[0] , account_info[1] , account_info[2], account_info[3] , phone_number ,account_info[5] , account_info[6] )    
        
        elif update == "Email":   
            email = st.text_input("Email ID")
            if st.button("Update     "):
                if not "@" in email or not "." in email or "@." in  email:
                    st.warning("Please enter a valid email address")
                else:
                    update_account(account_info[0] , account_info[1] , account_info[2] , account_info[3] , account_info[4] , email , account_info[6] )  
    else:
        st.warning("Enter the Account Number")   

with tab4:

    account_number = st.text_input("Account  Number ")
    
    if st.button("Delete"):
        # Create a connection to the SQLite database
        conn = sqlite3.connect('bank_database.db')
        cursor = conn.cursor()

        # Execute a DELETE query to remove the account from the database
        cursor.execute("DELETE FROM customers WHERE Account_number=?", (account_number,))
        rows_deleted = cursor.rowcount

        # If a row was deleted, show a success message and replace the CSV file with the new data
        if rows_deleted > 0:
            st.success("Account is successfully deleted" )
        else:
            st.warning("Account not found")
            
        conn.commit()
        conn.close()


with tab5:
    account_number = st.text_input("Account    Number")
    
    if st.button("Get Information"):
        # Create a connection to the SQLite database
        conn = sqlite3.connect('bank_database.db')
        cursor = conn.cursor()

        # Execute a SELECT query to find the account with the given account number
        cursor.execute("SELECT * FROM customers WHERE Account_number=?", (account_number,))
            
        data = cursor.fetchall()
        columns = ["Account Number", "Name", "Gender", "Address","Phone No" , "Email","Balance" , "Date" , "Time"]

        st.write("<h2 style='text-align: center;'>Account Detail</h2>", unsafe_allow_html=True)
        st.write("<br><hr>", unsafe_allow_html=True)
        table = "<table><thead><tr>"
        for column in columns:
            table += f"<th>{column}</th>"
        table += "</tr></thead><tbody>"
        for row in data:
            table += "<tr>"
            for column in row:
                table += f"<td>{column}</td>"
            table += "</tr>"
        table += "</tbody></table>"
        st.write(f'<div style="display: flex; justify-content: center;">{table}</div>', unsafe_allow_html=True)

with tab6:

    account_number = st.text_input("Account Number")
    credit_value = st.number_input("Credit Value", min_value=0.0)
    
    if st.button("Credit"):

        # Execute a SELECT query to find the account with the given account number
        
        db = BankDB()

        try:
            new_balance , email= db.credit_account(account_number, credit_value)
            print(f"New balance: {new_balance}")
            
            data = [[account_number,new_balance]]
            columns = ["Account Number", "Balance"]

            st.write("<h2 style='text-align: center;'>After Credit </h2>", unsafe_allow_html=True)
            st.write("<br><hr>", unsafe_allow_html=True)
            table = "<table><thead><tr>"
            for column in columns:
                table += f"<th>{column}</th>"
            table += "</tr></thead><tbody>"
            for row in data:
                table += "<tr>"
                for column in row:
                    table += f"<td>{column}</td>"
                table += "</tr>"
            table += "</tbody></table>"
            st.write(f'<div style="display: flex; justify-content: center;">{table}</div>', unsafe_allow_html=True)
            st.write("<br><hr>", unsafe_allow_html=True)
            
            subject = "Credited !"
            body = f"""${credit_value} as been credited to your account
                    Total balance : {new_balance}"""
            send_email(email , account_number , subject , body)
        except ValueError as e:
            print(str(e))
            
    

with tab7:

    account_number = st.text_input("Account  Number")
    debit_value = st.number_input("Debit Value", min_value=0.0)
    
    if st.button("Debit"):
        
        db = BankDB()

        try:
            new_balance , email  = db.debit_account(account_number, debit_value)
            print(f"New balance: {new_balance}")
            data = [[account_number,new_balance]]
            columns = ["Account Number", "Balance"]

            st.write("<h2 style='text-align: center;'>After Debit</h2>", unsafe_allow_html=True)
            st.write("<br><hr>", unsafe_allow_html=True)
            table = "<table><thead><tr>"
            for column in columns:
                table += f"<th>{column}</th>"
            table += "</tr></thead><tbody>"
            for row in data:
                table += "<tr>"
                for column in row:
                    table += f"<td>{column}</td>"
                table += "</tr>"
            table += "</tbody></table>"
            st.write(f'<div style="display: flex; justify-content: center;">{table}</div>', unsafe_allow_html=True)
            st.write("<br><hr>", unsafe_allow_html=True)
            
            subject = "Credited !"
            body = f"""${debit_value} as been debited to your account  
                    Total balance : {new_balance}"""
            send_email(email , account_number , subject , body)
        except ValueError as e:
            st.warning(str(e))
                
        
    
        
st.markdown("<br><hr><br>", unsafe_allow_html=True)

