from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for
import mysql
import mysql.connector as con
import requests
from flask_cors import CORS
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
CORS(app)
app.secret_key = 'praneel'

from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change if using a different email provider
app.config['MAIL_PORT'] = 587  # 465 for SSL
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '23110254@iitgn.ac.in'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'ncam utkw qnzv jdsv'  # Use App Password for security
app.config['MAIL_DEFAULT_SENDER'] = '23110254@iitgn.ac.in'

mail = Mail(app)

mydb = con.connect(
    host='localhost',
    user='root',
    passwd='tanishq20@5',
    database='inventory_management'
)
cursor = mydb.cursor()

GOOGLE_CLIENT_ID = "669359779182-djs6p4jjp9dfogpb3lakcqnu0rnbdanf.apps.googleusercontent.com"

from datetime import datetime,timedelta

from datetime import datetime
from flask_mail import Message

def send_reminders():
    current = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT * FROM approved")
    approval = cursor.fetchall()

    for i in approval:
        x = i[6]
        d1 = datetime.strptime(str(current), "%Y-%m-%d %H:%M:%S")
        d2 = datetime.strptime(str(x), "%Y-%m-%d %H:%M:%S")
        diff = (d2 - d1)

        if diff.total_seconds() == 86400:
            naam = i[1]
            email = i[4]
            print(email)
            email = 'praneeluj@gmail.com'
            subject = 'Reminder mail for returning item in 24 hours'
            body = f"""
            Dear Student,

            Your item is due in 24 hrs.

            Request Details:
            - User: {naam}
            - Item: {i[0]}
            - Quantity: {i[2]}
            - Purpose: {i[3]}
            - Requested From: {i[5]}
            - Requested To: {i[6]}

            Please return the item before the due datetime.

            Regards,  
            Cultural Inventory System
            """

            try:
                msg = Message(subject, recipients=[email], body=body)
                mail.send(msg)
                print(f"Email sent to {email}")
            except Exception as e:
                print(f"Email sending error", {e})

        elif diff.total_seconds() <= 0:
            naam = i[1]
            email = i[4]
            print(email)
            email = 'praneeluj@gmail.com'
            subject = 'Your item is overdue now, please return it with a fine'
            body = f"""
            Dear Student,

            Your item is overdue, please return it with the fine.

            Request Details:
            - User: {naam}
            - Item: {i[0]}
            - Quantity: {i[2]}
            - Purpose: {i[3]}
            - Requested From: {i[5]}
            - Requested To: {i[6]}

            Please return the item ASAP with the fine.

            Regards,  
            Cultural Inventory System
            """

            try:
                msg = Message(subject, recipients=[email], body=body)
                mail.send(msg)
                print(f"Email sent to {email}")
            except Exception as e:
                print(f"Email sending error", {e})
