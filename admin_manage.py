import mysql.connector as con
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)

# Secret key for sessions
app.secret_key = os.urandom(24)

# Database connection
mydb = con.connect(
    host='localhost',
    user='root',
    passwd='shrutika123@',
    database='inventory_management'
)
cursor = mydb.cursor()

@app.route("/", methods=["GET", "POST"])
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check credentials in the database
        cursor.execute("SELECT Password, Club, Position FROM details WHERE Name = %s", (username,))
        result = cursor.fetchone()

        if result:
            db_password, club, position = result
            if password == db_password:
                # Successful login
                session["username"] = username
                session["club"] = club
                session["position"] = position
                
                # Redirect admin to manage requests page
                if position.lower() == "admin":
                    return redirect(url_for("manage_requests"))
                
                # Redirect other users to their dashboard
                return render_template("user_dashboard.html", name=username, club=club, position=position)
            else:
                # Incorrect password
                flash("Incorrect password. Please try again.")
        else:
            # Username not found
            flash("Username not found. Please check your credentials.")

    return render_template("admin_login.html")

@app.route("/manage_requests", methods=["GET", "POST"])
def manage_requests():
    if "username" not in session or session.get("position", "").lower() != "admin":
        flash("Unauthorized access. Please log in as admin.")
        return redirect(url_for("login"))

    if request.method == "POST":
        request_id = request.form["request_id"]
        action = request.form["action"]

        try:
            if action == "approve":
                cursor.execute("UPDATE requests SET status = 'Approved' WHERE id = %s", (request_id,))
            elif action == "reject":
                cursor.execute("UPDATE requests SET status = 'Rejected' WHERE id = %s", (request_id,))
            mydb.commit()
            flash("Request updated successfully!")
        except Exception as e:
            print(f"Error updating request: {e}")
            flash("Failed to update request.")

    # Fetch pending requests
    cursor.execute("""
        SELECT r.id, i.ItemName, r.quantity, r.purpose, r.status 
        FROM requests r 
        JOIN CulturalInventory i ON r.item_id = i.ID 
        WHERE r.status = 'Pending'
    """)
    requests = cursor.fetchall()
    return render_template("manage_requests.html", requests=requests)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
