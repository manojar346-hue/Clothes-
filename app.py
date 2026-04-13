from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

DB = "store.db"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
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

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return redirect("/login")

# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = u
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid login")

    return render_template("login.html")

# REGISTER
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username,password) VALUES (?,?)", (u,p))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

# ADD ITEM
@app.route("/add_item", methods=["GET","POST"])
def add_item():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        size = request.form["size"]
        color = request.form["color"]
        qty = request.form["quantity"]
        price = request.form["price"]

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO items(name,size,color,quantity,price,timestamp)
        VALUES (?,?,?,?,?,?)
        """, (name,size,color,qty,price, datetime.now()))
        conn.commit()
        conn.close()

        return redirect("/items")

    return render_template("add_item.html")

# VIEW ITEMS
@app.route("/items")
def items():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT * FROM items ORDER BY id DESC")
    data = cur.fetchall()
    conn.close()

    return render_template("items.html", data=data)

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
