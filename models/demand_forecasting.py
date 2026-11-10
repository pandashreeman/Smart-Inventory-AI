import os
import joblib
import pandas as pd
import numpy as np

from datetime import timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from database.db import get_connection


MODEL_FOLDER = "saved_models"

os.makedirs(MODEL_FOLDER, exist_ok=True)


# ------------------------------------------------
# 1. Load historical sales data
# ------------------------------------------------

def load_sales_data():

    conn = get_connection()

    try:

        query = """
            SELECT
                p.id AS product_id,
                p.product_name,
                DATE(s.sale_date) AS sale_date,
                SUM(s.quantity_sold) AS quantity_sold
            FROM sales s
            JOIN products p
            ON s.product_id = p.id
            GROUP BY
                p.id,
                p.product_name,
                DATE(s.sale_date)
            ORDER BY sale_date
        """

        data = pd.read_sql_query(query, conn)

        return data

    finally:
        conn.close()


# ------------------------------------------------
# 2. Prepare daily sales data
# ------------------------------------------------

def prepare_product_data(data, product_id):

    product_data = data[
        data["product_id"] == product_id
    ].copy()

    if product_data.empty:
        return pd.DataFrame()

    product_data["sale_date"] = pd.to_datetime(
        product_data["sale_date"]
    )

    product_data = product_data.groupby(
        "sale_date"
    )["quantity_sold"].sum()

    date_range = pd.date_range(
        start=product_data.index.min(),
        end=product_data.index.max(),
        freq="D"
    )

    product_data = product_data.reindex(
        date_range,
        fill_value=0
    )

    product_data = product_data.rename(
        "quantity_sold"
    ).to_frame()

    return product_data


# ------------------------------------------------
# 3. Create Machine Learning features
# ------------------------------------------------

def create_features(data):

    df = data.copy()

    df["day"] = df.index.day
    df["month"] = df.index.month
    df["day_of_week"] = df.index.dayofweek

    df["lag_1"] = df["quantity_sold"].shift(1)
    df["lag_7"] = df["quantity_sold"].shift(7)

    df["rolling_mean_7"] = (
        df["quantity_sold"]
        .shift(1)
        .rolling(window=7)
        .mean()
    )

    df = df.dropna()

    return df


# ------------------------------------------------
# 4. Train Random Forest model
# ------------------------------------------------

def train_model(product_id):

    all_sales = load_sales_data()

    if all_sales.empty:
        return None, "No sales data available."

    product_data = prepare_product_data(
        all_sales,
        product_id
    )

    if len(product_data) < 15:
        return None, (
            "At least 15 days of sales history are required "
            "to train this forecasting model."
        )

    training_data = create_features(product_data)

    if len(training_data) < 8:
        return None, "Not enough training records available."

    feature_columns = [
        "day",
        "month",
        "day_of_week",
        "lag_1",
        "lag_7",
        "rolling_mean_7"
    ]

    X = training_data[feature_columns]
    y = training_data["quantity_sold"]

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        max_depth=8
    )

    model.fit(X, y)

    predictions = model.predict(X)

    mae = mean_absolute_error(y, predictions)

    model_path = os.path.join(
        MODEL_FOLDER,
        f"product_{product_id}_model.joblib"
    )

    joblib.dump(
        model,
        model_path
    )

    return {
        "model": model,
        "mae": mae,
        "model_path": model_path
    }, "Model trained successfully."


# ------------------------------------------------
# 5. Generate future demand predictions
# ------------------------------------------------

def forecast_demand(product_id, days=7):

    model_path = os.path.join(
        MODEL_FOLDER,
        f"product_{product_id}_model.joblib"
    )

    if not os.path.exists(model_path):

        return None, (
            "Please train the model before generating predictions."
        )

    all_sales = load_sales_data()

    product_data = prepare_product_data(
        all_sales,
        product_id
    )

    if len(product_data) < 15:
        return None, "Not enough historical sales data."

    model = joblib.load(model_path)

    history = list(
        product_data["quantity_sold"].astype(float)
    )

    last_date = product_data.index[-1]

    forecast_results = []

    for i in range(1, days + 1):

        forecast_date = last_date + timedelta(days=i)

        features = pd.DataFrame([{
            "day": forecast_date.day,
            "month": forecast_date.month,
            "day_of_week": forecast_date.dayofweek,
            "lag_1": history[-1],
            "lag_7": history[-7],
            "rolling_mean_7": np.mean(history[-7:])
        }])

        predicted_quantity = model.predict(features)[0]

        predicted_quantity = max(
            0,
            round(float(predicted_quantity), 2)
        )

        forecast_results.append({
            "Date": forecast_date.strftime("%Y-%m-%d"),
            "Predicted Demand": predicted_quantity
        })

        history.append(predicted_quantity)

    return pd.DataFrame(forecast_results), "Forecast generated successfully."