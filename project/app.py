from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bleach
import re
import smtplib
from email.mime.text import MIMEText
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/attack_logs'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    isApproved = db.Column(db.Boolean, default=False)

class AttackLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(100))
    username = db.Column(db.String(100))
    ip = db.Column(db.String(100))
    attack_type = db.Column(db.String(20))
    original = db.Column(db.Text)
    cleaned = db.Column(db.Text)

class UserInfo:
    def __init__(self, username: str, ip: str):
        self.username = username
        self.ip = ip

class UserInput:
    def __init__(self, input_text: str, user: UserInfo, timestamp: datetime = None):
        self.input_text = input_text
        self.user = user
        self.timestamp = timestamp if timestamp else datetime.now()

class XSSDetect:
    def detect(self, input: UserInput) -> bool:
        text = input.input_text.lower()
        return any(keyword in text for keyword in ["<script", "onerror", "javascript:", "iframe", "<img"])

    def cleanInput(self, input: UserInput) -> str:
        return bleach.clean(input.input_text)

    def processInput(self, input: UserInput):
        is_attack = self.detect(input)
        cleaned = self.cleanInput(input) if is_attack else input.input_text
        return {
            "detected": is_attack,
            "cleaned_input": cleaned
        }

class SQLIDetect:
    def __init__(self):
        self.patterns = [
            r"(?i)(\bor\b|\band\b).*(=|like)",
            r"(?i)union\s+select",
            r"(?i)insert\s+into",
            r"(?i)select.+from",
            r"(?i)drop\s+table",
            r"--",
            r"'[ ]*or[ ]*'1'='1"
        ]

    def detect(self, input: UserInput) -> bool:
        return any(re.search(pattern, input.input_text) for pattern in self.patterns)

    def cleanInput(self, input: UserInput) -> str:
        return re.sub(r"(--|;|'|\b(or|and|union|select|insert|drop)\b)", "", input.input_text, flags=re.IGNORECASE)

    def processInput(self, input: UserInput):
        is_attack = self.detect(input)
        cleaned = self.cleanInput(input) if is_attack else input.input_text
        return {
            "detected": is_attack,
            "cleaned_input": cleaned
        }

def send_alert_email(attack_type, user_input):
    sender = 'your_email@example.com'
    password = 'your_email_password'
    recipients = [admin.email for admin in Admin.query.filter_by(isApproved=True).all() if admin.email]

    if not recipients:
        return

    subject = f"[알림] {attack_type} 공격 탐지됨"
    body = f"{user_input.timestamp} - {user_input.user.username} ({user_input.user.ip})\n공격 내용: {user_input.input_text}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
    except Exception as e:
        print("메일 전송 실패:", str(e))

xss_engine = XSSDetect()
sqli_engine = SQLIDetect()

def log_attack(user_input: UserInput, attack_type: str, cleaned_text: str):
    log = AttackLog(
        timestamp=user_input.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        username=user_input.user.username,
        ip=user_input.user.ip,
        attack_type=attack_type,
        original=user_input.input_text,
        cleaned=cleaned_text
    )
    db.session.add(log)
    db.session.commit()
    send_alert_email(attack_type, user_input)

@app.route('/api/admins/<int:admin_id>', methods=['PATCH'])
@cross_origin()
def update_admin(admin_id):
    data = request.get_json()
    admin = Admin.query.get(admin_id)
    if not admin:
        return jsonify({'success': False, 'error': '관리자를 찾을 수 없습니다.'}), 404

    if data.get('currentPassword') != admin.password:
        return jsonify({'success': False, 'error': '현재 비밀번호가 일치하지 않습니다.'}), 403

    if 'newPassword' in data:
        admin.password = data['newPassword']
    if 'email' in data:
        admin.email = data['email']

    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/input', methods=['POST'])
