from project.extensions import db
from datetime import datetime

class BlockedIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), unique=True, nullable=False)
    blocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(100))
    count = db.Column(db.Integer, default=1)