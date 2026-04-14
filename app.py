from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"


# ---------- DB INIT ----------
def init_db():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
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


# ---------- LOGIN REQUIRED ----------
def login_required(route):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return route(*args, **kwargs)
    wrapper.__name__ = route.__name__
    return wrapper


# ---------- ROUTES ----------
@app.route("/")
def home():
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("store.db")
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect("/login")
        except:
            return "Username already exists!"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("store.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            session["user"] = username
            return redirect("/dashboard")

        return "Invalid login!"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/add_item", methods=["GET", "POST"])
@login_required
def add_item():
    if request.method == "POST":
        item_name = request.form["item_name"]
        size = request.form["size"]
        color = request.form["color"]
        quantity = request.form["quantity"]
        price = request.form["price"]

        conn = sqlite3.connect("store.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO inventory (item_name, size, color, quantity, price, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (item_name, size, color, quantity, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()

        return redirect("/transactions")

    return render_template("add_item.html")


@app.route("/transactions")
@login_required
def transactions():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM inventory ORDER BY id DESC")
    rows = cursor.fetchall()

    return render_template("transactions.html", data=rows)


@app.route("/analytics")
@login_required
def analytics():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()

    cursor.execute("SELECT item_name, SUM(quantity), SUM(quantity * price) FROM inventory GROUP BY item_name")
    report = cursor.fetchall()

    return render_template("analytics.html", report=report)


if __name__ == "__main__":
    app.run(debug=True)
