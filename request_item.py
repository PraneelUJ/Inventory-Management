from flask import Flask, render_template, request, flash, redirect
import pymysql
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MySQL Configuration
db = pymysql.connect(
    host="localhost",  
    user="root",  
    password="shrutika123@",  
    database="inventory_db"  
)

@app.route('/')
def home():
    return redirect('/request_item')

@app.route('/request_item', methods=['GET', 'POST'])
def request_item():
    if request.method == 'POST':
        item_id = request.form['item_id']
        quantity = request.form['quantity']
        purpose = request.form['purpose']
        # user_id = session.get('user_id')  # Assuming user is logged in and session stores user_id
        
        cursor = db.cursor()
        query = """
                INSERT INTO requests (item_id, quantity, purpose, status)
                VALUES (%s, %s, %s, 'Pending')
            """
        cursor.execute(query, (item_id, quantity, purpose))
        db.commit()
        flash('Request submitted successfully!')
        return redirect('/request_item')

    
    # Fetch items from the database for the dropdown menu
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM items WHERE status = 'Available'")
    items = cursor.fetchall()
    return render_template('request_item.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)