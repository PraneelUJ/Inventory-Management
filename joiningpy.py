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
        position = userinfo.get("position")
        
        cursor.execute("SELECT Position, Club FROM details WHERE Email = %s", (email,))
        userdata = cursor.fetchone()
        
        if userdata:
            position, club = userdata

            return jsonify({
                "success": True,
                "message": "OK",
                "name": name,
                "position": position
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "User Not Found",
                "name": name,
                "position": position
            }), 404
    else:
        return jsonify({"success": False, "message": "Invalid token"}), 400

@app.route("/request_item", methods=["GET", "POST"])
def request_item():
    try:
        if request.method == "POST":
            # Get form data
            purpose = request.form["purpose"]
            item_id = int(request.form["item_id"])
            qty = int(request.form["quantity"])
            status = "pending"

            # Fetch item name from CulturalInventory
            cursor.execute("SELECT ItemName FROM CulturalInventory WHERE ID = %s", (item_id,))
            item_data = cursor.fetchone()

            if not item_data:
                return jsonify({"error": "Item not found"}), 404

            item_name = item_data[0]

            # Insert into requests table
            cursor.execute(
                "INSERT INTO requests (Item, quantity, purpose, status_) VALUES (%s, %s, %s, %s)",
                (item_name, qty, purpose, status)
            )
            mydb.commit()  # Commit the changes to the database

            print("Request successfully added:", (item_name, qty, purpose, status))
            return redirect('/')

        # Fetch available inventory for GET request
        cursor.execute("SELECT ID, ItemName, ItemQty FROM CulturalInventory")
        items = cursor.fetchall()
        inventory = [
            {"item_number": row[0], "item_name": row[1], "quantity": row[2]}
            for row in items
            if row[2] > 0
        ]
        return jsonify(inventory), 200

    except Exception as e:
        print(f"Error in request_item: {e}")
        return jsonify({"error": "An error occurred while processing your requests"}), 500

@app.route("/requests", methods=["GET"])
def get_requests():
    try: 
        cursor.execute("SELECT  ID,Item, status_ FROM requests")
        requests_data = cursor.fetchall()
        requests = [
            { "item": row[0], "status": row[1]}
            for row in requests_data
        ]
        print(requests)
        return jsonify(requests), 200
    except Exception as e:
        print(f"Error fetching requests: {e}")
        return jsonify({"error": "Failed to fetch requests"}), 500


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
# @app.route("/requests",methods=["GET","POST"])
# def gettingrequests():
    


if __name__ == "__main__":
    app.run(debug=True)
