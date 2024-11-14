import streamlit as st
import sqlite3
from datetime import datetime
from hashlib import sha256

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
                    price REAL, 
                    supplier_id INTEGER)''')
    
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY, 
                    item_id INTEGER, 
                    quantity INTEGER, 
                    order_status TEXT, 
                    delivery_status TEXT, 
                    date TEXT)''')
    
    # Suppliers table
    c.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id INTEGER PRIMARY KEY, 
                    supplier_name TEXT, 
                    contact_info TEXT)''')
    
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

# Inventory Management Functionalities

def low_stock_alerts(threshold=10):
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    c.execute("SELECT item_name, stock FROM inventory WHERE stock < ?", (threshold,))
    data = c.fetchall()
    conn.close()
    
    st.subheader("Low Stock Alerts")
    if data:
        for item, stock in data:
            st.write(f"Item: {item}, Stock: {stock}")
    else:
        st.write("No items are below the threshold stock level.")

def update_inventory(item_id, stock, price):
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    c.execute("UPDATE inventory SET stock = ?, price = ? WHERE item_id = ?", (stock, price, item_id))
    conn.commit()
    conn.close()
    st.success("Inventory updated successfully.")

def order_tracking(order_id):
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    data = c.fetchone()
    conn.close()
    
    st.subheader("Order Tracking")
    if data:
        st.write(f"Order ID: {data[0]}, Item ID: {data[1]}, Quantity: {data[2]}, Status: {data[3]}, Delivery Status: {data[4]}, Date: {data[5]}")
    else:
        st.warning("Order not found.")

def reporting_analytics():
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    c.execute("SELECT item_name, SUM(stock) FROM inventory GROUP BY item_name")
    stock_data = c.fetchall()
    conn.close()
    
    st.subheader("Inventory Stock Summary")
    for item_name, total_stock in stock_data:
        st.write(f"Item: {item_name}, Total Stock: {total_stock}")
    st.write("---")

def display_supplier_details():
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    c.execute("SELECT supplier_name, contact_info FROM suppliers")
    data = c.fetchall()
    conn.close()
    
    st.subheader("Supplier Details")
    for supplier, contact in data:
        st.write(f"Supplier: {supplier}, Contact Info: {contact}")

def delivery_tracking(order_id):
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    c.execute("SELECT delivery_status FROM orders WHERE order_id = ?", (order_id,))
    data = c.fetchone()
    conn.close()
    
    st.subheader("Delivery Tracking")
    if data:
        st.write(f"Delivery Status: {data[0]}")
    else:
        st.warning("Order not found.")

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
                st.subheader("Low Stock Alerts")
                threshold = st.number_input("Enter Stock Threshold", min_value=1, value=10)
                low_stock_alerts(threshold)

            elif selected_function == "Update Inventory":
                st.subheader("Update Inventory")
                item_id = st.number_input("Enter Item ID", min_value=1)
                new_stock = st.number_input("New Stock Quantity", min_value=0)
                new_price = st.number_input("New Price", min_value=0.0)
                if st.button("Update"):
                    update_inventory(item_id, new_stock, new_price)

            elif selected_function == "Order Tracking":
                st.subheader("Order Tracking")
                order_id = st.number_input("Enter Order ID", min_value=1)
                if st.button("Track Order"):
                    order_tracking(order_id)

            elif selected_function == "Reporting and Analytics":
                reporting_analytics()

            elif selected_function == "Display Supplier Details":
                display_supplier_details()

            elif selected_function == "Delivery Tracking":
                st.subheader("Delivery Tracking")
                order_id = st.number_input("Enter Order ID", min_value=1)
                if st.button("Track Delivery"):
                    delivery_tracking(order_id)

# Initialize Database and Run App
if __name__ == '__main__':
    init_db()
    main()
