
import sqlite3

DB_NAME = "inventory.db"


# ---------------------------------
# DATABASE CONNECTION
# ---------------------------------

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------
# CREATE DATABASE TABLES
# ---------------------------------

def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # 1. USERS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. SUPPLIERS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT
            )
        """)

        # 3. PRODUCTS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                category TEXT,
                price REAL DEFAULT 0,
                description TEXT,
                supplier_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (supplier_id)
                REFERENCES suppliers(id)
                ON DELETE SET NULL
            )
        """)

        # 4. INVENTORY TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER UNIQUE NOT NULL,
                quantity INTEGER DEFAULT 0,
                minimum_stock INTEGER DEFAULT 10,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (product_id)
                REFERENCES products(id)
                ON DELETE CASCADE
            )
        """)

        # 5. SALES TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity_sold INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_amount REAL NOT NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (product_id)
                REFERENCES products(id)
            )
        """)

        # 6. PURCHASES TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                supplier_id INTEGER,
                quantity INTEGER NOT NULL,
                unit_cost REAL DEFAULT 0,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expected_delivery DATE,
                status TEXT DEFAULT 'Pending',

                FOREIGN KEY (product_id)
                REFERENCES products(id),

                FOREIGN KEY (supplier_id)
                REFERENCES suppliers(id)
                ON DELETE SET NULL
            )
        """)

        # 7. STOCK MOVEMENTS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                movement_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                notes TEXT,
                movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (product_id)
                REFERENCES products(id)
            )
        """)

        # 8. ML PREDICTIONS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                predicted_demand REAL,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                forecast_period TEXT,

                FOREIGN KEY (product_id)
                REFERENCES products(id)
            )
        """)

        # 9. AI ASSISTANT HISTORY TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question TEXT NOT NULL,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE SET NULL
            )
        """)

        # 10. STOCK ALERTS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                alert_message TEXT NOT NULL,
                alert_type TEXT DEFAULT 'Low Stock',
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (product_id)
                REFERENCES products(id)
            )
        """)

        # CREATE INDEXES FOR FASTER SEARCHING
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_product
            ON sales(product_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_date
            ON sales(sale_date)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_movements_product
            ON stock_movements(product_id)
        """)

        conn.commit()

        print("Database and tables created successfully!")

    except sqlite3.Error as error:
        conn.rollback()
        print("Database Error:", error)

    finally:
        conn.close()


# ---------------------------------
# TEST DATABASE
# ---------------------------------

if __name__ == "__main__":
    create_tables()

