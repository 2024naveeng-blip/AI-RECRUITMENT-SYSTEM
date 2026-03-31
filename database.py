"""
Project: TalentSphere Professional Assessment System
Module: database.py
Description: Data Persistence Layer for User Identity and Evaluation Records
"""

import sqlite3

def create_tables():
    conn = sqlite3.connect('system_data.db')
    c = conn.cursor()
    # Table for User Authentication
    c.execute('''CREATE TABLE IF NOT EXISTS system_users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    # Table for Performance Records
    c.execute('''CREATE TABLE IF NOT EXISTS evaluation_records 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, module_type TEXT, 
                  performance_rating TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('system_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO system_users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('system_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM system_users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def add_record(user_id, module, rating, time):
    conn = sqlite3.connect('system_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO evaluation_records (user_id, module_type, performance_rating, timestamp) VALUES (?, ?, ?, ?)", 
              (user_id, module, rating, time))
    conn.commit()
    conn.close()

def get_user_logs(user_id):
    conn = sqlite3.connect('system_data.db')
    c = conn.cursor()
    c.execute("SELECT module_type, performance_rating, timestamp FROM evaluation_records WHERE user_id=?", (user_id,))
    logs = c.fetchall()
    conn.close()
    return logs