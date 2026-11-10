
import streamlit as st

from utils.auth import register_user


def show_register():

    st.title("Create Your Account")

    st.write("Register to access Smart Inventory Assistant.")

    with st.form("register_form"):

        name = st.text_input("Full Name")

        email = st.text_input("Email Address")

        password = st.text_input(
            "Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        submit = st.form_submit_button(
            "Create Account",
            use_container_width=True
        )

        if submit:

            if not name.strip() or not email.strip():
                st.error("Please fill in all required fields.")

            elif password != confirm_password:
                st.error("Passwords do not match.")

            else:

                success, message = register_user(
                    name,
                    email,
                    password
                )

                if success:
                    st.success(message)
                    st.info("You can now log in using your account.")

                else:
                    st.error(message)

