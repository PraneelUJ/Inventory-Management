from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector as con
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # A random secret key for session management

# Database connection
db = con.connect(
    host='localhost',
    user='root',
    passwd='shrutika123@',
    database='inventory_db'
)
cursor = db.cursor(dictionary=True)

@app.route("/", methods=["GET", "POST"])
def data():
    return render_template("admin_login.html")

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch admin credentials from the database
        cursor.execute(
            "SELECT * FROM admins WHERE username = %s", (username,)
        )
        admin = cursor.fetchone()

        # Check if admin exists and the password is correct
        if admin and password == admin['password']:  # Replace with hashed password check later
            session['admin_logged_in'] = True
            return redirect('/admin/dashboard')
        else:
            return "Invalid credentials, please try again."

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')  # Redirect to admin login if not logged in

    # Fetch item requests from the database
    cursor.execute("SELECT id, user_id, item_id, status FROM requests WHERE status = 'Pending'")
    requests = cursor.fetchall()
    
    return render_template('admin_dashboard.html', requests=requests)

if __name__ == '__main__':
    app.run(debug=True)

