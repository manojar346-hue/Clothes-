import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecret"

# -----------------------------------
# Database initialization
# -----------------------------------

def init_db():
    conn = sqlite3.connect("store.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            size TEXT,
            color TEXT,
            stock INTEGER,
            price REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
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

# -----------------------------------
# Home Route
# -----------------------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

# -----------------------------------
# Register
# -----------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("store.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")

# -----------------------------------
# Login
# -----------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("store.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Login!"

    return render_template("login.html")

# -----------------------------------
# Dashboard
# -----------------------------------

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# -----------------------------------
# Add Clothing Item
# -----------------------------------

@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        name = request.form["name"]
        size = request.form["size"]
        color = request.form["color"]
        stock = request.form["stock"]
        price = request.form["price"]

        conn = sqlite3.connect("store.db")
        c = conn.cursor()
        c.execute("INSERT INTO items (name, size, color, stock, price) VALUES (?, ?, ?, ?, ?)",
                  (name, size, color, stock, price))
        conn.commit()
        conn.close()

        return redirect(url_for("stock"))

    return render_template("add_item.html")

# -----------------------------------
# Show Stock
# -----------------------------------

@app.route("/stock")
def stock():
    conn = sqlite3.connect("store.db")
    c = conn.cursor()

    c.execute("SELECT * FROM items")
    items = c.fetchall()

    conn.close()
    return render_template("stock.html", items=items)

# -----------------------------------
# Sell Item
# -----------------------------------

@app.route("/sell_item", methods=["GET", "POST"])
def sell_item():
    if request.method == "POST":
        item_name = request.form["name"]
        size = request.form["size"]
        color = request.form["color"]
        qty = int(request.form["quantity"])

        conn = sqlite3.connect("store.db")
        c = conn.cursor()

        c.execute("SELECT stock, price FROM items WHERE name=? AND size=? AND color=?",
                  (item_name, size, color))
        item = c.fetchone()

        if not item:
            return "Item not found!"

        stock, price = item

        if qty > stock:
            return "Not enough stock!"

        new_stock = stock - qty

        c.execute("UPDATE items SET stock=? WHERE name=? AND size=? AND color=?",
                  (new_stock, item_name, size, color))

        c.execute("INSERT INTO transactions (item_name, size, color, quantity, price, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                  (item_name, size, color, qty, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()

        return redirect(url_for("transactions"))

    return render_template("sell_item.html")

# -----------------------------------
# Transactions
# -----------------------------------

@app.route("/transactions")
def transactions():
    conn = sqlite3.connect("store.db")
    c = conn.cursor()

    c.execute("SELECT * FROM transactions")
    data = c.fetchall()

    conn.close()
    return render_template("transactions.html", data=data)

# -----------------------------------
# Analytics
# -----------------------------------

@app.route("/analytics")
def analytics():
    conn = sqlite3.connect("store.db")
    c = conn.cursor()

    c.execute("SELECT item_name, SUM(quantity), SUM(price * quantity) FROM transactions GROUP BY item_name")
    report = c.fetchall()

    conn.close()
    return render_template("analytics.html", report=report)

# -----------------------------------
# Logout
# -----------------------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -----------------------------------
# Run Server (Render-compatible)
# -----------------------------------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
