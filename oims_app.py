import streamlit as st
import pandas as pd
import hashlib

# Mock data for inventory and orders
inventory_data = {
    "SKU": ["A123", "B456", "C789"],
    "Product": ["Widget A", "Widget B", "Widget C"],
    "Category": ["Widgets", "Gadgets", "Widgets"],
    "Stock Level": [50, 20, 100],
    "Threshold": [10, 15, 30]
}
orders_data = {
    "Order ID": [1, 2, 3],
    "Product": ["Widget A", "Widget B", "Widget C"],
    "Quantity": [5, 10, 20],
    "Status": ["Shipped", "Pending", "Delivered"]
}

# Load data into DataFrames
inventory_df = pd.DataFrame(inventory_data)
orders_df = pd.DataFrame(orders_data)

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User credentials (in a real app, store this securely)
users_db = {
    "admin": hash_password("admin123"),
    "user1": hash_password("password1")
}

# Streamlit app layout
st.title("Online Inventory Management System (OIMS)")

# Session state to track login status
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Login Page
if not st.session_state.logged_in:
    st.subheader("Login")

    # Login Form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Authentication
    if st.button("Login", key="login_button"):
        if username in users_db and users_db[username] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid username or password.")

    # Registration Link
    if st.button("Register New User", key="register_button"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        # Redirect to registration page
        st.experimental_rerun()

# Registration Page
if not st.session_state.logged_in and st.button("Register New User", key="register_button_2"):
    st.subheader("Register New User")

    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if new_password == confirm_password:
        if st.button("Register", key="register_submit"):
            if new_username not in users_db:
                users_db[new_username] = hash_password(new_password)
                st.success(f"User {new_username} registered successfully!")
                st.session_state.logged_in = True
                st.session_state.username = new_username
                # No need to rerun manually
                st.experimental_rerun()
            else:
                st.error("Username already exists!")
    else:
        st.error("Passwords do not match.")

# After login or registration, show the app content
if st.session_state.logged_in:
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page:", ["Inventory", "Orders", "Reports"])

    # Inventory Page
    if page == "Inventory":
        st.header("Inventory Management")

        # Display inventory data
        st.subheader("Current Inventory")
        st.dataframe(inventory_df)

        # Low Stock Alerts
        st.subheader("Low Stock Alerts")
        low_stock = inventory_df[inventory_df["Stock Level"] < inventory_df["Threshold"]]
        if not low_stock.empty:
            st.warning("The following items are low in stock:")
            st.table(low_stock)
        else:
            st.success("All items are sufficiently stocked.")

        # Stock Adjustment
        st.subheader("Adjust Stock Levels")
        sku = st.selectbox("Select SKU:", inventory_df["SKU"])
        adjustment = st.number_input("Adjustment Quantity:", value=0)
        if st.button("Adjust Stock"):
            inventory_df.loc[inventory_df["SKU"] == sku, "Stock Level"] += adjustment
            st.success(f"Stock level for {sku} updated.")

    # Orders Page
    elif page == "Orders":
        st.header("Order Processing")

        # Display orders data
        st.subheader("Current Orders")
        st.dataframe(orders_df)

        # Order Status Update
        st.subheader("Update Order Status")
        order_id = st.selectbox("Select Order ID:", orders_df["Order ID"])
        new_status = st.selectbox("New Status:", ["Pending", "Shipped", "Delivered"])
        if st.button("Update Status"):
            orders_df.loc[orders_df["Order ID"] == order_id, "Status"] = new_status
            st.success(f"Order {order_id} status updated to {new_status}.")

    # Reports Page
    elif page == "Reports":
        st.header("Sales and Inventory Reports")

        # Sales Report
        st.subheader("Sales Report")
        st.write("Sales trends, performance metrics, and demand forecasting.")

        # Inventory Report
        st.subheader("Inventory Report")
        st.write("Stock levels, low stock history, and supplier details.")
