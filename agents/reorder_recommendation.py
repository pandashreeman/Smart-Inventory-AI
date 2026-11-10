import math
from database.db import get_connection


def get_reorder_recommendations(
    lead_time_days=7,
    target_coverage_days=14,
    safety_days=3
):
    """
    Generate smart reorder recommendations using
    current stock and the last 30 days of sales.

    No database records are modified.
    """

    conn = get_connection()

    try:

        products = conn.execute("""
            SELECT
                p.id AS product_id,
                p.product_name,
                p.price,
                i.quantity,
                i.minimum_stock,

                COALESCE(
                    SUM(
                        CASE
                            WHEN DATE(s.sale_date)
                            >= DATE('now', '-30 days')
                            THEN s.quantity_sold
                            ELSE 0
                        END
                    ), 0
                ) AS units_sold_30_days

            FROM products p

            JOIN inventory i
                ON p.id = i.product_id

            LEFT JOIN sales s
                ON p.id = s.product_id

            GROUP BY
                p.id,
                p.product_name,
                p.price,
                i.quantity,
                i.minimum_stock

            ORDER BY p.product_name
        """).fetchall()

        recommendations = []

        for product in products:

            current_stock = int(product["quantity"])
            minimum_stock = int(product["minimum_stock"])

            units_sold = int(
                product["units_sold_30_days"]
            )

            # Calculate average daily demand
            average_daily_demand = units_sold / 30

            # Calculate safety stock
            safety_stock = math.ceil(
                average_daily_demand * safety_days
            )

            # Calculate reorder point
            reorder_point = math.ceil(
                average_daily_demand * lead_time_days
                + safety_stock
            )

            # Calculate target stock
            demand_based_target = math.ceil(
                average_daily_demand
                * target_coverage_days
                + safety_stock
            )

            target_stock = max(
                minimum_stock,
                demand_based_target
            )

            # Calculate recommended quantity
            reorder_quantity = max(
                0,
                target_stock - current_stock
            )

            # Determine priority
            if current_stock == 0:

                priority = "Critical"

            elif current_stock <= minimum_stock:

                priority = "High"

            elif current_stock <= reorder_point:

                priority = "Medium"

            else:

                priority = "Normal"

            # Add recommendation
            recommendations.append({

                "product_id": product["product_id"],

                "product_name": product["product_name"],

                "current_stock": current_stock,

                "minimum_stock": minimum_stock,

                "units_sold_30_days": units_sold,

                "average_daily_demand": round(
                    average_daily_demand, 2
                ),

                "reorder_point": reorder_point,

                "target_stock": target_stock,

                "recommended_quantity": reorder_quantity,

                "priority": priority,

                "estimated_order_cost": round(
                    reorder_quantity * float(product["price"]),
                    2
                )

            })

        return recommendations

    finally:

        conn.close()


def get_reorder_summary():

    recommendations = get_reorder_recommendations()

    products_to_reorder = [
        product
        for product in recommendations
        if product["recommended_quantity"] > 0
    ]

    critical_products = [
        product
        for product in products_to_reorder
        if product["priority"] == "Critical"
    ]

    total_reorder_quantity = sum(
        product["recommended_quantity"]
        for product in products_to_reorder
    )

    total_estimated_cost = sum(
        product["estimated_order_cost"]
        for product in products_to_reorder
    )

    return {

        "total_products": len(recommendations),

        "products_to_reorder": len(products_to_reorder),

        "critical_products": len(critical_products),

        "total_reorder_quantity": total_reorder_quantity,

        "total_estimated_cost": round(
            total_estimated_cost, 2
        )

    }