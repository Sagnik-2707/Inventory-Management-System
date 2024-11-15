import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize the Database
def init_db():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute(''' 
            CREATE TABLE IF NOT EXISTS inventory (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                stock INTEGER,
                price REAL,
                threshold INTEGER
            )
        ''')
        c.execute(''' 
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                quantity INTEGER,
                order_date TEXT,
                order_status TEXT,
                FOREIGN KEY(item_id) REFERENCES inventory(item_id)
            )
        ''')
        c.execute(''' 
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name TEXT,
                contact_info TEXT
            )
        ''')
        c.execute(''' 
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        st.error(f"Error initializing database: {e}")

# User Registration Function
def register_user(username, password):
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        st.success("User registered successfully.")
    except sqlite3.Error as e:
        st.error(f"Error registering user: {e}")

# User Login Function
def login_user(username, password):
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            return True
        else:
            return False
    except sqlite3.Error as e:
        st.error(f"Error logging in user: {e}")
        return False

# Place Order Function
def place_order():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT item_name, stock, price FROM inventory")
        items = c.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching inventory data: {e}")
        return
    finally:
        conn.close()

    st.subheader("Place an Order")
    item_name = st.selectbox("Select an Item to Order", [item[0] for item in items])
    quantity = st.number_input("Quantity", min_value=1, value=1)

    if st.button("Place Order"):
        try:
            # Check if enough stock is available
            conn = sqlite3.connect('inventory_management.db')
            c = conn.cursor()
            c.execute("SELECT item_id, stock, price FROM inventory WHERE item_name = ?", (item_name,))
            item = c.fetchone()
            item_id, stock, price = item

            if quantity <= stock:
                # Place order
                order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO orders (item_id, quantity, order_date, order_status) VALUES (?, ?, ?, ?)", 
                          (item_id, quantity, order_date, "Pending"))
                # Update inventory stock
                new_stock = stock - quantity
                c.execute("UPDATE inventory SET stock = ? WHERE item_id = ?", (new_stock, item_id))
                conn.commit()
                st.success(f"Order placed for {quantity} of {item_name}.")
            else:
                st.error(f"Not enough stock for {item_name}. Only {stock} available.")

        except sqlite3.Error as e:
            st.error(f"Error placing order: {e}")
        finally:
            conn.close()

# Track Orders Function
def track_orders():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT orders.order_id, inventory.item_name, orders.quantity, orders.order_date, orders.order_status FROM orders JOIN inventory ON orders.item_id = inventory.item_id")
        orders = c.fetchall()
    except sqlite3.Error as e:
        st.error(f"Error fetching order data: {e}")
        return
    finally:
        conn.close()

    st.subheader("Track Orders")
    if orders:
        df = pd.DataFrame(orders, columns=["Order ID", "Item Name", "Quantity", "Order Date", "Order Status"])
        st.table(df)
    else:
        st.write("No orders found.")

# Update Inventory Function
def update_inventory():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT item_id, item_name, stock, price, threshold FROM inventory")
        items = c.fetchall()
        conn.close()
        
        if items:
            st.subheader("Current Inventory")
            df = pd.DataFrame(items, columns=["Item ID", "Item Name", "Stock", "Price", "Threshold"])
            st.table(df)

            # Select item to update stock
            item_names = [item[1] for item in items]
            selected_item_name = st.selectbox("Select an Item to Update", item_names)

            # Get the current stock of the selected item
            conn = sqlite3.connect('inventory_management.db')
            c = conn.cursor()
            c.execute("SELECT item_id, stock FROM inventory WHERE item_name = ?", (selected_item_name,))
            item = c.fetchone()
            conn.close()

            item_id, current_stock = item

            # Update stock quantity
            updated_stock = st.number_input("Enter New Stock Quantity", min_value=0, value=current_stock)

            if st.button("Update Stock"):
                try:
                    # Update inventory with the new stock value
                    conn = sqlite3.connect('inventory_management.db')
                    c = conn.cursor()
                    c.execute("UPDATE inventory SET stock = ? WHERE item_id = ?", (updated_stock, item_id))
                    conn.commit()
                    conn.close()
                    st.success(f"Stock for {selected_item_name} updated to {updated_stock}.")
                    
                    # Re-fetch and display the updated inventory
                    update_inventory()  # Recursively update the inventory table
                except sqlite3.Error as e:
                    st.error(f"Error updating stock: {e}")
        else:
            st.write("No items found in inventory.")
    except sqlite3.Error as e:
        st.error(f"Error fetching inventory data: {e}")

# Manage Suppliers Function
def display_suppliers():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT * FROM suppliers")
        suppliers = c.fetchall()
        conn.close()

        if suppliers:
            st.subheader("Suppliers")
            df = pd.DataFrame(suppliers, columns=["Supplier ID", "Supplier Name", "Contact Info"])
            st.table(df)
        else:
            st.write("No suppliers found.")
    except sqlite3.Error as e:
        st.error(f"Error fetching supplier data: {e}")

def edit_supplier():
    st.subheader("Add or Edit Supplier")
    supplier_name = st.text_input("Supplier Name")
    contact_info = st.text_input("Contact Info")
    
    if st.button("Add Supplier"):
        try:
            conn = sqlite3.connect('inventory_management.db')
            c = conn.cursor()
            c.execute("INSERT INTO suppliers (supplier_name, contact_info) VALUES (?, ?)", (supplier_name, contact_info))
            conn.commit()
            conn.close()
            st.success("Supplier added successfully.")
        except sqlite3.Error as e:
            st.error(f"Error adding supplier: {e}")

# Current Stock Status Function
def current_stock_status():
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

    st.subheader("Current Stock Status")
    st.write("Current stock levels and thresholds:")

    # Display data in a table format
    df = pd.DataFrame(data, columns=["Item ID", "Item Name", "Stock", "Threshold"])
    st.table(df)

    # Show alerts for items below threshold
    low_stock_items = df[df["Stock"] < df["Threshold"]]
    for index, row in low_stock_items.iterrows():
        st.error(f"Alert: {row['Item Name']} stock is below the threshold! Current stock: {row['Stock']}, Threshold: {row['Threshold']}")

# Dashboard Functionality
def dashboard():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.warning("Please login first.")
    else:
        st.subheader("Inventory Management Dashboard")
        st.sidebar.write("## Functions")
        functions = ["Current Stock Status", "Update Inventory", "Place Order", "Track Orders", "Manage Suppliers"]
        selected_function = st.sidebar.selectbox("Select Function", functions)

        if selected_function == "Current Stock Status":
            current_stock_status()

        elif selected_function == "Update Inventory":
            update_inventory()

        elif selected_function == "Place Order":
            place_order()

        elif selected_function == "Track Orders":
            track_orders()

        elif selected_function == "Manage Suppliers":
            display_suppliers()

# Main Program
def main():
    init_db()

    st.title("Inventory Management System")

    # User login/logout
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state['logged_in'] = True
                st.success("Logged in successfully.")
            else:
                st.error("Invalid username or password.")

        if st.button("Register"):
            register_user(username, password)
    else:
        dashboard()

if __name__ == "__main__":
    main()
