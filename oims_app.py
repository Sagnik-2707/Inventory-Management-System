import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime
from hashlib import sha256

# Initialize the database
def init_db():
    try:
        conn = sqlite3.connect("inventory_management.db")
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT UNIQUE,
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
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database initialization failed: {e}")
    finally:
        conn.close()

# User authentication
def hash_password(password):
    return sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        conn = sqlite3.connect("inventory_management.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                  (username, hash_password(password)))
        conn.commit()
        st.success("User registered successfully!")
    except sqlite3.IntegrityError:
        st.error("Username already exists.")
    except sqlite3.Error as e:
        st.error(f"Registration failed: {e}")
    finally:
        conn.close()

def login_user(username, password):
    try:
        conn = sqlite3.connect("inventory_management.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                  (username, hash_password(password)))
        return c.fetchone()
    except sqlite3.Error as e:
        st.error(f"Login failed: {e}")
    finally:
        conn.close()

# Inventory management
def get_inventory():
    try:
        conn = sqlite3.connect("inventory_management.db")
        df = pd.read_sql_query("SELECT * FROM inventory", conn)
        return df
    except sqlite3.Error as e:
        st.error(f"Failed to fetch inventory: {e}")
    finally:
        conn.close()

def update_stock(item_name, new_stock):
    try:
        conn = sqlite3.connect("inventory_management.db")
        c = conn.cursor()
        c.execute("UPDATE inventory SET stock = ? WHERE item_name = ?", 
                  (new_stock, item_name))
        conn.commit()
        st.success(f"Stock for {item_name} updated to {new_stock}.")
    except sqlite3.Error as e:
        st.error(f"Failed to update stock: {e}")
    finally:
        conn.close()

def current_stock_status():
    st.subheader("Current Stock Status")
    df = get_inventory()
    if not df.empty:
        st.dataframe(df)
        low_stock_items = df[df["stock"] < df["threshold"]]
        for _, row in low_stock_items.iterrows():
            st.warning(f"Low stock alert: {row['item_name']} ({row['stock']} units remaining).")
    else:
        st.info("No items in inventory.")

# Place order
def place_order():
    st.subheader("Place an Order")
    inventory = get_inventory()
    if not inventory.empty:
        item_name = st.selectbox("Select Item", inventory["item_name"])
        quantity = st.number_input("Quantity", min_value=1)
        if st.button("Place Order"):
            conn = sqlite3.connect("inventory_management.db")
            try:
                c = conn.cursor()
                item = inventory[inventory["item_name"] == item_name].iloc[0]
                if quantity > item["stock"]:
                    st.error("Insufficient stock.")
                else:
                    c.execute("""
                        INSERT INTO orders (item_id, quantity, order_date, order_status)
                        VALUES (?, ?, ?, ?)
                    """, (item["item_id"], quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Pending"))
                    c.execute("UPDATE inventory SET stock = ? WHERE item_id = ?", 
                              (item["stock"] - quantity, item["item_id"]))
                    conn.commit()
                    st.success(f"Order placed for {quantity} of {item_name}.")
            except sqlite3.Error as e:
                st.error(f"Failed to place order: {e}")
            finally:
                conn.close()
    else:
        st.info("No items available for order.")

# Track orders
def track_orders():
    st.subheader("Track Orders")
    try:
        conn = sqlite3.connect("inventory_management.db")
        query = """
            SELECT orders.order_id, inventory.item_name, orders.quantity, 
                   orders.order_date, orders.order_status
            FROM orders
            JOIN inventory ON orders.item_id = inventory.item_id
        """
        orders = pd.read_sql_query(query, conn)
        if not orders.empty:
            st.dataframe(orders)
        else:
            st.info("No orders found.")
    except sqlite3.Error as e:
        st.error(f"Failed to fetch orders: {e}")
    finally:
        conn.close()

# Dashboard function
def dashboard():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.error("Please log in to access the dashboard.")
        return

    st.sidebar.title("Dashboard")
    options = ["Current Stock Status", "Update Inventory", "Place Order", "Track Orders"]
    choice = st.sidebar.radio("Choose an option", options)

    if choice == "Current Stock Status":
        current_stock_status()
    elif choice == "Update Inventory":
        item_name = st.text_input("Item Name")
        new_stock = st.number_input("New Stock Quantity", min_value=0)
        if st.button("Update Stock"):
            update_stock(item_name, new_stock)
    elif choice == "Place Order":
        place_order()
    elif choice == "Track Orders":
        track_orders()

# Main application
def main():
    st.title("Inventory Management System")
    init_db()
    menu = ["Home", "Login", "Register", "Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.write("Welcome to the Inventory Management System.")
    elif choice == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state["logged_in"] = True
                st.success("Login successful!")
            else:
                st.error("Invalid username or password.")
    elif choice == "Register":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            register_user(username, password)
    elif choice == "Dashboard":
        dashboard()

if __name__ == "__main__":
    main()
