from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Task
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # 允許跨域請求，讓前端 Vue 可以呼叫

# 資料庫設定
# 將資料庫檔案存放在 backend 目錄下，方便查看
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schedule.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 應用程式啟動時建立資料表
with app.app_context():
    db.create_all()

# --- API Routes ---

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    # 取得所有行程，並依時間排序
    tasks = Task.query.order_by(Task.due_date).all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    try:
        # 處理日期字串轉換
        due_date_val = None
        if data.get('due_date'):
            due_date_val = datetime.fromisoformat(data.get('due_date'))
            
        new_task = Task(
            title=data.get('title'),
            description=data.get('description'),
            due_date=due_date_val
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify(new_task.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.json
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'is_completed' in data:
        task.is_completed = data['is_completed']
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        
    db.session.commit()
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'})

if __name__ == '__main__':
    # 開發模式啟動
    app.run(debug=True, port=5000)
