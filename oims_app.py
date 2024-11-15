import sqlite3
import streamlit as st
import pandas as pd
from datetime import datetime
from hashlib import sha256
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="Inventory Management",
    page_icon="📦",
    layout="wide"
)

# Custom CSS for Styling
st.markdown("""
    <style>
        .main {
            background-color: #f9f9f9;
            font-family: Arial, sans-serif;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
        }
        .stSidebar {
            background-color: #222;
            color: white;
        }
        h1 {
            color: #4CAF50;
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize Database
def init_db():
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

# User Authentication Functions
def register_user(username, password):
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    hashed_password = sha256(password.encode()).hexdigest()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    st.success("User registered successfully!")

def login_user(username, password):
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    hashed_password = sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    data = c.fetchone()
    conn.close()
    return data

# Dashboard Functions
def current_stock_status():
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    c.execute("SELECT item_id, item_name, stock, threshold FROM inventory")
    data = c.fetchall()
    conn.close()

    st.subheader("📦 Current Stock Status")
    if data:
        df = pd.DataFrame(data, columns=["Item ID", "Item Name", "Stock", "Threshold"])
        st.table(df)

        low_stock_items = df[df["Stock"] < df["Threshold"]]
        if not low_stock_items.empty:
            for index, row in low_stock_items.iterrows():
                st.error(f"⚠️ {row['Item Name']} stock is below the threshold! Current: {row['Stock']}, Threshold: {row['Threshold']}")

        # Visualize stock levels
        fig = px.bar(df, x="Item Name", y="Stock", color="Stock", title="Stock Levels")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No items found in inventory.")

def manage_suppliers():
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    c.execute("SELECT * FROM suppliers")
    suppliers = c.fetchall()
    conn.close()

    st.subheader("👥 Manage Suppliers")
    if suppliers:
        df = pd.DataFrame(suppliers, columns=["Supplier ID", "Supplier Name", "Contact Info"])
        st.table(df)

    supplier_name = st.text_input("Supplier Name")
    contact_info = st.text_input("Contact Info")
    if st.button("Add Supplier"):
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("INSERT INTO suppliers (supplier_name, contact_info) VALUES (?, ?)", (supplier_name, contact_info))
        conn.commit()
        conn.close()
        st.success("Supplier added successfully!")

def sales_reports_and_analytics():
    conn = sqlite3.connect('inventory_management.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT item_name FROM inventory")
    items = [row[0] for row in c.fetchall()]
    conn.close()

    st.subheader("📊 Sales Reports and Analytics")
    selected_month = st.selectbox("Select Month", [f"{i:02}" for i in range(1, 13)])
    selected_item = st.selectbox("Select Item", items)

    if st.button("Generate Report"):
        conn = sqlite3.connect('inventory_management.db')
        c = conn.cursor()
        c.execute("""
            SELECT orders.order_date, orders.quantity, inventory.price
            FROM orders
            JOIN inventory ON orders.item_id = inventory.item_id
            WHERE inventory.item_name = ? AND strftime('%m', orders.order_date) = ?
        """, (selected_item, selected_month))
        data = c.fetchall()
        conn.close()

        if data:
            df = pd.DataFrame(data, columns=["Order Date", "Quantity", "Price"])
            df["Sales"] = df["Quantity"] * df["Price"]
            st.write(f"Sales Report for {selected_item} in Month {selected_month}")
            st.table(df)
            st.write("Total Quantity Sold:", df["Quantity"].sum())
            st.write("Total Sales:", df["Sales"].sum())
            st.line_chart(df[["Sales"]])
        else:
            st.info(f"No sales data for {selected_item} in Month {selected_month}.")

# Main Application
def main():
    st.title("📦 Online Inventory Management System")

    init_db()

    menu = ["Home", "Login", "Register", "Dashboard"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.write("Welcome to the **Online Inventory Management System**. Use the menu to navigate.")
    elif choice == "Login":
        st.subheader("🔑 Login")
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
        st.subheader("📝 Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            register_user(username, password)
    elif choice == "Dashboard":
        if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
            st.error("Please log in to access the dashboard.")
        else:
            st.sidebar.title("📋 Dashboard Menu")
            options = ["Current Stock Status", "Manage Suppliers", "Sales Reports and Analytics"]
            choice = st.sidebar.radio("Select an Option", options)

            if choice == "Current Stock Status":
                current_stock_status()
            elif choice == "Manage Suppliers":
                manage_suppliers()
            elif choice == "Sales Reports and Analytics":
                sales_reports_and_analytics()

if __name__ == "__main__":
    main()
