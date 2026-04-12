from flask import Flask, render_template, request, redirect, session
import sqlite3, os, datetime

app = Flask(__name__)
app.secret_key = "store_secret_key"

DB = "store.db"

def get_db():
    return sqlite3.connect(DB)

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = cur.fetchone()

        if user:
            session["user"] = u
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid login")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        con = get_db()
        cur = con.cursor()
        cur.execute("INSERT INTO users(username,password) VALUES (?,?)", (u,p))
        con.commit()
        return redirect("/login")
    
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html")

@app.route("/add_item", methods=["GET","POST"])
def add_item():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["item_name"]
        size = request.form["size"]
        color = request.form["color"]
        qty = request.form["quantity"]
        price = request.form["price"]
        time = datetime.datetime.now()

        con = get_db()
        cur = con.cursor()
        cur.execute("""
            INSERT INTO inventory(item_name,size,color,quantity,price,timestamp)
            VALUES (?,?,?,?,?,?)
        """, (name,size,color,qty,price,time))
        con.commit()
        return redirect("/items")

    return render_template("add_item.html")

@app.route("/items")
def items():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM inventory ORDER BY id DESC")
    data = cur.fetchall()
    return render_template("items.html", data=data)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Render compatibility
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
