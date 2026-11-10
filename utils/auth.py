import sqlite3
import hashlib
import secrets
import re

from database.db import get_connection


# Password hashing
def hash_password(password):
    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        310000
    ).hex()

    return salt + "$" + password_hash


# Verify password
def verify_password(password, stored_password):
    try:
        salt, original_hash = stored_password.split("$")

        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            310000
        ).hex()

        return secrets.compare_digest(new_hash, original_hash)

    except ValueError:
        return False


# Validate email
def validate_email(email):
    pattern = r"^[\w.+-]+@[\w-]+\.[\w.-]+$"
    return re.match(pattern, email) is not None


# Register user
def register_user(name, email, password):

    if not name.strip():
        return False, "Name is required."

    if not validate_email(email):
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        password_hash = hash_password(password)

        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        """, (name.strip(), email.strip().lower(), password_hash))

        conn.commit()

        return True, "Registration successful!"

    except sqlite3.IntegrityError:
        return False, "This email is already registered."

    except sqlite3.Error as error:
        return False, f"Database error: {error}"

    finally:
        conn.close()


# Login user
def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, name, email, password_hash
            FROM users
            WHERE email = ?
        """, (email.strip().lower(),))

        user = cursor.fetchone()

        if user and verify_password(password, user["password_hash"]):

            return True, {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }

        return False, "Invalid email or password."

    except sqlite3.Error as error:
        return False, f"Database error: {error}"

    finally:
        conn.close()
        