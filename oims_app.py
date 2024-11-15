import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime
from hashlib import sha256

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

# User Registration Function with Password Hashing
def register_user(username, password):
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        hashed_password = sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        st.success("User registered successfully!")
    except sqlite3.Error as e:
        st.error(f"Error during registration: {e}")

# User Login Function with Password Hashing
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
            conn = sqlite3.connect('inventory_management.db')
            c = conn.cursor()
            c.execute("SELECT item_id, stock, price FROM inventory WHERE item_name = ?", (item_name,))
            item = c.fetchone()
            item_id, stock, price = item

            if quantity <= stock:
                order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO orders (item_id, quantity, order_date, order_status) VALUES (?, ?, ?, ?)", 
                          (item_id, quantity, order_date, "Pending"))
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

            item_names = [item[1] for item in items]
            selected_item_name = st.selectbox("Select an Item to Update", item_names)

            conn = sqlite3.connect('inventory_management.db')
            c = conn.cursor()
            c.execute("SELECT item_id, stock FROM inventory WHERE item_name = ?", (selected_item_name,))
            item = c.fetchone()
            conn.close()

            item_id, current_stock = item

            updated_stock = st.number_input("Enter New Stock Quantity", min_value=0, value=current_stock)

            if st.button("Update Stock"):
                try:
                    conn = sqlite3.connect('inventory_management.db')
                    c = conn.cursor()
                    c.execute("UPDATE inventory SET stock = ? WHERE item_id = ?", (updated_stock, item_id))
                    conn.commit()
                    conn.close()
                    st.success(f"Stock for {selected_item_name} updated to {updated_stock}.")
                except sqlite3.Error as e:
                    st.error(f"Error updating stock: {e}")
        else:
            st.write("No items found in inventory.")
    except sqlite3.Error as e:
        st.error(f"Error fetching inventory data: {e}")

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
    df = pd.DataFrame(data, columns=["Item ID", "Item Name", "Stock", "Threshold"])
    st.table(df)

    low_stock_items = df[df["Stock"] < df["Threshold"]]
    for index, row in low_stock_items.iterrows():
        st.error(f"Alert: {row['Item Name']} stock is below the threshold! Current stock: {row['Stock']}, Threshold: {row['Threshold']}")

# Manage Suppliers Function
def manage_suppliers():
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

        st.subheader("Add or Edit Supplier")
        selected_supplier = st.selectbox(
            "Select Supplier to Edit", 
            ["Add New Supplier"] + [f"{sup[0]}: {sup[1]}" for sup in suppliers]
        )

        if selected_supplier == "Add New Supplier":
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
        else:
            supplier_id = int(selected_supplier.split(":")[0])
            supplier_name = st.text_input("Supplier Name", value=[sup[1] for sup in suppliers if sup[0] == supplier_id][0])
            contact_info = st.text_input("Contact Info", value=[sup[2] for sup in suppliers if sup[0] == supplier_id][0])

            if st.button("Update Supplier"):
                try:
                    conn = sqlite3.connect('inventory_management.db')
                    c = conn.cursor()
                    c.execute("UPDATE suppliers SET supplier_name = ?, contact_info = ? WHERE supplier_id = ?", 
                              (supplier_name, contact_info, supplier_id))
                    conn.commit()
                    conn.close()
                    st.success("Supplier details updated successfully.")
                except sqlite3.Error as e:
                    st.error(f"Error updating supplier: {e}")
    except sqlite3.Error as e:
        st.error(f"Error fetching supplier data: {e}")

# Sales Reports and Analytics Functionality
def sales_reports_and_analytics():
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT DISTINCT item_name FROM inventory")
        skus = [row[0] for row in c.fetchall()]
        conn.close()

        st.subheader("Sales Reports and Analytics")
        selected_month = st.selectbox("Select Month", [f"{i:02}" for i in range(1, 13)])
        selected_sku = st.selectbox("Select SKU", skus)

        if st.button("View Report"):
            try:
                conn = sqlite3.connect('inventory_management.db')
                c = conn.cursor()
                c.execute("""
                    SELECT 
                        orders.order_date, 
                        orders.quantity, 
                        inventory.price
                    FROM 
                        orders
                    JOIN 
                        inventory 
                    ON 
                        orders.item_id = inventory.item_id
                    WHERE 
                        inventory.item_name = ? 
                        AND strftime('%m', orders.order_date) = ?
                """, (selected_sku, selected_month))
                data = c.fetchall()
                conn.close()

                if data:
                    df = pd.DataFrame(data, columns=["Order Date", "Quantity", "Price"])
                    df["Sales"] = df["Quantity"] * df["Price"]
                    st.write(f"Sales Report for {selected_sku} in Month {selected_month}")
                    st.table(df)
                    st.write("Total Quantity Sold:", df["Quantity"].sum())
                    st.write("Total Sales:", df["Sales"].sum())
                    st.line_chart(df[["Sales"]])
                else:
                    st.write(f"No sales data found for {selected_sku} in Month {selected_month}.")
            except sqlite3.Error as e:
                st.error(f"Error fetching sales data: {e}")
    except sqlite3.Error as e:
        st.error(f"Error fetching SKU data: {e}")

# Dashboard Function
def dashboard():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.error("Please log in to access the dashboard.")
        return

    st.sidebar.title("Dashboard Menu")
    options = [
        "Current Stock Status", 
        "Update Inventory", 
        "Place Order", 
        "Track Orders", 
        "Manage Suppliers", 
        "Sales Reports and Analytics"
    ]
    choice = st.sidebar.radio("Select an Option", options)

    if choice == "Current Stock Status":
        current_stock_status()
    elif choice == "Update Inventory":
        update_inventory()
    elif choice == "Place Order":
        place_order()
    elif choice == "Track Orders":
        track_orders()
    elif choice == "Manage Suppliers":
        manage_suppliers()
    elif choice == "Sales Reports and Analytics":
        sales_reports_and_analytics()

# Main Application
def main():
    st.title("Online Inventory Management System")

    init_db()

    menu = ["Home", "Login", "Register", "Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.write("""
        Welcome to the Online Inventory Management System.
        Navigate using the menu on the left.
        """)
    elif choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state["logged_in"] = True
                st.success("Login successful.")
            else:
                st.error("Invalid username or password.")
    elif choice == "Register":
        st.subheader("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            register_user(username, password)
    elif choice == "Dashboard":
        dashboard()

if __name__ == "__main__":
    main()
