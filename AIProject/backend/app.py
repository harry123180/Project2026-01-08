from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Event
from datetime import datetime
import os

app = Flask(__name__)
CORS(app) # 允許跨域請求

# 資料庫設定
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 初始化資料庫
with app.app_context():
    db.create_all()

@app.route('/api/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events])

@app.route('/api/events', methods=['POST'])
def add_event():
    try:
        data = request.json
        
        # 強健的日期處理邏輯
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        
        # 1. 處理開始時間
        if start_time_str and start_time_str.strip():
            try:
                start_time = datetime.fromisoformat(start_time_str)
            except ValueError:
                start_time = datetime.utcnow() # 格式錯誤就用當下
        else:
            start_time = datetime.utcnow() # 沒填就用當下

        # 2. 處理結束時間
        end_time = None
        if end_time_str and end_time_str.strip():
            try:
                end_time = datetime.fromisoformat(end_time_str)
            except ValueError:
                end_time = None

        new_event = Event(
            title=data.get('title') or "未命名行程", # 防止標題為空
            description=data.get('description', ''),
            start_time=start_time,
            end_time=end_time,
            color=data.get('color', '#3788d8')
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify(new_event.to_dict()), 201
    except Exception as e:
        print(f"Error adding event: {e}") # 在後端 Log 顯示錯誤
        return jsonify({"error": "伺服器處理錯誤，請檢查資料格式"}), 500

@app.route('/api/events/<int:id>', methods=['PUT'])
def update_event(id):
    event = Event.query.get_or_404(id)
    data = request.json
    
    if 'title' in data: event.title = data['title']
    if 'description' in data: event.description = data['description']
    if 'start_time' in data: event.start_time = datetime.fromisoformat(data['start_time'])
    if 'end_time' in data: event.end_time = datetime.fromisoformat(data['end_time'])
    if 'is_completed' in data: event.is_completed = data['is_completed']
    if 'color' in data: event.color = data['color']
    
    db.session.commit()
    return jsonify(event.to_dict())

@app.route('/api/events/<int:id>', methods=['DELETE'])
def delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5000)
