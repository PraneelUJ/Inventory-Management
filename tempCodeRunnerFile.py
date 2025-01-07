import mysql.connector as con
from flask import Flask, render_template, request

app = Flask(__name__, static_folder='css')  # Use 'css' as the static folder

# Database connection
mydb = con.connect(
    host='localhost',
    user='root',
    passwd='tanishq20@5',
    database='inventory_management'
)
cursor = mydb.cursor()

@app.route("/",methods=["GET","POST"])
def data():
    return render_template ("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT Password FROM details WHERE Name = %s", (name,))
        result = cursor.fetchone()  

        if result and result[0] == password: 
            print("Login successful")
            return "Login successful"
        else:
            print("Incorrect username/password")
            message="Incorrect username/password"
            return render_template("login.html",msg=message)

    # Render login form (for GET requests)
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
