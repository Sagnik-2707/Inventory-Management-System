import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize SQLite database
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
conn.commit()

# Registration and Login Pages
def register_user(username, password):
    hashed_password = hash_password(password)
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()

def login_user(username, password):
    hashed_password = hash_password(password)
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    return cursor.fetchone()

# Check if user is already logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login and Registration Interface
if not st.session_state.logged_in:
    st.title("Welcome to Inventory Management Dashboard")
    menu = st.selectbox("Choose Action", ["Login", "Register"])

    if menu == "Register":
        st.subheader("Create a New Account")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        if st.button("Register"):
            if new_username and new_password:
                cursor.execute("SELECT * FROM users WHERE username = ?", (new_username,))
                if cursor.fetchone():
                    st.warning("Username already taken. Please choose another username.")
                else:
                    register_user(new_username, new_password)
                    st.success("Registration successful! You can now log in.")
            else:
                st.warning("Please fill out both fields.")

    elif menu == "Login":
        st.subheader("Log in to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Incorrect username or password.")

# Main Dashboard after Login
if st.session_state.logged_in:
    # Initialize mock data in session state if not already initialized
    if "inventory_data" not in st.session_state:
        st.session_state.inventory_data = {
            "SKU": ["A123", "B456", "C789"],
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Category": ["Widgets", "Gadgets", "Widgets"],
            "Stock Level": [50, 20, 100],
            "Threshold": [10, 15, 30]
        }

    if "orders_data" not in st.session_state:
        st.session_state.orders_data = {
            "Order ID": [1, 2, 3],
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Quantity": [5, 10, 20],
            "Status": ["Shipped", "Pending", "Delivered"]
        }

    # Convert dictionaries to DataFrames for easy manipulation
    inventory_df = pd.DataFrame(st.session_state.inventory_data)
    orders_df = pd.DataFrame(st.session_state.orders_data)

    # KPI section at the top
    st.title("🗃️ Inventory Management Dashboard")
    col1, col2, col3 = st.columns(3)
    total_stock = inventory_df["Stock Level"].sum()
    low_stock_count = inventory_df[inventory_df["Stock Level"] < inventory_df["Threshold"]].shape[0]
    pending_orders = orders_df[orders_df["Status"] == "Pending"].shape[0]

    col1.markdown(f"<div class='kpi'>📦 Total Stock<br><b>{total_stock}</b></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='kpi'>⚠️ Low Stock Items<br><b>{low_stock_count}</b></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='kpi'>📋 Pending Orders<br><b>{pending_orders}</b></div>", unsafe_allow_html=True)

    # Sidebar for navigation with icons
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", ["📦 Inventory", "📑 Orders", "📈 Reports"])
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False, "username": ""}))

    # Inventory Page
    if page == "📦 Inventory":
        st.header("Inventory Management")

        # Display inventory data in an expander
        with st.expander("Current Inventory", expanded=True):
            st.dataframe(inventory_df)

        # Low Stock Alerts in an expander
        with st.expander("Low Stock Alerts", expanded=True):
            low_stock = inventory_df[inventory_df["Stock Level"] < inventory_df["Threshold"]]
            if not low_stock.empty:
                st.warning("🚨 Alert! The following items are below the threshold stock level:")
                st.table(low_stock[["SKU", "Product", "Stock Level", "Threshold"]])
            else:
                st.success("All items are sufficiently stocked.")

        # Stock Adjustment
        st.subheader("Adjust Stock Levels")
        sku = st.selectbox("Select SKU:", inventory_df["SKU"])
        adjustment = st.number_input("Adjustment Quantity:", value=0)
        if st.button("Adjust Stock"):
            # Update stock level in the session state directly
            index = inventory_df[inventory_df["SKU"] == sku].index[0]
            st.session_state.inventory_data["Stock Level"][index] += adjustment
            st.success(f"Stock level for {sku} updated.")

            # Refresh the displayed inventory data
            inventory_df = pd.DataFrame(st.session_state.inventory_data)
            st.dataframe(inventory_df)  # Refresh table with updated data

    # Orders Page
    elif page == "📑 Orders":
        st.header("Order Processing")

        # Display orders data in an expander
        with st.expander("Current Orders", expanded=True):
            st.dataframe(orders_df)

        # Order Status Update
        st.subheader("Update Order Status")
        order_id = st.selectbox("Select Order ID:", orders_df["Order ID"])
        new_status = st.selectbox("New Status:", ["Pending", "Shipped", "Delivered"])
        if st.button("Update Status"):
            # Update order status in the session state directly
            index = orders_df[orders_df["Order ID"] == order_id].index[0]
            st.session_state.orders_data["Status"][index] = new_status
            st.success(f"Order {order_id} status updated to {new_status}.")

            # Refresh the displayed orders data
            orders_df = pd.DataFrame(st.session_state.orders_data)
            st.dataframe(orders_df)  # Refresh table with updated data

    # Reports Page
    elif page == "📈 Reports":
        st.header("Sales and Inventory Reports")

        # Sales Report with Matplotlib
        st.subheader("Sales Trends")
        dates = pd.date_range(start="2023-01-01", periods=12, freq="M")
        sales = np.random.randint(1000, 5000, size=12)
        sales_data = pd.DataFrame({"Date": dates, "Sales": sales})
        fig, ax = plt.subplots()
        ax.plot(sales_data["Date"], sales_data["Sales"], marker="o", color="b")
        ax.set_title("Monthly Sales Trends")
        ax.set_xlabel("Date")
        ax.set_ylabel("Sales")
        st.pyplot(fig)

        # Inventory Turnover with Matplotlib
        st.subheader("Inventory Turnover")
        turnover = np.random.rand(3) * 10
        fig, ax = plt.subplots()
        ax.bar(inventory_df["Product"], turnover, color="green")
        ax.set_title("Inventory Turnover Rate by Product")
        ax.set_xlabel("Product")
        ax.set_ylabel("Turnover Rate")
        st.pyplot(fig)

        # Product Performance
        st.subheader("Product Performance Metrics")
        performance_data = {
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Sales": [150, 120, 300],
            "Returns": [5, 10, 8],
            "Profit Margin": [0.35, 0.25, 0.45]
        }
        performance_df = pd.DataFrame(performance_data)
        st.table(performance_df)

        st.write("These reports give insights into sales trends, inventory turnover, and individual product performance.")
