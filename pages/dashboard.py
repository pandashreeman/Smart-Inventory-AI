
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database.db import get_connection


def load_dashboard_data():

    conn = get_connection()

    try:
        total_products = conn.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        total_stock = conn.execute(
            "SELECT COALESCE(SUM(quantity), 0) FROM inventory"
        ).fetchone()[0]

        total_sales = conn.execute(
            "SELECT COALESCE(SUM(total_amount), 0) FROM sales"
        ).fetchone()[0]

        low_stock = conn.execute("""
            SELECT COUNT(*)
            FROM inventory
            WHERE quantity <= minimum_stock
        """).fetchone()[0]

        recent_sales = pd.read_sql_query("""
            SELECT
                p.product_name,
                s.quantity_sold,
                s.total_amount,
                s.sale_date
            FROM sales s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.sale_date DESC
            LIMIT 5
        """, conn)

        stock_data = pd.read_sql_query("""
            SELECT p.product_name, i.quantity
            FROM products p
            JOIN inventory i ON p.id = i.product_id
            ORDER BY i.quantity DESC
            LIMIT 10
        """, conn)

        sales_data = pd.read_sql_query("""
            SELECT DATE(sale_date) AS sale_day,
                   SUM(total_amount) AS daily_sales
            FROM sales
            GROUP BY DATE(sale_date)
            ORDER BY sale_day
        """, conn)

        return (
            total_products,
            total_stock,
            total_sales,
            low_stock,
            recent_sales,
            stock_data,
            sales_data
        )

    finally:
        conn.close()


def show_dashboard():

    st.title("📦 Smart Inventory Dashboard")

    st.write(
        "Monitor your products, stock, sales and inventory performance."
    )

    st.divider()

    try:
        (
            total_products,
            total_stock,
            total_sales,
            low_stock,
            recent_sales,
            stock_data,
            sales_data
        ) = load_dashboard_data()

    except Exception as error:
        st.error(f"Unable to load dashboard data: {error}")
        return

    # BUSINESS OVERVIEW

    st.subheader("Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Products", total_products)
    col2.metric("Total Stock", total_stock)
    col3.metric("Total Sales", f"₹{total_sales:,.2f}")
    col4.metric("Low Stock Alerts", low_stock)

    st.divider()

    # STOCK ALERTS

    st.subheader("⚠️ Inventory Alerts")

    if low_stock > 0:
        st.warning(
            f"You have {low_stock} products at or below minimum stock."
        )
    else:
        st.success("All products are above their minimum stock level.")

    st.divider()

    # ANALYTICS

    st.subheader("Inventory Analytics")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Product Stock Overview**")

        if not stock_data.empty:

            fig, ax = plt.subplots(figsize=(8, 5))

            ax.barh(
                stock_data["product_name"],
                stock_data["quantity"]
            )

            ax.set_xlabel("Available Quantity")
            ax.set_ylabel("Products")
            ax.set_title("Current Product Stock")

            fig.tight_layout()

            st.pyplot(fig)
            plt.close(fig)

        else:
            st.info("No product stock data available yet.")

    with col2:

        st.write("**Daily Sales Overview**")

        if not sales_data.empty:

            fig, ax = plt.subplots(figsize=(8, 5))

            ax.plot(
                sales_data["sale_day"],
                sales_data["daily_sales"],
                marker="o"
            )

            ax.set_xlabel("Date")
            ax.set_ylabel("Sales Amount (₹)")
            ax.set_title("Daily Sales Trend")

            fig.autofmt_xdate()
            fig.tight_layout()

            st.pyplot(fig)
            plt.close(fig)

        else:
            st.info("No sales data available yet.")

    st.divider()

    # RECENT SALES

    st.subheader("🧾 Recent Sales")

    if not recent_sales.empty:

        recent_sales = recent_sales.rename(columns={
            "product_name": "Product",
            "quantity_sold": "Quantity",
            "total_amount": "Total Amount (₹)",
            "sale_date": "Sale Date"
        })

        st.dataframe(
            recent_sales,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No sales transactions available yet.")

    st.divider()

    st.caption(
        "Smart Inventory Management Assistant | "
        "Powered by Python, SQLite and Machine Learning"
    )