scheduler=BackgroundScheduler()
scheduler.add_job(send_reminders,"interval",minutes=1)
scheduler.start()

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
        frome, toe = None, None  # Initialize variables
        
        if request.method == "GET":
            # Fetch all items from CulturalInventory
            cursor.execute("SELECT ID, ItemName, ItemQty FROM CulturalInventory")
            data = cursor.fetchall()

            if not data:
                return jsonify([])  # Return an empty list if no items found

            inventory = [{"item_number": row[0], "item_name": row[1], "quantity": row[2]} for row in data]
            return jsonify(inventory), 200 

        elif request.method == "POST":
            # Get form data
            name = request.form.get("user")
            purpose = request.form.get("purpose")
            item_id = request.form.get("item_id")
            qty = request.form.get("quantity")
            frome = request.form.get("from")
            toe = request.form.get("to")
            
            

            # Convert date strings to MySQL-compatible format
            from datetime import datetime
            
            if frome:
                    try:
                        frome = datetime.strptime(frome, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
                        print(frome)
                    except ValueError:
                        return jsonify({"error": "Invalid 'from' date format"}), 400

            if toe:
                    try:
                        toe = datetime.strptime(toe, "%Y-%m-%dT%H:%M").strftime("%Y-%m-%d %H:%M:%S")
                        print(toe)
                    except ValueError:
                        return jsonify({"error": "Invalid 'to' date format"}), 400
            print(frome," ", toe)
            # Validate inputs
            if not all([name, purpose, item_id, qty]):
                return jsonify({"error": "Missing required fields"}), 400

            try:
                item_id = int(item_id)
                qty = int(qty)
            except ValueError:
                return jsonify({"error": "Invalid data type for item_id or quantity"}), 400

            status = "pending"

            # Fetch item name from CulturalInventory
            cursor.execute("SELECT ItemName FROM CulturalInventory WHERE ID = %s", (item_id,))
            item_data = cursor.fetchone()

            if not item_data:
                return jsonify({"error": "Item not found"}), 404

            item_name = item_data[0]

            # Insert into requests table
            cursor.execute(
                "INSERT INTO requests (Item, naam, quantity, purpose, status_, frome, toe) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (item_name, name, qty, purpose, status, frome, toe)
            )
            mydb.commit()

            # Fetch user details
            cursor.execute("SELECT Club, Position FROM details WHERE Name = %s", (name,))
            user_data = cursor.fetchone()

            if user_data:
                club, pos = user_data
            else:
                club, pos = "Unknown Club", "Unknown Position"
            
            admin_email="23110254@iitgn.ac.in"
            subject="New Item Request for approval"
            body=f"""
            Dear Admin,
            
            A new request is pending for approval.
            
            Request Details:
            - User: {name}
            - Item: {item_name}
            - Quantity: {qty}
            - Purpose: {purpose}
            - Requested From: {frome}
            - Requested To: {toe}

            Please review and approve the request.

            Regards,
            Cultural Inventory System
            """
            
            try:
                msg=Message(subject,recipients=[admin_email],body=body)
                mail.send(msg)
            except Exception as e:
                print(f"Email sending error",{e})
            

            return render_template("admin.html", name=name, position=pos, council=club)

    except mysql.connector.Error as db_err:
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database operation failed"}), 500
    except Exception as e:
        print(f"Unexpected error in request_item: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500



        return jsonify({"error": "Invalid request method"}), 405

    except mysql.connector.Error as db_err:
        return jsonify({"error": "Database operation failed"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500


@app.route("/requests", methods=["GET"])
def get_requests():
    try:
        cursor.execute("SELECT Item, naam, status_, purpose, quantity, frome,toe FROM requests")
        requests_data = cursor.fetchall()
        requests = [
            {"item": row[0], "name": row[1], "status": row[2], "purpose": row[3], "quantity": row[4],"from":row[5],"to":row[6]}
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
        name = request.form['username']
        frome_str=request.form.get('from')
        toe_str=request.form.get('to')
        
        from datetime import datetime
        frome = None
        toe = None
        if frome_str:
                try:
                    frome = datetime.strptime(frome_str, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return jsonify({"error": "Invalid 'from' date format"}), 400

        if toe_str:
                try:
                    toe = datetime.strptime(toe_str, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return jsonify({"error": "Invalid 'to' date format"}), 400

        try:
            # Fetch email for the user
            cursor.execute("SELECT Email, Club, Position FROM details WHERE Name = %s", (name,))
            result = cursor.fetchone()
            if not result:
                flash('User details not found.', 'danger')
                return redirect('/login')  # Adjust the redirect as per your flow

            email, club, pos = result

            # Delete the request from the 'requests' table
            print([naam,item,quantity,purpose,name])
            cursor.execute("""
                DELETE FROM requests 
                WHERE naam = %s AND quantity = %s AND Item = %s AND purpose = %s 
                AND TRIM(LOWER(status_)) = 'pending' AND frome=%s AND toe = %s;
            """, (naam, quantity, item, purpose,frome,toe))
            mydb.commit()

            # Insert the request into the 'approved' table with email
            cursor.execute("""
                INSERT INTO approved (Item, naam, quantity, purpose, email,frome,toe) 
                VALUES (%s, %s, %s, %s, %s,%s,%s);
            """, (item, naam, quantity, purpose, email,frome,toe))

            # Update the inventory
            cursor.execute("""
                UPDATE CulturalInventory 
                SET ItemQty = ItemQty - %s 
                WHERE ItemName = %s;
            """, (quantity, item))
            mydb.commit()
            
            sender_email=email
            print(email)
            sender_email="praneeluj@gmail.com"
            
            subject="Request of item approved"
            
            body=f"""
            Dear {naam},
            
            Your request of {item} of quantity {quantity} from {frome} to {toe} has been 
            approved.
            
            Regards,
            Cultural Inventory System
            """
            
            try:
                msg = Message(subject, recipients=[sender_email], body=body)
                mail.send(msg)
            except Exception as email_err:
                print(f"Email sending failed: {email_err}")


            flash('Request approved successfully!', 'success')
            return render_template("admin.html", name=name, position=pos, council=club)

        except Exception as e:
            print(f"Error in approve function: {e}")
            mydb.rollback()
            flash('An error occurred while approving the request.', 'danger')

            # Fetch club and position for the user again in case of error
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
        frome_str=request.form.get('from')
        toe_str=request.form.get('to')
        
        from datetime import datetime
        
        if frome_str:
                try:
                    frome = datetime.strptime(frome_str, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return jsonify({"error": "Invalid 'from' date format"}), 400

        if toe_str:
                try:
                    toe = datetime.strptime(toe_str, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return jsonify({"error": "Invalid 'to' date format"}), 400
        
        # Delete the request from the 'requests' table
        cursor.execute("""DELETE FROM requests WHERE naam = %s AND quantity = %s AND Item = %s AND purpose = %s AND frome = %s AND toe = %s;""", 
                       (naam, quantity, item, purpose,frome,toe))
        mydb.commit()

        # Fetch club and position for the user
        cursor.execute("SELECT Email, Club, Position FROM details WHERE Name = %s", (name,))
        email,club, pos = cursor.fetchone()
        
        sender_email=email
        print(email)
        sender_email="praneeluj@gmail.com"
            
        subject="Request of item approved"
            
        body=f"""
            Dear {naam},
            
            Your request of {item} of quantity {quantity} from {frome} to {toe} has been 
            rejected.
            
            Regards,
            Cultural Inventory System
            """
            
        try:
                msg = Message(subject, recipients=[sender_email], body=body)
                mail.send(msg)
        except Exception as email_err:
                print(f"Email sending failed: {email_err}")

        return render_template("admin.html", name=name, position=pos, council=club)
@app.route('/approvedtable', methods=['GET', 'POST'])
def approvedtable():
    try:
        # Execute query to fetch approved items
        cursor.execute("SELECT Item, naam, quantity, purpose, email,frome,toe FROM approved")
        items = cursor.fetchall()

        # Format the results into a list of dictionaries
        inventory = [
    {"Item": row[0], "Holder_Name": row[1], "Quantity": row[2], "Purpose": row[3], "Email": row[4],
     "From": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else None,
     "To": row[6].strftime("%Y-%m-%d %H:%M:%S") if row[6] else None}
    for row in items
]


        # Return the JSON response
        return jsonify(inventory), 200

    except mysql.connector.Error as db_err:
        # Handle database-specific errors
        print(f"Database error: {db_err}")
        return jsonify({"error": "Database operation failed"}), 500

    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error in approvedtable: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/add_item', methods=["POST"])
def add_item():
    item = request.form['item_name'].strip().lower()
    quantity = int(request.form['quantity'])
    name=request.form['user']

    # Fetch all existing items with their IDs
    cursor.execute("SELECT ID, LOWER(ItemName) FROM CulturalInventory")
    existing_items = {name: id for id, name in cursor.fetchall()}

    if item in existing_items:
        # If item exists, update its quantity
        cursor.execute("""
            UPDATE CulturalInventory 
            SET ItemQty = ItemQty + %s 
            WHERE ID = %s;
        """, (quantity, existing_items[item]))
    else:
        # Find the next available ID
        cursor.execute("SELECT MAX(ID) FROM CulturalInventory")
        max_id = cursor.fetchone()[0]  # Get the highest ID
        new_id = (max_id + 1) if max_id else 1  # Assign next ID
        item=item.capitalize()
        # Insert new item with new ID
        cursor.execute("""
            INSERT INTO CulturalInventory (ID, ItemName, ItemQty)
            VALUES (%s, %s, %s)
        """, (new_id, item, quantity))
        mydb.commit()

    cursor.execute("SELECT Email, Club, Position FROM details WHERE Name = %s", (name,))
    email,club, pos = cursor.fetchone()
    return render_template("admin.html", name=name, position=pos, council=club)

    
    
    
if __name__ == "__main__":
    app.run(debug=True)


