from flask import Flask, request, render_template, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# Home page
@app.route("/")
def home():
    return "Welcome to Smart Finance App!"

# Signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    message = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Save to database
        conn = sqlite3.connect("smart_finance.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            message = "User created successfully!"
        except sqlite3.IntegrityError:
            message = "Username already exists!"
        conn.close()
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("smart_finance.db")
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and user[1] == password:  # for now, plain password
            session["user_id"] = user[0]   # <-- MUST be set
            session["username"] = username
            return redirect("/dashboard")   # <-- redirect to dashboard
        else:
            return "Invalid credentials"     # or flash a message

    return render_template("login.html")
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = sqlite3.connect("smart_finance.db")
    c = conn.cursor()

    c.execute("SELECT type, amount, description FROM transactions WHERE user_id = ?", (user_id,))
    transactions = c.fetchall()

    conn.close()

    total_income = 0
    total_expense = 0

    for t in transactions:
        if t[0] == "income":
            total_income += t[1]
        else:
            total_expense += t[1]

    balance = total_income - total_expense

    return render_template(
        "dashboard.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance
    )
@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    type_ = request.form["type"]
    amount = request.form["amount"]
    description = request.form["description"]

    conn = sqlite3.connect("smart_finance.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO transactions (user_id, type, amount, description)
        VALUES (?, ?, ?, ?)
    """, (user_id, type_, amount, description))

    conn.commit()
    conn.close()

    return redirect("/dashboard") 


if __name__ == "__main__" :
    app.run(debug=True)