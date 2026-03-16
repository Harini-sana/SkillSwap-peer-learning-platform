import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Harini@1511",   # 👈 put your MySQL password
    "database": "urlguard_db"
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("CREATE DATABASE IF NOT EXISTS urlguard_db")
    cur.execute("USE urlguard_db")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            url TEXT,
            prediction VARCHAR(20),
            risk_score FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def create_user(name, email, password):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        conn.commit()
        return True
    except mysql.connector.errors.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name FROM users WHERE email = %s AND password = %s",
        (email, password)
    )
    user = cur.fetchone()
    conn.close()
    return user

def save_record(url, prediction, risk_score):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history (url, prediction, risk_score) VALUES (%s, %s, %s)",
        (url, prediction, risk_score)
    )
    conn.commit()
    conn.close()

def get_history(limit=1000):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT url, prediction, risk_score, created_at FROM history ORDER BY id DESC LIMIT %s",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows