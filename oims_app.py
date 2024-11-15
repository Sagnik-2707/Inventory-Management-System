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

        # Drop the existing inventory table if it exists and recreate it
        c.execute("DROP TABLE IF EXISTS inventory")
        c.execute('''CREATE TABLE inventory (
                        item_id INTEGER PRIMARY KEY, 
                        item_name TEXT UNIQUE, 
                        stock INTEGER, 
                        threshold INTEGER, 
                        price REAL, 
                        supplier_id INTEGER)''')

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
        c.executemany("INSERT INTO inventory (item_name, stock, threshold, price, supplier_id) VALUES (?, ?, ?, ?, ?)", sample_data)

        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
    finally:
        conn.close()

# Remaining functions for user registration, login, and low stock alert
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

# Low Stock Alert System
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

    # Remove stock functionality
    selected_item = st.selectbox("Select an Item to Remove Stock", df["Item Name"])
    remove_quantity = st.number_input("Quantity to Remove", min_value=1, value=1)
    if st.button("Remove Stock"):
        try:
            conn = sqlite3.connect('inventory_management.db')
            c = conn.cursor()
            c.execute("SELECT stock, threshold FROM inventory WHERE item_name = ?", (selected_item,))
            stock, threshold = c.fetchone()
            new_stock = stock - remove_quantity
            if new_stock < 0:
                st.warning("Cannot have negative stock. Check the removal quantity.")
            else:
                c.execute("UPDATE inventory SET stock = ? WHERE item_name = ?", (new_stock, selected_item))
                conn.commit()
                st.success(f"Removed {remove_quantity} from {selected_item}. New stock is {new_stock}.")
                if new_stock < threshold:
                    st.error(f"Alert: {selected_item} stock is below the threshold! Current stock: {new_stock}, Threshold: {threshold}")
        except sqlite3.Error as e:
            st.error(f"Error updating stock: {e}")
        finally:
            conn.close()

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
            functions = ["Low Stock Alerts"]
            selected_function = st.sidebar.selectbox("Select Function", functions)

            if selected_function == "Low Stock Alerts":
                low_stock_alerts()

# Initialize Database and Run App
if __name__ == '__main__':
    init_db()
    main()
