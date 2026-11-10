import json

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import create_agent

from agents.inventory_tools import (
    get_total_products,
    get_total_stock,
    get_low_stock_products,
    get_total_sales,
    get_best_selling_products,
    get_inventory_value
)

from agents.reorder_recommendation import (
    get_reorder_recommendations,
    get_reorder_summary
)

from agents.forecast_tools import (
    get_ml_demand_analysis,
    get_ml_forecast_summary
)


# INVENTORY TOOLS

@tool
def total_products():
    """Get total products in inventory."""
    return get_total_products()


@tool
def total_stock():
    """Get total available stock."""
    return get_total_stock()


@tool
def low_stock_products():
    """Find products at or below minimum stock."""
    return get_low_stock_products()


@tool
def total_sales():
    """Get total sales revenue and transactions."""
    return get_total_sales()


@tool
def best_selling_products():
    """Find the five best-selling products."""
    return get_best_selling_products()


@tool
def inventory_value():
    """Calculate current inventory value."""
    return get_inventory_value()


# REORDER TOOLS

@tool
def reorder_recommendations():
    """Get detailed inventory reorder recommendations."""

    result = get_reorder_recommendations()

    return json.dumps(result, indent=4)


@tool
def reorder_summary():
    """Get overall reorder summary and estimated cost."""

    result = get_reorder_summary()

    return json.dumps(result, indent=4)


# MACHINE LEARNING TOOLS

@tool
def ml_demand_forecast():
    """Analyze predicted demand for the next seven days for all products."""

    result = get_ml_demand_analysis(days=7)

    return json.dumps(
        result,
        indent=4,
        ensure_ascii=False
    )


@tool
def ml_forecast_summary():
    """Get an overall summary of seven-day ML demand forecasts."""

    result = get_ml_forecast_summary(days=7)

    return json.dumps(
        result,
        indent=4,
        ensure_ascii=False
    )


# CREATE AI AGENT

def create_inventory_agent():

    llm = ChatOllama(
        model="llama3.1:8b",
        temperature=0
    )

    tools = [
        total_products,
        total_stock,
        low_stock_products,
        total_sales,
        best_selling_products,
        inventory_value,
        reorder_recommendations,
        reorder_summary,
        ml_demand_forecast,
        ml_forecast_summary
    ]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
        You are a Smart Inventory Management AI Assistant.

        Your responsibilities:

        1. Analyze inventory.
        2. Identify low-stock products.
        3. Analyze sales performance.
        4. Calculate inventory value.
        5. Generate reorder recommendations.
        6. Analyze machine learning demand forecasts.
        7. Compare predicted demand with current stock.
        8. Explain which products need replenishment.

        IMPORTANT RULES:

        - Use tools for actual inventory information.
        - Use ml_demand_forecast for future demand questions.
        - Use ml_forecast_summary for overall forecast summaries.
        - Use reorder_recommendations for reorder questions.
        - Never invent product quantities or predictions.
        - Clearly mention when an ML model is unavailable.
        - Explain results in simple English.
        - Distinguish predicted demand from actual sales.
        - Do not modify inventory or purchase records.
        - Never claim that an order has been placed.
        - All recommendations require user approval.
        """
    )

    return agent


# ASK AI AGENT

def ask_inventory_agent(agent, question):

    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    })

    return response["messages"][-1].content