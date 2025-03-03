import pandas as pd
from flask import Flask, render_template, request, redirect, send_file, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app and set the correct template folder
app = Flask(__name__, template_folder="templates")
app.secret_key = "secret_key"  # For session management

# Database connection function
def db_connection():
    # Ensure the database path is correct
    db_folder = "../database"
    db_file = os.path.join(db_folder, "data.db")
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    print(f"Database Path: {db_file}")
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

# Login route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("index.html", error="Please provide both email and password!")

        conn = db_connection()
        cursor = conn.cursor()

        # Query to validate user credentials
        query = "SELECT * FROM users WHERE email = ?"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            # Save user info in session
            session["username"] = user["email"]
            session["role"] = user["role"]

            # Redirect based on role
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        else:
            # If credentials are invalid
            return render_template("index.html", error="Invalid credentials!")

    return render_template("index.html")

# Admin dashboard route
@app.route("/admin")
def admin_dashboard():
    if "username" in session and session["role"] == "admin":
        return render_template("admin_dashboard.html", username=session["username"])
    return redirect(url_for("login"))

# User dashboard route
@app.route("/user")
def user_dashboard():
    if "username" in session and session["role"] == "user":
        return render_template("user_dashboard.html", username=session["username"])
    return redirect(url_for("login"))

# User setup route
@app.route("/user-setup", methods=["GET", "POST"])
def user_setup():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        role = request.form.get("role")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not all([email, first_name, last_name, role, password, confirm_password]):
            return render_template("userSetup.html", error="All fields are required!")

        if password != confirm_password:
            return render_template("userSetup.html", error="Passwords do not match!")

        hashed_password = generate_password_hash(password)  # Hash the password

        # Save user to the database
        conn = db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (email, password, first_name, last_name, role) VALUES (?, ?, ?, ?, ?)",
                (email, hashed_password, first_name, last_name, role)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("userSetup.html", error="Email already exists!")

    return render_template("userSetup.html")

# About route
@app.route("/about")
def about():
    return render_template("about.html")

# Home route
@app.route("/home")
def home():
    return render_template("home.html")

# Contact route
@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/vehicle-data", methods=["GET", "POST"])
def vehicle_data():
    message = None  # Message to display on the form page
    error = None    # Error to display on the form page
    
    if request.method == "POST":
        # Retrieve form data
        vehicle_number = request.form.get("vehicle_number")
        vin = request.form.get("vin")
        model_year = request.form.get("model_year")
        make = request.form.get("make")
        model = request.form.get("model")
        purchase_date = request.form.get("purchase_date")
        starting_mileage = request.form.get("starting_mileage")
        vehicle_weight = request.form.get("vehicle_weight")
        fuel_type = request.form.get("fuel_type")

        # Validate all required fields
        if not all([vehicle_number, vin, model_year, make, model, purchase_date, starting_mileage, vehicle_weight, fuel_type]):
            error = "All fields are required!"
            return render_template("vehicle_data.html", error=error)

        try:
            # Save data to the database
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO vehicles (vehicle_number, vin, model_year, make, model, purchase_date, starting_mileage, vehicle_weight, fuel_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (vehicle_number, vin, model_year, make, model, purchase_date, starting_mileage, vehicle_weight, fuel_type))
            conn.commit()
            conn.close()

            # Show success message
            message = "Vehicle data saved successfully!"
        except sqlite3.OperationalError as e:
            error = f"Database error: {e}"
        except Exception as e:
            error = f"An error occurred: {e}"

    return render_template("vehicle_data.html", message=message, error=error)

@app.route("/fueling-event", methods=["GET", "POST"])
def fueling_event():
    if request.method == "POST":
        vehicle_number = request.form.get("vehicle_number")
        date = request.form.get("date")
        current_mileage = request.form.get("current_mileage")
        fuel_added = request.form.get("fuel_added")
        fuel_cost = request.form.get("fuel_cost")

        if not all([vehicle_number, date, current_mileage, fuel_added, fuel_cost]):
            return render_template("fueling_event.html", error="All fields are required!")

        try:
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fueling_events (vehicle_number, date, current_mileage, fuel_added, fuel_cost)
                VALUES (?, ?, ?, ?, ?)
            """, (vehicle_number, date, current_mileage, fuel_added, fuel_cost))
            conn.commit()
            conn.close()
            return render_template("fueling_event.html", message="Fueling event saved successfully!")
        except sqlite3.Error as e:
            return render_template("fueling_event.html", error=f"Database error: {e}")

    return render_template("fueling_event.html")


@app.route("/maintenance-event", methods=["GET", "POST"])
def maintenance_event():
    if request.method == "POST":
        vehicle_number = request.form.get("vehicle_number")
        date = request.form.get("date")
        maintenance_cost = request.form.get("maintenance_cost")
        maintenance_description = request.form.get("maintenance_description")

        if not all([vehicle_number, date, maintenance_cost, maintenance_description]):
            return render_template("maintenance_event.html", error="All fields are required!")

        try:
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO maintenance_events (vehicle_number, date, maintenance_cost, maintenance_description)
                VALUES (?, ?, ?, ?)
            """, (vehicle_number, date, maintenance_cost, maintenance_description))
            conn.commit()
            conn.close()
            return render_template("maintenance_event.html", message="Maintenance event saved successfully!")
        except sqlite3.Error as e:
            return render_template("maintenance_event.html", error=f"Database error: {e}")

    return render_template("maintenance_event.html")



# Logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# 🛠️ Route for displaying reports
@app.route("/reports")
def reports():
    conn = db_connection()
    cursor = conn.cursor()

    # Query Fueling Events (Fuel Expenses by Month)
    cursor.execute("""
        SELECT strftime('%Y-%m', date) as month, SUM(fuel_cost) as total_fuel_cost 
        FROM fueling_events 
        GROUP BY month 
        ORDER BY month
    """)
    fuel_data = cursor.fetchall()
    months = [row["month"] for row in fuel_data]
    fuel_expenses = [row["total_fuel_cost"] for row in fuel_data]

    # Query Miles Driven (By Month)
    cursor.execute("""
        SELECT strftime('%Y-%m', date) as month, SUM(current_mileage) as total_miles 
        FROM fueling_events 
        GROUP BY month 
        ORDER BY month
    """)
    mileage_data = cursor.fetchall()
    miles_driven = [row["total_miles"] for row in mileage_data]

    # Query Maintenance Expenses (By Month)
    cursor.execute("""
        SELECT strftime('%Y-%m', date) as month, SUM(maintenance_cost) as total_maintenance_cost 
        FROM maintenance_events 
        GROUP BY month 
        ORDER BY month
    """)
    maintenance_data = cursor.fetchall()
    maintenance_expenses = [row["total_maintenance_cost"] for row in maintenance_data]

    # Fetch All Vehicles with Fuel Efficiency
    cursor.execute("""
        SELECT vehicle_number, model_year, starting_mileage as current_mileage, 
               (SELECT SUM(current_mileage) / SUM(fuel_added) FROM fueling_events WHERE fueling_events.vehicle_number = vehicles.vehicle_number) as mpg
        FROM vehicles
    """)
    vehicles = cursor.fetchall()

    # Fetch Maintenance Events
    cursor.execute("""
        SELECT vehicle_number, date, maintenance_cost, maintenance_description 
        FROM maintenance_events
    """)
    maintenance_events = cursor.fetchall()

    conn.close()

    return render_template("reports.html",
                           months=months,
                           fuel_expenses=fuel_expenses,
                           miles_driven=miles_driven,
                           maintenance_expenses=maintenance_expenses,
                           vehicles=vehicles,
                           maintenance_events=maintenance_events)

@app.route("/download-report")
def download_report():
    conn = db_connection()
    cursor = conn.cursor()

    # Fetch all fueling events
    cursor.execute("SELECT id, vehicle_number, date, current_mileage, fuel_added, fuel_cost FROM fueling_events")
    fueling_events = cursor.fetchall()

    # Fetch all maintenance events
    cursor.execute("SELECT id, vehicle_number, date, maintenance_cost, maintenance_description FROM maintenance_events")
    maintenance_events = cursor.fetchall()

    # Convert to DataFrame
    fuel_df = pd.DataFrame(fueling_events, columns=["ID", "Vehicle Number", "Date", "Current Mileage", "Fuel Added", "Fuel Cost"])
    maintenance_df = pd.DataFrame(maintenance_events, columns=["ID", "Vehicle Number", "Date", "Maintenance Cost", "Description"])

    # Ensure the 'database' directory exists
    report_dir = "database"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)  # Create 'database' directory if it does not exist

    report_path = os.path.join(report_dir, "vehicle_report.xlsx")

    # Save as an Excel file
    with pd.ExcelWriter(report_path) as writer:
        fuel_df.to_excel(writer, sheet_name="Fueling Events", index=False)
        maintenance_df.to_excel(writer, sheet_name="Maintenance Events", index=False)

    conn.close()

    return send_file(report_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
