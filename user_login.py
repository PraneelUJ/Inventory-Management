from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector as con
from werkzeug.security import check_password_hash  # You may want to use this for password comparison

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
mydb = con.connect(
    host='localhost',
    user='root',
    passwd='shrutika123@',
    database='inventory_db'
)
cursor = mydb.cursor(dictionary=True)  # Fetch results as dictionary

@app.route("/", methods=["GET", "POST"])
def data():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT Password FROM users WHERE name = %s", (name,))
        result = cursor.fetchone()  # Fetch the first matching result

        if result and check_password_hash(result['password'], password):  # Check if the hashed password matches
            print("Login successful")
            return "Login successful"
        else:
            print("Incorrect username/password")
            message = "Incorrect username/password"
            return render_template("login.html", msg=message)

    # Render login form (for GET requests)
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)

