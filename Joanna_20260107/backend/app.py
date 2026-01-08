import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db
from models import Event
from datetime import datetime

# --- App Initialization ---
app = Flask(__name__)

# --- Configuration ---
# 根據絕對路徑設定資料庫 URI
project_dir = os.path.dirname(os.path.abspath(__file__))
# 確保 instance 資料夾存在
instance_path = os.path.join(project_dir, 'instance')
os.makedirs(instance_path, exist_ok=True)
database_file = f"sqlite:///{os.path.join(instance_path, 'schedule.db')}"
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- Extensions ---
# 啟用 CORS，允許來自所有來源的請求，這在開發中很方便
CORS(app, resources={r"/api/*": {"origins": "*"}})
# 將 SQLAlchemy 物件與 Flask app 關聯
db.init_app(app)

# --- CLI Commands ---
@app.cli.command("init-db")
def init_db_command():
    """清除現有資料並建立新的資料表"""
    with app.app_context():
        db.create_all()
    print("Initialized the database.")

# --- API Endpoints ---

@app.route('/api/events', methods=['GET'])
def get_events():
    """根據查詢參數中的 start 和 end 日期獲取事件列表，如果沒有則獲取所有事件"""
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    query = Event.query

    if start_str and end_str:
        try:
            # FullCalendar 可能會傳送不同格式的日期時間字串，這裡做一些容錯處理
            start_date = datetime.fromisoformat(start_str.split('T')[0])
            end_date = datetime.fromisoformat(end_str.split('T')[0])
            query = query.filter(
                Event.start_time < end_date,
                Event.end_time > start_date
            )
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO 8601."}), 400
    
    events = query.all()
    
    return jsonify([event.to_dict() for event in events])

@app.route('/api/events', methods=['POST'])
def create_event():
    """創建一個新事件"""
    data = request.get_json()
    if not data or not data.get('title') or not data.get('start_time'):
        return jsonify({"error": "Missing required fields: title, start_time"}), 400

    try:
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00')) if data.get('end_time') else start_time
    except ValueError:
        return jsonify({"error": "Invalid date format for start_time or end_time"}), 400

    new_event = Event(
        title=data['title'],
        description=data.get('description'),
        start_time=start_time,
        end_time=end_time,
        is_all_day=data.get('is_all_day', False),
        status=data.get('status', 'To Do')
    )
    
    db.session.add(new_event)
    db.session.commit()
    
    return jsonify(new_event.to_dict()), 201

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """更新一個現有事件"""
    event = Event.query.get_or_404(event_id)
    data = request.get_json()

    try:
        if 'start_time' in data:
            event.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        if 'end_time' in data and data['end_time']:
            event.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        else:
            # 如果 end_time 未提供或為 null，可以將其設為 start_time
            event.end_time = event.start_time
    except (ValueError, KeyError):
        return jsonify({"error": "Invalid date format or missing key"}), 400

    event.title = data.get('title', event.title)
    event.description = data.get('description', event.description)
    event.is_all_day = data.get('is_all_day', event.is_all_day)
    event.status = data.get('status', event.status)
    
    db.session.commit()
    
    return jsonify(event.to_dict())

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """刪除一個事件"""
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    
    return jsonify({"message": "Event deleted successfully"})

# --- Main Execution ---
if __name__ == '__main__':
    # 執行 Flask app
    # host='0.0.0.0' 讓區域網路中的其他裝置可以存取
    app.run(host='0.0.0.0', port=5000, debug=True)
