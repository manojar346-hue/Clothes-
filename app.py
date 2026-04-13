from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Dummy login details
USER = {
    "username": "admin",
    "password": "1234"
}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        if user == USER["username"] and pwd == USER["password"]:
            session["user"] = user
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", message="Invalid Login")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", username=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