@cross_origin()
def handle_input():
    data = request.get_json()
    if not data or 'inputText' not in data or 'username' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    input_text = data['inputText']
    username = data['username']
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    user = UserInfo(username=username, ip=ip)
    user_input = UserInput(input_text=input_text, user=user)

    xss_result = xss_engine.processInput(user_input)
    sqli_result = sqli_engine.processInput(user_input)

    detected_attacks = {}
    if xss_result['detected']:
        detected_attacks['XSS'] = xss_result
        log_attack(user_input, "XSS", xss_result['cleaned_input'])

    if sqli_result['detected']:
        detected_attacks['SQL_Injection'] = sqli_result
        log_attack(user_input, "SQLi", sqli_result['cleaned_input'])

    response = {
        "status": "processed",
        "input_summary": f"{user_input.timestamp} {username} ({ip}): {input_text}",
        "detected_attacks": detected_attacks
    }
    if not detected_attacks:
        response["safe"] = True

    return jsonify(response)

@app.route('/api/register', methods=['POST', 'OPTIONS'])
@cross_origin()
def register_admin():
    data = request.get_json()
    print("📥 받은 데이터:", data)

    if not data or not all(k in data for k in ('name', 'username', 'password', 'email')):
        return jsonify({'success': False, 'error': '필수 정보 누락'}), 400

    if Admin.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'error': '이미 존재하는 아이디입니다.'}), 409

    new_admin = Admin(
        name=data['name'],
        username=data['username'],
        password=data['password'],
        email=data['email'],
        isApproved=False
    )
    db.session.add(new_admin)
    db.session.commit()
    print("✅ 등록 완료:", new_admin.username)
    return jsonify({'success': True})

@app.route('/api/login', methods=['POST'])
@cross_origin()
def login_admin():
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({'success': False, 'error': '필수 정보 누락'}), 400

    admin = Admin.query.filter_by(username=data['username'], password=data['password']).first()
    if admin:
        if not admin.isApproved:
            return jsonify({'success': False, 'error': '승인 대기 중입니다.'})
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': '로그인 실패'})

@app.route('/api/admins', methods=['GET'])
@cross_origin()
def get_admins():
    admins = Admin.query.all()
    return jsonify([{
        'id': admin.id,
        'name': admin.name,
        'username': admin.username,
        'email': admin.email,
        'isApproved': admin.isApproved
    } for admin in admins])

@app.route('/api/approve/<int:admin_id>', methods=['POST'])
@cross_origin()
def approve_admin(admin_id):
    admin = Admin.query.get(admin_id)
    if not admin:
        return jsonify({'success': False, 'error': '관리자를 찾을 수 없습니다.'}), 404

    data = request.get_json()
    if 'isApproved' in data:
        admin.isApproved = data['isApproved']
        db.session.commit()
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': '승인 값 누락'}), 400

@app.route('/api/admins/<int:admin_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin()
def delete_admin(admin_id):
    print(f"삭제 요청 ID: {admin_id}")
    admin = Admin.query.get(admin_id)
    if not admin:
        print("❌ 관리자 없음")
        return jsonify({'success': False, 'error': '관리자를 찾을 수 없습니다.'}), 404

    db.session.delete(admin)
    db.session.commit()
    print(f"✅ 삭제 완료: {admin.username}")
    return jsonify({'success': True})

@app.route('/admin/logs', methods=['GET'])
@cross_origin()
def get_logs():
    logs = AttackLog.query.order_by(AttackLog.id.desc()).all()
    return jsonify([{
        "timestamp": log.timestamp,
        "username": log.username,
        "ip": log.ip,
        "attack_type": log.attack_type,
        "original": log.original,
        "cleaned": log.cleaned
    } for log in logs])
@app.route('/api/admins/update', methods=['PATCH'])
@cross_origin()
def update_admin_info():
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'currentPassword')):
        return jsonify({'success': False, 'error': '필수 정보 누락'}), 400

    admin = Admin.query.filter_by(username=data['username'], password=data['currentPassword']).first()
    if not admin:
        return jsonify({'success': False, 'error': '비밀번호가 일치하지 않거나 사용자를 찾을 수 없습니다.'}), 404

    if 'newPassword' in data and data['newPassword']:
        admin.password = data['newPassword']
    if 'email' in data and data['email']:
        admin.email = data['email']

    db.session.commit()
    return jsonify({'success': True})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
