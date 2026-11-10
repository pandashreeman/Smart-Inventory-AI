import math

from database.db import get_connection
from models.demand_forecasting import forecast_demand


def get_ml_demand_analysis(days=7):

    """
    Analyze future demand using trained ML models.

    Compares predicted demand with current stock
    and calculates suggested replenishment quantities.

    This function does not modify the database.
    """

    conn = get_connection()

    try:

        products = conn.execute("""
            SELECT
                p.id AS product_id,
                p.product_name,
                i.quantity,
                i.minimum_stock
            FROM products p
            JOIN inventory i
                ON p.id = i.product_id
            ORDER BY p.product_name
        """).fetchall()

    finally:

        conn.close()

    if not products:

        return "No products found in inventory."

    results = []

    for product in products:

        product_id = product["product_id"]
        product_name = product["product_name"]

        current_stock = int(product["quantity"])
        minimum_stock = int(product["minimum_stock"])

        try:

            forecast_data, message = forecast_demand(
                product_id,
                days=days
            )

            if forecast_data is None:

                results.append({
                    "product": product_name,
                    "status": "Forecast unavailable",
                    "reason": message
                })

                continue

            predicted_demand = max(
                0,
                float(
                    forecast_data["Predicted Demand"].sum()
                )
            )

            predicted_demand = math.ceil(
                predicted_demand
            )

            # Maintain minimum stock as a buffer
            target_stock = (
                predicted_demand + minimum_stock
            )

            suggested_reorder = max(
                0,
                target_stock - current_stock
            )

            if current_stock == 0:

                priority = "Critical"

            elif suggested_reorder > 0:

                priority = "Reorder Suggested"

            else:

                priority = "Stock Sufficient"

            results.append({

                "product": product_name,

                "current_stock": current_stock,

                "minimum_stock": minimum_stock,

                "forecast_days": days,

                "predicted_demand": predicted_demand,

                "suggested_reorder": suggested_reorder,

                "priority": priority,

                "status": "Success"

            })

        except Exception as error:

            results.append({

                "product": product_name,

                "status": "Forecast Error",

                "reason": str(error)

            })

    return results


def get_ml_forecast_summary(days=7):

    results = get_ml_demand_analysis(days)

    if isinstance(results, str):

        return results

    successful = [
        item for item in results
        if item["status"] == "Success"
    ]

    unavailable = [
        item for item in results
        if item["status"] != "Success"
    ]

    total_predicted_demand = sum(
        item["predicted_demand"]
        for item in successful
    )

    total_reorder = sum(
        item["suggested_reorder"]
        for item in successful
    )

    return {

        "forecast_period_days": days,

        "total_products": len(results),

        "successful_forecasts": len(successful),

        "unavailable_forecasts": len(unavailable),

        "total_predicted_demand": total_predicted_demand,

        "total_suggested_reorder": total_reorder

    }