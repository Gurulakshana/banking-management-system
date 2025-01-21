from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'


class Account:
    def __init__(self, account_number, name, initial_deposit):
        self.account_number = account_number
        self.name = name
        self.balance = initial_deposit  # Balance in INR
        self.transactions = []
        self.interest_rate = 0.01  # Default interest rate
        self.loans = {}
        self.transactions.append(f"Account opened with deposit of ₹{initial_deposit} on {datetime.now()}")

    def deposit(self, amount):
        self.balance += amount
        self.transactions.append(f"Deposited ₹{amount} on {datetime.now()}")
        return True

    def withdraw(self, amount):
        if amount > self.balance:
            print(f"Insufficient funds! Available balance: ₹{self.balance}")
            return False
        self.balance -= amount
        self.transactions.append(f"Withdrew ₹{amount} on {datetime.now()}")
        return True

    def apply_for_loan(self, loan_amount, interest_rate, loan_term_months):
        loan_id = len(self.loans) + 1
        self.loans[loan_id] = {
            "amount": loan_amount,
            "interest_rate": interest_rate,
            "loan_term": loan_term_months,
            "balance": loan_amount,
            "start_date": datetime.now()
        }
        self.transactions.append(f"Loan of ₹{loan_amount} applied with interest rate of {interest_rate}% for {loan_term_months} months")
        return loan_id

    def repay_loan(self, loan_id, payment):
        if loan_id not in self.loans:
            print("Invalid Loan ID!")
            return False
        loan = self.loans[loan_id]
        loan['balance'] -= payment
        if loan['balance'] <= 0:
            self.transactions.append(f"Loan ID {loan_id} fully repaid on {datetime.now()}")
            del self.loans[loan_id]
        else:
            self.transactions.append(f"Repayment of ₹{payment} made on Loan ID {loan_id} on {datetime.now()}")
        return True

    def accumulate_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        self.transactions.append(f"Accumulated ₹{interest} as interest on {datetime.now()}")

    def search_transactions(self, keyword):
        return [transaction for transaction in self.transactions if keyword.lower() in transaction.lower()]

    def view_account(self):
        return {
            "Account Number": self.account_number,
            "Name": self.name,
            "Balance (INR)": self.balance,
            "Transactions": self.transactions
        }

class BankSystem:
    def __init__(self):
        self.customers = {}

    def create_account(self, account_number, name, initial_deposit):
        if account_number in self.customers:
            return False
        account = Account(account_number, name, initial_deposit)
        self.customers[account_number] = account
        return True

    def deposit_money(self, account_number, amount):
        if account_number not in self.customers:
            return False
        account = self.customers[account_number]
        account.deposit(amount)
        return True

    def withdraw_money(self, account_number, amount):
        if account_number not in self.customers:
            return False
        account = self.customers[account_number]
        return account.withdraw(amount)

    def apply_for_loan(self, account_number, loan_amount, interest_rate, loan_term_months):
        if account_number not in self.customers:
            return False
        account = self.customers[account_number]
        loan_id = account.apply_for_loan(loan_amount, interest_rate, loan_term_months)
        return loan_id

    def repay_loan(self, account_number, loan_id, payment):
        if account_number not in self.customers:
            return False
        account = self.customers[account_number]
        return account.repay_loan(loan_id, payment)

    def search_transactions(self, account_number, keyword):
        if account_number not in self.customers:
            return None
        account = self.customers[account_number]
        return account.search_transactions(keyword)

    def view_account(self, account_number):
        if account_number not in self.customers:
            return None
        account = self.customers[account_number]
        return account.view_account()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        account_number = request.form['account_number']
        name = request.form['name']
        initial_deposit = float(request.form['initial_deposit'])
        if bank.create_account(account_number, name, initial_deposit):
            flash('Account created successfully!')
        else:
            flash('Account already exists!')
        return redirect(url_for('index'))
    return render_template('create_account.html')

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])
        bank.deposit_money(account_number, amount)
        flash('Money deposited successfully!')
        return redirect(url_for('index'))
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])
        if bank.withdraw_money(account_number, amount):
            flash('Money withdrawn successfully!')
        else:
            flash('Insufficient funds or account not found!')
        return redirect(url_for('index'))
    return render_template('withdraw.html')

@app.route('/apply_for_loan', methods=['GET', 'POST'])
def apply_for_loan():
    if request.method == 'POST':
        account_number = request.form['account_number']
        loan_amount = float(request.form['loan_amount'])
        interest_rate = float(request.form['interest_rate'])
        loan_term = int(request.form['loan_term'])
        loan_id = bank.apply_for_loan(account_number, loan_amount, interest_rate, loan_term)
        if loan_id:
            flash('Loan applied successfully!')
        else:
            flash('Account not found!')
        return redirect(url_for('index'))
    return render_template('loan.html')

@app.route('/repay_loan', methods=['GET', 'POST'])
def repay_loan():
    if request.method == 'POST':
        account_number = request.form['account_number']
        loan_id = int(request.form['loan_id'])
        payment = float(request.form['payment'])
        if bank.repay_loan(account_number, loan_id, payment):
            flash('Loan repayment successful!')
        else:
            flash('Invalid loan ID or account not found!')
        return redirect(url_for('index'))
    return render_template('repay_loan.html')

@app.route('/search_transactions', methods=['GET', 'POST'])
def search_transactions():
    transactions = []
    if request.method == 'POST':
        account_number = request.form['account_number']
        keyword = request.form['keyword']
        transactions = bank.search_transactions(account_number, keyword)
    return render_template('transactions.html', transactions=transactions)

@app.route('/view_account', methods=['GET', 'POST'])
def view_account():
    account_details = None
    if request.method == 'POST':
        account_number = request.form['account_number']
        account_details = bank.view_account(account_number)
    return render_template('account.html', account_details=account_details)

if __name__ == '__main__':
    bank = BankSystem()
    app.run(debug=True)
