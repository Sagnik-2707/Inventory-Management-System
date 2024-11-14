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

# Registration and Login Functions
def register_user(username, password):
    hashed_password = hash_password(password)
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()

def login_user(username, password):
    hashed_password = hash_password(password)
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    return cursor.fetchone()

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login and Registration Interface
def login_screen():
    st.title("Welcome to Inventory Management Dashboard")
    menu = st.selectbox("Choose Action", ["Login", "Register"])

    if menu == "Register":
        st.subheader("Create a New Account")
        new_username = st.text_input("Username", key="register_username")
        new_password = st.text_input("Password", type="password", key="register_password")
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
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Incorrect username or password.")

# Main Dashboard after Login
def main_dashboard():
    # KPI section at the top
    st.title("🗃️ Inventory Management Dashboard")
    col1, col2, col3 = st.columns(3)

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

    # Display KPI boxes at the top of the dashboard
    total_stock = inventory_df["Stock Level"].sum()
    low_stock_count = inventory_df[inventory_df["Stock Level"] < inventory_df["Threshold"]].shape[0]
    pending_orders = orders_df[orders_df["Status"] == "Pending"].shape[0]

    col1.metric("📦 Total Stock", total_stock)
    col2.metric("⚠️ Low Stock Items", low_stock_count)
    col3.metric("📋 Pending Orders", pending_orders)

    # Sidebar for navigation with icons
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", ["📦 Inventory", "📑 Orders", "📈 Reports"])
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

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

