from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for
import mysql.connector as con
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'praneel'

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
            name = request.form["user"]
            naming = request.form["username"]
            purpose = request.form["purpose"]
            item_id = int(request.form["item_id"])
            qty = int(request.form["quantity"])
            status = "pending"
            
            print(name, purpose, item_id, qty, status)

            # Fetch item name from CulturalInventory
            cursor.execute("SELECT ItemName FROM CulturalInventory WHERE ID = %s", (item_id,))
            item_data = cursor.fetchone()

            if not item_data:
                return jsonify({"error": "Item not found"}), 404

            item_name = item_data[0]

            # Insert into requests table
            cursor.execute(
                "INSERT INTO requests (Item, naam, quantity, purpose, status_) VALUES (%s, %s, %s, %s, %s)",
                (item_name, name, qty, purpose, status)
            )
            mydb.commit()  # Commit the changes to the database

            print("Request successfully added:", (item_name, qty, purpose, status))

            cursor.execute("SELECT Club, Position FROM details WHERE Name = %s", (name,))
            club, pos = cursor.fetchone()

            return render_template("admin.html", name=name, position=pos, council=club)

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
        cursor.execute("SELECT Item, naam, status_, purpose, quantity FROM requests")
        requests_data = cursor.fetchall()
        requests = [
            {"item": row[0], "name": row[1], "status": row[2], "purpose": row[3], "quantity": row[4]}
            for row in requests_data
        ]
        print(requests)
        return jsonify(requests), 200
    except Exception as e:
        print(f"Error fetching requests: {e}")  # This will print the error message
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

@app.route('/approve', methods=['POST'])
def approve():
    if request.method == 'POST':
        # Fetch form data
        naam = request.form['naam']
        item = request.form['item']
        quantity = request.form['quantity']
        purpose = request.form['purpose']
        name=request.form['username']
        try:
            # Delete the request from the 'requests' table
            cursor.execute("""DELETE FROM requests WHERE naam = %s AND quantity = %s AND Item = %s AND purpose = %s AND TRIM(LOWER(status_)) = 'pending';""", (naam, quantity, item, purpose))
            mydb.commit()

            # Insert the request into the 'approved' table
            cursor.execute("""INSERT INTO approved (Item, naam, quantity, purpose) VALUES (%s, %s, %s, %s);""", (item, naam, quantity, purpose))
            cursor.execute("UPDATE CulturalInventory SET ItemQty = ItemQty - %s WHERE ItemName = %s", (quantity, item))
            mydb.commit()

            flash('Request approved successfully!', 'success')

            # Fetch club and position for the user
            cursor.execute("SELECT Club, Position FROM details WHERE Name = %s", (naam,))
            club, pos = cursor.fetchone()

            return render_template("admin.html", name=name, position=pos, council=club)
        
        except Exception as e:
            print(f"Error in approve function: {e}")
            mydb.rollback()
            flash('An error occurred while approving the request.', 'danger')

            # Fetch club and position for the user
            cursor.execute("SELECT Club, Position FROM details WHERE Name = %s", (name,))
            club, pos = cursor.fetchone()

            return render_template("admin.html", name=name, position=pos, council=club)

@app.route('/reject', methods=['POST'])
def reject_request():
    if request.method == 'POST':
        # Fetch form data
        naam = request.form['naam']
        name=request.form['username']
        item = request.form['item']
        quantity = request.form['quantity']
        purpose = request.form['purpose']
        
        # Delete the request from the 'requests' table
        cursor.execute("""DELETE FROM requests WHERE naam = %s AND quantity = %s AND Item = %s AND purpose = %s;""", (naam, quantity, item, purpose))
        mydb.commit()

        # Fetch club and position for the user
        cursor.execute("SELECT Club, Position FROM details WHERE Name = %s", (name,))
        club, pos = cursor.fetchone()

        return render_template("admin.html", name=name, position=pos, council=club)

if __name__ == "__main__":
    app.run(debug=True)
