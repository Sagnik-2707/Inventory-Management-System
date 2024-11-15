import streamlit as st
import sqlite3
from datetime import datetime
from hashlib import sha256
import pandas as pd
import os

# Delete the existing database if it exists to avoid issues with outdated schema
if os.path.exists('inventory_management.db'):
    os.remove('inventory_management.db')

# Database setup
def init_db():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()

        # User table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY, 
                        username TEXT UNIQUE, 
                        password TEXT)''')

        # Inventory table with sample SKUs
        c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                        item_id INTEGER PRIMARY KEY, 
                        item_name TEXT UNIQUE, 
                        stock INTEGER, 
                        threshold INTEGER, 
                        price REAL, 
                        supplier_id INTEGER)''')

        # Create the orders table with order_date column
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
                        order_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        item_id INTEGER, 
                        quantity INTEGER, 
                        order_date TEXT, 
                        order_status TEXT,
                        FOREIGN KEY(item_id) REFERENCES inventory(item_id))''')

        # Populate inventory with sample SKUs if empty
        sample_data = [
            ("SKU1", 50, 10, 100.0, 1),
            ("SKU2", 20, 5, 200.0, 1),
            ("SKU3", 15, 5, 150.0, 2),
            ("SKU4", 30, 10, 300.0, 2),
            ("SKU5", 40, 15, 120.0, 3),
            ("SKU6", 5, 2, 80.0, 3),
            ("SKU7", 25, 8, 90.0, 4),
            ("SKU8", 35, 10, 130.0, 4),
            ("SKU9", 10, 3, 160.0, 5),
            ("SKU10", 8, 4, 140.0, 5)
        ]
        c.executemany("INSERT OR IGNORE INTO inventory (item_name, stock, threshold, price, supplier_id) VALUES (?, ?, ?, ?, ?)", sample_data)

        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    finally:
        conn.close()

# User management functions
def register_user(username, password):
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        hashed_password = sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Error during registration: {e}")
    finally:
        conn.close()

def login_user(username, password):
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        hashed_password = sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        data = c.fetchone()
        return data
    except sqlite3.Error as e:
        st.error(f"Error during login: {e}")
    finally:
        conn.close()

# Other functions like low_stock_alerts, update_inventory, place_order, etc. remain the same

# Main app
def main():
    st.title("Inventory Management System")

    menu = ["Login", "Register", "Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login to your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state['logged_in'] = True
                st.success("Logged in successfully.")
            else:
                st.error("Invalid username or password.")

    elif choice == "Register":
        st.subheader("Create a New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        if st.button("Register"):
            register_user(new_user, new_password)
            st.success("Account created successfully! Please log in.")

    elif choice == "Dashboard":
        dashboard()

# Initialize Database and Run App
if __name__ == "__main__":
    init_db()  # Initialize the database
    main()
