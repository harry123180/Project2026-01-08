from database import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    is_all_day = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='To Do')

    def to_dict(self):
        """將 Event 物件轉換為可序列化為 JSON 的字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start': self.start_time.isoformat() + 'Z', # 使用 FullCalendar 期望的 'start'
            'end': self.end_time.isoformat() + 'Z' if self.end_time else None, # 使用 FullCalendar 期望的 'end'
            'allDay': self.is_all_day, # 使用 FullCalendar 期望的 'allDay'
            'status': self.status,
        }
