import sqlite3
from flask import Flask, render_template, redirect, url_for, request, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# --------------------------
# DATABASE INITIALIZATION
# --------------------------
def init_db():
    conn = sqlite3.connect("store.db")
    c = conn.cursor()

    # Users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Inventory table
    c.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT,
        size TEXT,
        color TEXT,
        quantity INTEGER,
        price REAL,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()

# --------------------------
# HOME ➜ REDIRECT LOGIN
# --------------------------
@app.route("/")
def home():
    return redirect(url_for("login"))

# --------------------------
# REGISTER
# --------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("store.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users(username, password) VALUES(?, ?)", (username, password))
            conn.commit()
        except:
            return render_template("register.html", message="User already exists")

        return redirect(url_for("login"))

    return render_template("register.html")

# --------------------------
# LOGIN
# --------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("store.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", message="Invalid login")

    return render_template("login.html")

# --------------------------
# DASHBOARD
# --------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", username=session["user"])

# --------------------------
# ADD INVENTORY
# --------------------------
@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        item_name = request.form["item_name"]
        size = request.form["size"]
        color = request.form["color"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect("store.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO inventory (item_name, size, color, quantity, price, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_name, size, color, quantity, price, timestamp))
        conn.commit()
        conn.close()

        return redirect(url_for("transactions"))

    return render_template("add_item.html")

# --------------------------
# SHOW TRANSACTIONS
# --------------------------
@app.route("/transactions")
def transactions():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("store.db")
    c = conn.cursor()
    c.execute("SELECT * FROM inventory ORDER BY id DESC")
    data = c.fetchall()
    conn.close()

    return render_template("transactions.html", data=data)

# --------------------------
# ANALYTICS
# --------------------------
@app.route("/analytics")
def analytics():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("store.db")
    c = conn.cursor()

    # Total revenue calculation
    c.execute("SELECT SUM(quantity * price) FROM inventory")
    total_revenue = c.fetchone()[0]

    # Count of sales by size
    c.execute("SELECT size, SUM(quantity) FROM inventory GROUP BY size")
    size_data = c.fetchall()

    conn.close()

    return render_template("analytics.html", revenue=total_revenue, size_data=size_data)

# --------------------------
# LOGOUT
# --------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
