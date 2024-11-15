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
    st.subheader("📦 Place an Order")
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

    if not items:
        st.warning("No items available in inventory.")
        return

    item_name = st.selectbox("Select an Item to Order", [item[0] for item in items])
    quantity = st.number_input("Quantity", min_value=1, value=1)

    if st.button("🛒 Place Order"):
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
                st.success(f"✅ Order placed for {quantity} of {item_name}.")
            else:
                st.error(f"❌ Not enough stock for {item_name}. Only {stock} available.")
        except sqlite3.Error as e:
            st.error(f"Error placing order: {e}")
        finally:
            conn.close()

# Track Orders Function
def track_orders():
    st.subheader("📝 Track Orders")
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

    if orders:
        df = pd.DataFrame(orders, columns=["Order ID", "Item Name", "Quantity", "Order Date", "Order Status"])
        st.table(df)
    else:
        st.info("No orders found.")

# Update Inventory Function
def update_inventory():
    st.subheader("📋 Update Inventory")
    try:
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("SELECT item_id, item_name, stock, price, threshold FROM inventory")
        items = c.fetchall()
        conn.close()

        if items:
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

            if st.button("✅ Update Stock"):
                try:
                    conn = sqlite3.connect('inventory_management.db')
                    c = conn.cursor()
                    c.execute("UPDATE inventory SET stock = ? WHERE item_id = ?", (updated_stock, item_id))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Stock for {selected_item_name} updated to {updated_stock}.")
                except sqlite3.Error as e:
                    st.error(f"Error updating stock: {e}")
        else:
            st.warning("No items found in inventory.")
    except sqlite3.Error as e:
        st.error(f"Error fetching inventory data: {e}")

# Other functions can be updated similarly with better use of Streamlit's features and layout management

# Main Application
def main():
    st.set_page_config(page_title="Inventory Management System", page_icon="📦", layout="wide")
    st.title("📦 Online Inventory Management System")

    init_db()

    menu = ["🏠 Home", "🔐 Login", "📝 Register", "📊 Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "🏠 Home":
        st.markdown("""
        Welcome to the **Online Inventory Management System**. 
        Navigate using the menu on the left. 🚀
        """)
    elif choice == "🔐 Login":
        st.subheader("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state["logged_in"] = True
                st.success("Login successful.")
            else:
                st.error("Invalid username or password.")
    elif choice == "📝 Register":
        st.subheader("📝 Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            register_user(username, password)
    elif choice == "📊 Dashboard":
        dashboard()

if __name__ == "__main__":
    main()
