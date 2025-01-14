from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "shrutika123@",  
    "database": "inventory_db"  # Replace with your DB name
}

    # Connect to the database
@app.route('/')
def inventory_list():
    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Fetch inventory data (item, quantity, holder_name)
    query = "SELECT item, quantity, holder_name FROM approved"
    cursor.execute(query)
    inventory = cursor.fetchall()

    # Loop through the inventory and fetch the email for each holder_name
    updated_inventory = []
    for entry in inventory:
        holder_name = entry[2]
        print(f"Fetching email for holder_name: {holder_name}")  # Debugging output
        
        # Query to get the email of the user based on the holder_name
        cursor.execute("SELECT email FROM users WHERE name=%s", (holder_name,))
        email = cursor.fetchone()  # Fetch the email
        
        # Check if we got the email
        if email:
            print(f"Found email: {email[0]}")  # Debugging output
            entry_with_email = list(entry) + [email[0]]  # Append the email to the entry
        else:
            print("No email found.")  # Debugging output
            entry_with_email = list(entry) + [None]  # If no email found, append None
        
        # Add the updated entry to the list
        updated_inventory.append(entry_with_email)

    # Close the connection
    cursor.close()
    connection.close()

    # Pass the updated inventory to the template
    return render_template('public_page.html', inventory=updated_inventory)

    # Close the connection
    cursor.close()
    connection.close()

    # Pass the updated inventory to the template
    return render_template('public_page.html', inventory=updated_inventory)

if __name__ == '__main__':
    app.run(debug=True)

