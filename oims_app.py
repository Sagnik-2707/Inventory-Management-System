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

        # Orders table
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
                        order_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        item_id INTEGER, 
                        quantity INTEGER, 
                        order_date TEXT, 
                        order_status TEXT,
                        FOREIGN KEY(item_id) REFERENCES inventory(item_id))''')

        # Suppliers table (New table for supplier information)
        c.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                        supplier_id INTEGER PRIMARY KEY, 
                        supplier_name TEXT, 
                        contact_info TEXT)''')

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

        # Sample supplier data
        supplier_data = [
            (1, "Supplier 1", "Contact Info 1"),
            (2, "Supplier 2", "Contact Info 2"),
            (3, "Supplier 3", "Contact Info 3"),
            (4, "Supplier 4", "Contact Info 4"),
            (5, "Supplier 5", "Contact Info 5")
        ]
        c.executemany("INSERT OR IGNORE INTO suppliers (supplier_id, supplier_name, contact_info) VALUES (?, ?, ?)", supplier_data)

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
        st.success("User registered successfully!")
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

# Supplier Management: Display and Edit Supplier Information
def display_suppliers():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT supplier_id, supplier_name, contact_info FROM suppliers")
        suppliers = c.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching supplier data: {e}")
        return
    finally:
        conn.close()

    st.subheader("Supplier Information")
    if suppliers:
        df = pd.DataFrame(suppliers, columns=["Supplier ID", "Supplier Name", "Contact Info"])
        st.table(df)
    else:
        st.write("No supplier data found.")

def edit_supplier():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT supplier_id, supplier_name FROM suppliers")
        suppliers = c.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching supplier data: {e}")
        return
    finally:
        conn.close()

    st.subheader("Edit Supplier Information")
    supplier_names = [s[1] for s in suppliers]
    selected_supplier_name = st.selectbox("Select Supplier to Edit", supplier_names)

    if selected_supplier_name:
        # Fetch supplier details
        try:
            conn = sqlite3.connect('inventory_management.db')
            c = conn.cursor()
            c.execute("SELECT supplier_id, supplier_name, contact_info FROM suppliers WHERE supplier_name = ?", (selected_supplier_name,))
            supplier = c.fetchone()
        except sqlite3.Error as e:
            st.error(f"Error fetching supplier details: {e}")
            return
        finally:
            conn.close()

        supplier_id, supplier_name, contact_info = supplier
        new_supplier_name = st.text_input("Supplier Name", supplier_name)
        new_contact_info = st.text_input("Contact Info", contact_info)

        if st.button("Update Supplier"):
            try:
                conn = sqlite3.connect('inventory_management.db')
                c = conn.cursor()
                c.execute("UPDATE suppliers SET supplier_name = ?, contact_info = ? WHERE supplier_id = ?", 
                          (new_supplier_name, new_contact_info, supplier_id))
                conn.commit()
                st.success(f"Supplier information for {selected_supplier_name} updated successfully!")
            except sqlite3.Error as e:
                st.error(f"Error updating supplier data: {e}")
            finally:
                conn.close()

# Dashboard Functionality
def dashboard():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.warning("Please login first.")
    else:
        st.subheader("Inventory Management Dashboard")
        st.sidebar.write("## Functions")
        functions = ["Low Stock Alerts", "Update Inventory", "Place Order", "Track Orders", "Manage Suppliers"]
        selected_function = st.sidebar.selectbox("Select Function", functions)

        if selected_function == "Low Stock Alerts":
            low_stock_alerts()

        elif selected_function == "Update Inventory":
            update_inventory()

        elif selected_function == "Manage Suppliers":
            display_suppliers()
            edit_supplier()

# Streamlit App
def main():
    st.title("Inventory Management System")
    st.sidebar.title("Navigation")
    menu = ["Login", "Register", "Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.success(f"Welcome back {username}!")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
            else:
                st.warning("Incorrect Username or Password")

    elif choice == "Register":
        st.subheader("Create a New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        if st.button("Register"):
            register_user(new_user, new_password)

    elif choice == "Dashboard":
        dashboard()

# Initialize Database and Run App
if __name__ == '__main__':
    init_db()
    main()
