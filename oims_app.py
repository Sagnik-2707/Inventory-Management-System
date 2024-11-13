import streamlit as st
import pandas as pd

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

# Streamlit app layout
st.title("Online Inventory Management System (OIMS)")

# Sidebar for navigation
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

# Run the app with: streamlit run oims_app.py
