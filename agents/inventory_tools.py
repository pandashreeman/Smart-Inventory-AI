from database.db import get_connection


def get_total_products():

    conn = get_connection()

    try:
        result = conn.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()

        return f"Total products: {result[0]}"

    finally:
        conn.close()


def get_total_stock():

    conn = get_connection()

    try:
        result = conn.execute(
            "SELECT COALESCE(SUM(quantity), 0) FROM inventory"
        ).fetchone()

        return f"Total available stock: {result[0]} units"

    finally:
        conn.close()


def get_low_stock_products():

    conn = get_connection()

    try:
        products = conn.execute("""
            SELECT
                p.product_name,
                i.quantity,
                i.minimum_stock
            FROM products p
            JOIN inventory i
            ON p.id = i.product_id
            WHERE i.quantity <= i.minimum_stock
            ORDER BY i.quantity
        """).fetchall()

        if not products:
            return "There are no low-stock products."

        result = "Low Stock Products:\n"

        for product in products:

            result += (
                f"- {product['product_name']}: "
                f"{product['quantity']} units available, "
                f"minimum required: {product['minimum_stock']}\n"
            )

        return result

    finally:
        conn.close()


def get_total_sales():

    conn = get_connection()

    try:
        result = conn.execute("""
            SELECT
                COALESCE(SUM(total_amount), 0),
                COUNT(*)
            FROM sales
        """).fetchone()

        return (
            f"Total revenue: ₹{result[0]:,.2f}\n"
            f"Total transactions: {result[1]}"
        )

    finally:
        conn.close()


def get_best_selling_products():

    conn = get_connection()

    try:
        products = conn.execute("""
            SELECT
                p.product_name,
                SUM(s.quantity_sold) AS total_sold
            FROM sales s
            JOIN products p
            ON p.id = s.product_id
            GROUP BY p.id, p.product_name
            ORDER BY total_sold DESC
            LIMIT 5
        """).fetchall()

        if not products:
            return "No sales data available."

        result = "Best Selling Products:\n"

        for product in products:

            result += (
                f"- {product['product_name']}: "
                f"{product['total_sold']} units sold\n"
            )

        return result

    finally:
        conn.close()


def get_inventory_value():

    conn = get_connection()

    try:
        result = conn.execute("""
            SELECT
                COALESCE(SUM(p.price * i.quantity), 0)
            FROM products p
            JOIN inventory i
            ON p.id = i.product_id
        """).fetchone()

        return (
            f"Current inventory value: ₹{result[0]:,.2f}"
        )

    finally:
        conn.close()