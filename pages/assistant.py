import streamlit as st

from agents.ai_assistant import (
    create_inventory_agent,
    ask_inventory_agent
)


@st.cache_resource
def load_agent():

    return create_inventory_agent()


def show_assistant():

    st.title("🤖 AI Inventory Assistant")

    st.write(
        "Ask questions about your products, stock and sales "
        "using Llama 3.1 8B."
    )

    st.divider()

    try:

        agent = load_agent()

    except Exception as error:

        st.error(f"Unable to initialize AI assistant: {error}")

        st.info(
            "Make sure Ollama is running and llama3.1:8b is installed."
        )

        return

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask something about your inventory..."
    )

    if question:

        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("AI is thinking..."):

                try:

                    answer = ask_inventory_agent(
                        agent,
                        question
                    )

                    st.markdown(answer)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as error:

                    st.error(f"AI Error: {error}")
                    st.info(
                        "Check that Ollama is running and "
                        "the Llama 3.1 model is available."
                    )