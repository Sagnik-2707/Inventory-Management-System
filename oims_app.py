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

        # Create a new orders table with the correct schema
        c.execute('''CREATE TABLE IF NOT EXISTS orders_new (
                        order_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        item_id INTEGER, 
                        quantity INTEGER, 
                        order_date TEXT, 
                        order_status TEXT,
                        FOREIGN KEY(item_id) REFERENCES inventory(item_id))''')

        # Migrate data if needed
        c.execute('''INSERT INTO orders_new (order_id, item_id, quantity, order_date, order_status)
                     SELECT order_id, item_id, quantity, order_date, order_status FROM orders''')
        conn.commit()

        # Drop the old orders table and rename the new one
        c.execute('''DROP TABLE IF EXISTS orders''')
        c.execute('''ALTER TABLE orders_new RENAME TO orders''')
        
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

# Place an Order Function
def place_order(item_name, quantity):
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()

        # Fetch the item_id and current stock for the item
        c.execute("SELECT item_id, stock FROM inventory WHERE item_name = ?", (item_name,))
        item = c.fetchone()

        if item:
            item_id, current_stock = item
            if quantity <= current_stock:
                # Insert the order into the orders table
                order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO orders (item_id, quantity, order_date, order_status) VALUES (?, ?, ?, ?)", 
                          (item_id, quantity, order_date, "Pending"))
                # Update the inventory stock
                c.execute("UPDATE inventory SET stock = stock - ? WHERE item_name = ?", (quantity, item_name))
                conn.commit()
                st.success(f"Order placed for {quantity} of {item_name}.")
            else:
                st.warning(f"Not enough stock for {item_name}. Current stock: {current_stock}")
        else:
            st.warning("Item not found.")
    except sqlite3.Error as e:
        st.error(f"Error placing order: {e}")
    finally:
        conn.close()

# Track Orders Function
def track_orders():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute('''SELECT o.order_id, i.item_name, o.quantity, o.order_date, o.order_status 
                     FROM orders o 
                     JOIN inventory i ON o.item_id = i.item_id''')
        orders = c.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching orders: {e}")
        return
    finally:
        conn.close()

    st.subheader("Order Tracking")
    if orders:
        df = pd.DataFrame(orders, columns=["Order ID", "Item Name", "Quantity", "Order Date", "Order Status"])
        st.table(df)
    else:
        st.write("No orders found.")

# Inventory Management Dashboard with Order Tracking
def dashboard():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.warning("Please login first.")
    else:
        st.subheader("Inventory Management Dashboard")
        st.sidebar.write("## Functions")
        functions = ["Low Stock Alerts", "Update Inventory", "Place Order", "Track Orders"]
        selected_function = st.sidebar.selectbox("Select Function", functions)

        if selected_function == "Low Stock Alerts":
            low_stock_alerts()

        elif selected_function == "Update Inventory":
            update_inventory()

        elif selected_function == "Place Order":
            st.subheader("Place a New Order")
            # Fetch available items for order placement
            conn = sqlite3.connect('inventory_management.db')
            c = conn.cursor()
            c.execute("SELECT item_name FROM inventory")
            items = c.fetchall()
            conn.close()

            item_name = st.selectbox("Select Item to Order", [item[0] for item in items])
            quantity = st.number_input("Quantity", min_value=1, value=1)

            if st.button("Place Order"):
                place_order(item_name, quantity)

        elif selected_function == "Track Orders":
            track_orders()

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
