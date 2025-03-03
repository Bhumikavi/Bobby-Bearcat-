import sqlite3
import os

# Function to establish a database connection
def db_connection():
    # Correct cross-platform path handling
    db_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database"))
    db_file = os.path.join(db_folder, "data.db")

    if not os.path.exists(db_folder):
        os.makedirs(db_folder)

    print(f"✅ Database Path: {db_file}")  # Debugging output
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

# Function to set up the database and create tables
def setup_database():
    conn = db_connection()
    cursor = conn.cursor()

    # Drop and recreate the 'users' table
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin', 'user')) NOT NULL
    );
    """)

    # Add sample users
    cursor.execute("""
    INSERT INTO users (email, password, first_name, last_name, role) 
    VALUES ('admin@domain.com', 'admin123', 'Admin', 'User', 'admin')
    """)
    cursor.execute("""
    INSERT INTO users (email, password, first_name, last_name, role) 
    VALUES ('user@domain.com', 'user123', 'Regular', 'User', 'user')
    """)

    # Drop and recreate the 'vehicles' table
    cursor.execute("DROP TABLE IF EXISTS vehicles")
    cursor.execute("""
    CREATE TABLE vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_number TEXT UNIQUE NOT NULL,
        vin TEXT NOT NULL,
        model_year INTEGER NOT NULL,
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        purchase_date TEXT NOT NULL,
        starting_mileage INTEGER NOT NULL,
        vehicle_weight TEXT NOT NULL,
        fuel_type TEXT NOT NULL
    );
    """)

    # Drop and recreate the 'fueling_events' table
    cursor.execute("DROP TABLE IF EXISTS fueling_events")
    cursor.execute("""
    CREATE TABLE fueling_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_number TEXT NOT NULL,
        date TEXT NOT NULL,
        current_mileage INTEGER NOT NULL,
        fuel_added REAL NOT NULL,
        fuel_cost REAL NOT NULL,
        FOREIGN KEY(vehicle_number) REFERENCES vehicles(vehicle_number) ON DELETE CASCADE
    );
    """)

    # Drop and recreate the 'maintenance_events' table
    cursor.execute("DROP TABLE IF EXISTS maintenance_events")
    cursor.execute("""
    CREATE TABLE maintenance_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_number TEXT NOT NULL,
        date TEXT NOT NULL,
        maintenance_cost REAL NOT NULL,
        maintenance_description TEXT NOT NULL,
        FOREIGN KEY(vehicle_number) REFERENCES vehicles(vehicle_number) ON DELETE CASCADE
    );
    """)

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("✅ Database setup completed! 'users', 'vehicles', 'fueling_events', and 'maintenance_events' tables are ready.")

# Run the setup
if __name__ == "__main__":
    setup_database()
