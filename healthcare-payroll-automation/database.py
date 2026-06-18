import sqlite3
import pandas as pd
from pathlib import Path


DB_PATH = Path("data/payroll.db")


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            weekly_authorized_hours REAL NOT NULL,
            active_status TEXT DEFAULT 'Active'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caretakers (
            caretaker_id INTEGER PRIMARY KEY AUTOINCREMENT,
            caretaker_name TEXT NOT NULL,
            hourly_rate REAL NOT NULL,
            active_status TEXT DEFAULT 'Active'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts (
            shift_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            caretaker_id INTEGER NOT NULL,
            service_date TEXT NOT NULL,
            clock_in TEXT,
            clock_out TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(client_id),
            FOREIGN KEY (caretaker_id) REFERENCES caretakers(caretaker_id)
        )
    """)

    conn.commit()
    conn.close()


def add_client(client_name, weekly_authorized_hours):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clients (client_name, weekly_authorized_hours)
        VALUES (?, ?)
    """, (client_name, weekly_authorized_hours))

    conn.commit()
    conn.close()


def add_caretaker(caretaker_name, hourly_rate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO caretakers (caretaker_name, hourly_rate)
        VALUES (?, ?)
    """, (caretaker_name, hourly_rate))

    conn.commit()
    conn.close()


def add_shift(client_id, caretaker_id, service_date, clock_in, clock_out):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO shifts (
            client_id,
            caretaker_id,
            service_date,
            clock_in,
            clock_out
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        client_id,
        caretaker_id,
        service_date,
        clock_in,
        clock_out
    ))

    conn.commit()
    conn.close()


def update_client_hours(client_id, weekly_authorized_hours):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clients
        SET weekly_authorized_hours = ?
        WHERE client_id = ?
    """, (weekly_authorized_hours, client_id))

    conn.commit()
    conn.close()


def update_caretaker_rate(caretaker_id, hourly_rate):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE caretakers
        SET hourly_rate = ?
        WHERE caretaker_id = ?
    """, (hourly_rate, caretaker_id))

    conn.commit()
    conn.close()


def get_clients_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM clients", conn)
    conn.close()
    return df


def get_caretakers_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM caretakers", conn)
    conn.close()
    return df


def get_shifts_df():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            shifts.client_id,
            clients.client_name,
            shifts.caretaker_id,
            caretakers.caretaker_name,
            shifts.service_date,
            shifts.clock_in,
            shifts.clock_out
        FROM shifts
        JOIN clients ON shifts.client_id = clients.client_id
        JOIN caretakers ON shifts.caretaker_id = caretakers.caretaker_id
    """, conn)

    conn.close()
    return df
def get_all_clients():
    return get_clients_df()


def get_all_caretakers():
    return get_caretakers_df()


def get_all_shifts():
    return get_shifts_df()


def update_client(client_id, client_name, weekly_authorized_hours, active_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clients
        SET client_name = ?, weekly_authorized_hours = ?, active_status = ?
        WHERE client_id = ?
    """, (client_name, weekly_authorized_hours, active_status, client_id))

    conn.commit()
    conn.close()


def update_caretaker(caretaker_id, caretaker_name, hourly_rate, active_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE caretakers
        SET caretaker_name = ?, hourly_rate = ?, active_status = ?
        WHERE caretaker_id = ?
    """, (caretaker_name, hourly_rate, active_status, caretaker_id))

    conn.commit()
    conn.close()


def delete_client(client_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clients WHERE client_id = ?", (client_id,))

    conn.commit()
    conn.close()


def delete_caretaker(caretaker_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM caretakers WHERE caretaker_id = ?", (caretaker_id,))

    conn.commit()
    conn.close()


def delete_shift(shift_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM shifts WHERE shift_id = ?", (shift_id,))

    conn.commit()
    conn.close()


def get_shifts_with_ids_df():
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            shifts.shift_id,
            shifts.client_id,
            clients.client_name,
            shifts.caretaker_id,
            caretakers.caretaker_name,
            shifts.service_date,
            shifts.clock_in,
            shifts.clock_out
        FROM shifts
        JOIN clients ON shifts.client_id = clients.client_id
        JOIN caretakers ON shifts.caretaker_id = caretakers.caretaker_id
        ORDER BY shifts.service_date DESC
    """, conn)

    conn.close()

    return df

def export_tables_to_csv():
    get_clients_df().to_csv("data/clients.csv", index=False)
    get_caretakers_df().to_csv("data/caretakers.csv", index=False)
    get_shifts_df().to_csv("data/ltss_shifts.csv", index=False)