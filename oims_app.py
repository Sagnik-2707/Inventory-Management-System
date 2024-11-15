import streamlit as st
import sqlite3
from datetime import datetime
from hashlib import sha256
import pandas as pd

# Database setup
def init_db():
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    
    # User table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY, 
                    username TEXT, 
                    password TEXT)''')
    
    # Inventory table
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    item_id INTEGER PRIMARY KEY, 
                    item_name TEXT, 
                    stock INTEGER, 
                    threshold INTEGER, 
                    price REAL, 
                    supplier_id INTEGER)''')
    
    # Populate inventory with sample SKUs if empty
    c.execute("SELECT COUNT(*) FROM inventory")
    if c.fetchone()[0] == 0:
        sample_data = [
            ("SKU1", 50, 10, 100.0),
            ("SKU2", 20, 5, 200.0),
            ("SKU3", 15, 5, 150.0),
            ("SKU4", 30, 10, 300.0),
            ("SKU5", 40, 15, 120.0),
            ("SKU6", 5, 2, 80.0),
            ("SKU7", 25, 8, 90.0),
            ("SKU8", 35, 10, 130.0),
            ("SKU9", 10, 3, 160.0),
            ("SKU10", 8, 4, 140.0)
        ]
        c.executemany("INSERT INTO inventory (item_name, stock, threshold, price) VALUES (?, ?, ?, ?)", sample_data)
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    hashed_password = sha256(password.encode()).hexdigest()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    hashed_password = sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    data = c.fetchone()
    conn.close()
    return data

# Low Stock Alert System
def low_stock_alerts():
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    c.execute("SELECT item_id, item_name, stock, threshold FROM inventory")
    data = c.fetchall()
    conn.close()
    
    st.subheader("Low Stock Alerts System")
    st.write("Current stock levels and thresholds:")

    # Convert data to DataFrame for better display
    df = pd.DataFrame(data, columns=["Item ID", "Item Name", "Stock", "Threshold"])
    st.table(df)

    # Remove stock functionality
    selected_item = st.selectbox("Select an Item to Remove Stock", df["Item Name"])
    remove_quantity = st.number_input("Quantity to Remove", min_value=1, value=1)
    if st.button("Remove Stock"):
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT stock, threshold FROM inventory WHERE item_name = ?", (selected_item,))
        stock, threshold = c.fetchone()
        new_stock = stock - remove_quantity
        if new_stock < 0:
            st.warning("Cannot have negative stock. Check the removal quantity.")
        else:
            # Update stock in database
            c.execute("UPDATE inventory SET stock = ? WHERE item_name = ?", (new_stock, selected_item))
            conn.commit()
            st.success(f"Removed {remove_quantity} from {selected_item}. New stock is {new_stock}.")
            
            # Trigger alert if stock falls below threshold
            if new_stock < threshold:
                st.error(f"Alert: {selected_item} stock is below the threshold! Current stock: {new_stock}, Threshold: {threshold}")
        conn.close()

# Other Inventory Functionalities

def update_inventory():
    st.subheader("Update Inventory")
    st.write("Functionality for updating inventory here...")

def order_tracking():
    st.subheader("Order Tracking")
    st.write("Functionality for tracking orders here...")

def reporting_analytics():
    st.subheader("Reporting and Analytics")
    st.write("Functionality for displaying reports and analytics here...")

def display_supplier_details():
    st.subheader("Supplier Details")
    st.write("Functionality for displaying supplier details here...")

def delivery_tracking():
    st.subheader("Delivery Tracking")
    st.write("Functionality for tracking deliveries here...")

# Streamlit App

def main():
    st.title("Online Inventory Management System")
    st.sidebar.title("Navigation")
    menu = ["Login", "Register", "Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login Section")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.success(f"Welcome {username}!")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "Register":
        st.subheader("Create a New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        if st.button("Register"):
            register_user(new_user, new_password)
            st.success("You have successfully created an account!")
            st.info("Go to Login Menu to login")

    elif choice == "Dashboard":
        if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
            st.warning("Please login first.")
        else:
            st.subheader("Inventory Management Dashboard")
            st.sidebar.write("## Functions")
            functions = [
                "Low Stock Alerts",
                "Update Inventory",
                "Order Tracking",
                "Reporting and Analytics",
                "Display Supplier Details",
                "Delivery Tracking"
            ]
            selected_function = st.sidebar.selectbox("Select Function", functions)

            if selected_function == "Low Stock Alerts":
                low_stock_alerts()
            elif selected_function == "Update Inventory":
                update_inventory()
            elif selected_function == "Order Tracking":
                order_tracking()
            elif selected_function == "Reporting and Analytics":
                reporting_analytics()
            elif selected_function == "Display Supplier Details":
                display_supplier_details()
            elif selected_function == "Delivery Tracking":
                delivery_tracking()

# Initialize Database and Run App
if __name__ == '__main__':
    init_db()
    main()
