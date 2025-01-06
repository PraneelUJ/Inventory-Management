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
    return redirect('/manage_requests')

@app.route('/manage_requests', methods=['GET', 'POST'])
def manage_requests():
    if request.method == 'POST':
        request_id = request.form['request_id']
        action = request.form['action']
        
        cursor = db.cursor()
        if action == 'approve':
            query = "UPDATE requests SET status = 'Approved' WHERE id = %s"
        elif action == 'reject':
            query = "UPDATE requests SET status = 'Rejected' WHERE id = %s"
        cursor.execute(query, (request_id,))
        db.commit()
        flash('Request status updated successfully!')
        return redirect('/manage_requests')
    
    # Fetch all pending requests
    cursor = db.cursor()
    cursor.execute("""
        SELECT requests.id, items.name AS item_name, 
               users.name AS user_name, requests.quantity, 
               requests.purpose, requests.requested_at
        FROM requests
        JOIN items ON requests.item_id = items.id
        JOIN users ON requests.user_id = users.id
        WHERE requests.status = 'Pending'
    """)
    requests = cursor.fetchall()
    return render_template('manage_requests.html', requests=requests)

if __name__ == '__main__':
    app.run(debug=True)