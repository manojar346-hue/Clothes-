from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secure_key"

# ✔ Use temporary folder for database (Render compatible)
DB = "/tmp/store.db"

# ---------------------- DATABASE SETUP ----------------------
def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        c = conn.cursor()

        c.execute("""
        CREATE TABLE users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        );
        """)

        c.execute("""
        CREATE TABLE items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            size TEXT,
            color TEXT,
            quantity INTEGER,
            price REAL,
            timestamp TEXT
        );
        """)

        conn.commit()
        conn.close()

init_db()

# ---------------------- HOME ----------------------
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

# ---------------------- REGISTER ----------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users(username, password) VALUES(?, ?)", (user, pw))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return "Username already exists!"

    return render_template("register.html")

# ---------------------- LOGIN ----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
        data = c.fetchone()
        conn.close()

        if data:
            session["user"] = user
            return redirect("/dashboard")
        else:
            return "Invalid username or password"

    return render_template("login.html")

# ---------------------- LOGOUT ----------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------------- DASHBOARD ----------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

# ---------------------- ADD ITEM ----------------------
@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        item_name = request.form["item_name"]
        size = request.form["size"]
        color = request.form["color"]
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO items(item_name, size, color, quantity, price, timestamp) VALUES(?,?,?,?,?,?)",
                  (item_name, size, color, quantity, price, timestamp))
        conn.commit()
        conn.close()

        return redirect("/transactions")

    return render_template("add_item.html")

# ---------------------- TRANSACTIONS ----------------------
@app.route("/transactions")
def transactions():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()

    return render_template("transactions.html", rows=rows)

# ---------------------- ANALYTICS ----------------------
@app.route("/analytics")
def analytics():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT item_name, SUM(quantity), SUM(quantity * price)
        FROM items
        GROUP BY item_name
    """)
    summary = c.fetchall()
    conn.close()

    return render_template("analytics.html", summary=summary)

# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
