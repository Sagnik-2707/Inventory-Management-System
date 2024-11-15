import streamlit as st
import sqlite3
from datetime import datetime
from hashlib import sha256
import pandas as pd

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

        # Order tracking table
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
                        order_id INTEGER PRIMARY KEY, 
                        item_id INTEGER, 
                        quantity INTEGER, 
                        status TEXT, 
                        FOREIGN KEY (item_id) REFERENCES inventory (item_id))''')

        # Sample orders for testing
        sample_orders = [
            (1, 1, 5, "Processing"),
            (2, 2, 3, "Shipped"),
            (3, 3, 7, "In Transit"),
            (4, 4, 2, "Delivered"),
            (5, 5, 10, "Processing"),
        ]
        c.executemany("INSERT OR IGNORE INTO orders (order_id, item_id, quantity, status) VALUES (?, ?, ?, ?)", sample_orders)

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

# Low Stock Alert and Inventory Display
def low_stock_alerts():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT item_id, item_name, stock, threshold FROM inventory")
        data = c.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching inventory data: {e}")
        return
    finally:
        conn.close()

    st.subheader("Low Stock Alerts System")
    st.write("Current stock levels and thresholds:")

    # Display data in a table format
    df = pd.DataFrame(data, columns=["Item ID", "Item Name", "Stock", "Threshold"])
    st.table(df)

    # Show alerts for items below threshold
    low_stock_items = df[df["Stock"] < df["Threshold"]]
    for index, row in low_stock_items.iterrows():
        st.error(f"Alert: {row['Item Name']} stock is below the threshold! Current stock: {row['Stock']}, Threshold: {row['Threshold']}")

# Inventory Update Function
def update_inventory():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT item_name, stock FROM inventory")
        items = c.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching inventory data: {e}")
        return
    finally:
        conn.close()

    st.subheader("Update Inventory Stock Levels")
    item_name = st.selectbox("Select an Item to Update Stock", [item[0] for item in items])
    new_stock = st.number_input("New Stock Quantity", min_value=0, value=0)

    if st.button("Update Stock"):
        try:
            conn = sqlite3.connect('inventory_management.db')
            c = conn.cursor()
            c.execute("UPDATE inventory SET stock = ? WHERE item_name = ?", (new_stock, item_name))
            conn.commit()
            st.success(f"Stock for {item_name} updated to {new_stock}.")
        except sqlite3.Error as e:
            st.error(f"Error updating stock: {e}")
        finally:
            conn.close()

        # Refresh Low Stock Alerts Table
        low_stock_alerts()

# Order Tracking Function
def order_tracking():
    st.subheader("Order Tracking System")
    order_id = st.number_input("Enter Order ID to Track", min_value=1, step=1)

    if st.button("Track Order"):
        try:
            conn = sqlite3.connect('inventory_management.db')
            c = conn.cursor()
            c.execute("SELECT order_id, item_id, quantity, status FROM orders WHERE order_id = ?", (order_id,))
            order_data = c.fetchone()
        except sqlite3.Error as e:
            st.error(f"Error tracking order: {e}")
        finally:
            conn.close()

        if order_data:
            order_id, item_id, quantity, status = order_data
            st.write(f"Order ID: {order_id}")
            st.write(f"Item ID: {item_id}")
            st.write(f"Quantity: {quantity}")
            st.write(f"Status: {status}")
        else:
            st.warning("Order ID not found.")

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
            functions = ["Low Stock Alerts", "Update Inventory", "Order Tracking"]
            selected_function = st.sidebar.selectbox("Select Function", functions)

            if selected_function == "Low Stock Alerts":
                low_stock_alerts()

            elif selected_function == "Update Inventory":
                update_inventory()

            elif selected_function == "Order Tracking":
                order_tracking()

# Initialize Database and Run App
if __name__ == '__main__':
    init_db()
    main()
