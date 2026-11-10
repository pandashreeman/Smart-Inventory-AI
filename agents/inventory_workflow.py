from agents.ai_assistant import (
    create_inventory_agent,
    ask_inventory_agent
)


def run_inventory_analysis():

    """
    Run a complete inventory analysis using
    the LangChain AI agent and inventory tools.
    """

    print("\n" + "=" * 55)
    print("SMART INVENTORY AUTOMATED ANALYSIS")
    print("=" * 55)

    print("\nStep 1: Initializing AI Agent...")

    try:

        agent = create_inventory_agent()

        print("AI Agent initialized successfully!")

    except Exception as error:

        return f"Unable to initialize AI Agent: {error}"

    # Analysis request
    analysis_question = """
    Perform a complete analysis of my inventory.

    Use the available tools to collect actual information.

    Analyze these areas:

    1. Total number of products.
    2. Total available stock.
    3. Products with low stock.
    4. Total sales revenue.
    5. Best-selling products.
    6. Current inventory value.
    7. Smart reorder recommendations.
    8. Estimated reorder cost.

    After collecting the information:

    - Prepare a clear business analysis.
    - Identify products requiring urgent attention.
    - Explain which products should be reordered.
    - Explain the recommended reorder quantities.
    - Suggest practical inventory improvements.
    - Mention if sales history is insufficient.

    Use actual database information.
    Do not invent numbers.

    Do not modify stock or create purchase orders.
    Only provide analysis and recommendations.

    Write the final report using simple English.
    """

    print("\nStep 2: Analyzing Inventory...")

    try:

        result = ask_inventory_agent(
            agent,
            analysis_question
        )

        print("\nStep 3: Analysis Completed!")

        return result

    except Exception as error:

        return f"Inventory analysis failed: {error}"


def show_inventory_analysis():

    print("\nGenerating Inventory Analysis...")

    report = run_inventory_analysis()

    print("\n" + "=" * 55)
    print("FINAL INVENTORY ANALYSIS REPORT")
    print("=" * 55)

    print(report)

    print("\n" + "=" * 55)
    print("ANALYSIS FINISHED")
    print("=" * 55)


if __name__ == "__main__":

    show_inventory_analysis()