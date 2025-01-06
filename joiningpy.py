import mysql.connector as con
from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
app = Flask(__name__)
from flask_cors import CORS
CORS(app)

mydb = con.connect(
    host='localhost',
    user='root',
    passwd='tanishq20@5',
    database='inventory_management'
)
cursor = mydb.cursor()

GOOGLE_CLIENT_ID = "669359779182-djs6p4jjp9dfogpb3lakcqnu0rnbdanf.apps.googleusercontent.com"

@app.route("/", methods=["GET", "POST"])
def data():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]

        cursor.execute("SELECT Password FROM details WHERE Name = %s", (name,))
        result = cursor.fetchone()
        cursor.execute("SELECT Club FROM details WHERE Name = %s", (name,))
        club = cursor.fetchone()
        cursor.execute("SELECT Position FROM details WHERE Name = %s", (name,))
        pos = cursor.fetchone()

        if result and result[0] == password:
            print("Login successful")
            return render_template("admin.html", name=name, council=club[0], position=pos[0])
        else:
            print("Incorrect username/password")
            message = "Incorrect Username/Password"
            return render_template("login.html", msg=message)

    return render_template("login.html")

@app.route("/google-login", methods=["POST", "GET"])
def googlelogin():
    token = request.json.get("id_token")
    url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
    response = requests.get(url)
    userinfo = response.json()
    
    if response.status_code == 200:
        email = userinfo.get("email")
        name = userinfo.get("name")
        
        cursor.execute("SELECT Position, Club FROM details WHERE Email = %s", (email,))
        userdata = cursor.fetchone()
        
        if userdata:
            position, club = userdata
            # Pass data to admin.html using the redirect
            return jsonify({"success": True, "message": "OK"}), 200
        else:
            return jsonify({"success": False, "message": "User Not Found"}), 404
    else:
        return jsonify({"success": False, "message": "Invalid token"}), 400

@app.route("/admin", methods=["GET"])
def admin():
    # Fetching all items from CulturalInventory
    cursor.execute("SELECT ID, ItemName FROM CulturalInventory")
    items = cursor.fetchall()

    # Pass the items to the template
    return render_template("admin.html", items=items)

@app.route("/inventory", methods=["GET"])
def getdata():
    try:
        cursor.execute("SELECT ID, ItemName, ItemQty FROM CulturalInventory")
        data = cursor.fetchall()
        inventory = [{"item_number": row[0], "item_name": row[1], "quantity": row[2]} for row in data]
        return jsonify(inventory)
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return jsonify({"error": "Failed to fetch inventory"}), 500

if __name__ == "__main__":
    app.run(debug=True)
