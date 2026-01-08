from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
from backend.database import get_db_connection, init_db

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Ensure the database is initialized when the app starts
with app.app_context():
    init_db()

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()

    start_param = request.args.get('start')
    end_param = request.args.get('end')

    query = "SELECT * FROM tasks"
    params = []

    if start_param and end_param:
        query += " WHERE start_time BETWEEN ? AND ?"
        params.append(start_param)
        params.append(end_param)
    elif start_param:
        query += " WHERE start_time >= ?"
        params.append(start_param)
    elif end_param:
        query += " WHERE start_time <= ?"
        params.append(end_param)

    cursor.execute(query, params)
    tasks = cursor.fetchall()
    conn.close()

    tasks_list = []
    for task in tasks:
        task_dict = dict(task)
        # Convert boolean from 0/1 to actual boolean
        task_dict['completed'] = bool(task_dict['completed'])
        tasks_list.append(task_dict)
    
    return jsonify(tasks_list)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get('title')
    client_name = data.get('client_name')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    # Parse start_time; if not provided, use current time
    start_time = datetime.now()
    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00')) # Handle 'Z' for UTC
        except ValueError:
            return jsonify({"error": "Invalid start_time format"}), 400
    
    # Parse end_time if provided
    end_time = None
    if end_time_str:
        try:
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00')) # Handle 'Z' for UTC
        except ValueError:
            return jsonify({"error": "Invalid end_time format"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title, client_name, start_time, end_time) VALUES (?, ?, ?, ?)',
        (title, client_name, start_time.isoformat(), end_time.isoformat() if end_time else None)
    )
    conn.commit()
    new_task_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": new_task_id,
        "title": title,
        "client_name": client_name,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat() if end_time else None,
        "completed": False,
        "created_at": datetime.now().isoformat() # This will be the creation time, not necessarily from DB
    }), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if task exists
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    # Dynamically build the SET part of the SQL query
    update_fields = []
    update_values = []
    
    # Supported fields for update
    supported_fields = ['title', 'client_name', 'start_time', 'end_time', 'completed']

    for field in supported_fields:
        if field in data:
            update_fields.append(f"{field} = ?")
            # Handle boolean conversion for 'completed'
            if field == 'completed':
                update_values.append(bool(data[field]))
            else:
                update_values.append(data[field])
    
    if not update_fields:
        conn.close()
        return jsonify({"error": "No valid fields to update"}), 400

    query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
    update_values.append(task_id)

    cursor.execute(query, tuple(update_values))
    conn.commit()

    # Fetch the updated task to return
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    updated_task = dict(cursor.fetchone())
    conn.close()
    
    # Convert boolean from 0/1 to actual boolean before returning
    updated_task['completed'] = bool(updated_task['completed'])

    return jsonify(updated_task)


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if task exists before deleting
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Task with id {task_id} deleted successfully"}), 200


if __name__ == '__main__':
    # It's good practice to run Flask apps in development mode
    # with debug=True, but for production, this should be False.
    # The host='0.0.0.0' makes it accessible from other devices on the network.
    app.run(debug=True, host='0.0.0.0', port=5000)
