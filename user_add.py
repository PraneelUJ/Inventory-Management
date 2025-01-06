from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)

# MySQL Configuration
db = pymysql.connect(
    host="localhost",  
    user="root",  
    password="shrutika123@",  
    database="inventory_db"  
)
@app.route('/')
def index():
    # Redirect to the user registration form
    return render_template('user_add.html')

@app.route('/register', methods=['POST'])
def register():
    # Extract data from form
    name = request.form['name']  
    email = request.form['email']
    password = request.form['password']

    try:
        cursor = db.cursor()
        # Insert user into the database
        sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, email, password))
        db.commit()
        return "Registration successful!"
    except Exception as e:
        db.rollback()
        return f"An error occurred: {e}"
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug=True)


