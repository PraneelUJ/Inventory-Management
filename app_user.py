from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector as con
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # A random secret key for session management

# Database connection
mydb = con.connect(
    host='localhost',
    user='root',
    passwd='shrutika123@',
    database='inventory_db'
)
cursor = mydb.cursor(dictionary=True)  # Fetch results as dictionary

# Route to display login page
@app.route("/", methods=["GET", "POST"])
def data():
    return render_template("login.html")

# Login route to handle login logic
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT id, password FROM users WHERE name = %s", (name,))
        result = cursor.fetchone()  # Fetch the first matching result

        if result and result['password'] == password:
            session['user_id'] = result['id']  # Set user ID in session
            return redirect(url_for('request_item'))
        else:
            flash("Invalid username or password")
            return render_template("login.html")
    return render_template("login.html")


        # return render_template("login.html")
    

# Request Item Page route
@app.route('/request_item', methods=['GET', 'POST'])
def request_item():
    # Check if the user is logged in by verifying session
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login page if not logged in
    print(f"User logged in with user_id: {session['user_id']}")
    if request.method == 'POST':
        item_id = request.form['item_id']
        quantity = request.form['quantity']
        purpose = request.form['purpose']
        user_id = session['user_id']  # Get the logged-in user's ID from session

        cursor = mydb.cursor()
        query = """
                INSERT INTO requests (user_id, item_id, quantity, purpose, status, user)
                VALUES (%s, %s, %s, %s, 'Pending', %s)
            """  
        cursor.execute(query, (user_id, item_id, quantity, purpose, user_id))
        mydb.commit() 
        flash('Request submitted successfully!')
        return redirect('/request_item')  # Redirect to request_item page after submission

    # Fetch available items from the database for the dropdown menu
    cursor = mydb.cursor()
    cursor.execute("SELECT id, name FROM items WHERE status = 'Available'")
    items = cursor.fetchall()
    return render_template('request_item.html', items=items)

# Running the application
if __name__ == '__main__':
    app.run(debug=True)



    
