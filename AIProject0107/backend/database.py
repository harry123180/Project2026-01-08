import sqlite3
from datetime import datetime

DATABASE = 'instance/tasks.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This enables name-based access to columns
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            client_name TEXT,
            start_time DATETIME NOT NULL,
            end_time DATETIME,
            completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)) DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_task(title, client_name=None, start_time=None, end_time=None):
    if start_time is None:
        start_time = datetime.now()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title, client_name, start_time, end_time) VALUES (?, ?, ?, ?)',
        (title, client_name, start_time, end_time)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

# Call init_db() to ensure the database and table exist when this module is imported
init_db()

if __name__ == '__main__':
    # This block will only run when database.py is executed directly
    # You can use it for testing or initial data seeding
    print("Initializing database and creating 'tasks' table...")
    init_db()
    print("Database initialized.")

    # Example of adding a task
    # task_id = add_task("與客戶A開會", "客戶A", datetime(2026, 1, 7, 10, 0), datetime(2026, 1, 7, 11, 0))
    # print(f"Added task with ID: {task_id}")
    
    # Example of fetching tasks
    # conn = get_db_connection()
    # tasks = conn.execute("SELECT * FROM tasks").fetchall()
    # for task in tasks:
    #     print(dict(task))
    # conn.close()
