from project.extensions import db

class AttackLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 고유 ID
    timestamp = db.Column(db.String(100))         # 공격 시각
    username = db.Column(db.String(100))          # 사용자 이름
    ip = db.Column(db.String(100))                # IP 주소
    attack_type = db.Column(db.String(20))        # 공격 유형 (XSS, SQLi 등)
    original = db.Column(db.Text)                 # 원본 입력
    cleaned = db.Column(db.Text)                  # 정제된 입력