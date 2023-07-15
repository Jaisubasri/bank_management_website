import sqlite3

class BankDB:
    def __init__(self):
        self.conn = sqlite3.connect('bank_database.db')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    """
    # create the stored procedures
        self.cursor.execute('''
            CREATE PROCEDURE debit_account_proc(account_number INT, debit_value FLOAT)
            BEGIN
                SELECT * FROM customers WHERE Account_number=account_number;
                UPDATE customers SET Balance = Balance - debit_value WHERE Account_number=account_number;
            END
        ''')

        self.cursor.execute('''
            CREATE PROCEDURE credit_account_proc(account_number INT, credit_value FLOAT)
            BEGIN
                SELECT * FROM customers WHERE Account_number=account_number;
                UPDATE customers SET Balance = Balance + credit_value WHERE Account_number=account_number;
            END
        ''')
    
    """
    
    def credit_account(self, account_number, credit_value):
        # Execute a SELECT query to find the account with the given account number
        self.cursor.execute("SELECT * FROM customers WHERE Account_number=?", (account_number,))
        account = self.cursor.fetchone()

        # If no account was found, raise an exception
        if account is None:
            raise ValueError("Account not found")
        else:
            # Update the credit balance of the account in the database
            new_balance = account[6] + credit_value
            self.cursor.execute("UPDATE customers SET Balance=? WHERE Account_number=?", (new_balance, account_number))
            self.conn.commit()

            return new_balance , account[5]

    def debit_account(self, account_number, debit_value):
        # execute a SELECT statement to retrieve the row for the specified account number
        self.cursor.execute("SELECT * FROM customers WHERE Account_number=?", (account_number,))

        # fetch the first row returned by the SELECT statement
        row = self.cursor.fetchone()

        # if a row was found, update the balance by subtracting the debit value
        if row:
            if(row[6] >= debit_value):
                new_balance = row[6] - debit_value
                # execute an UPDATE statement to update the balance in the row
                self.cursor.execute("UPDATE customers SET Balance=? WHERE Account_number=?", (new_balance, account_number))
                # commit the changes to the database
                self.conn.commit()

                return new_balance , row[5]
            else:
                raise ValueError("You don't have enough balance")
        else:
            raise ValueError("Account not found")