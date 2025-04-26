from flask_mail import Message
from flask import current_app
from project import db
from project.models.attack_log import AttackLog

def send_attack_alert_mail(app, attack_type, user_input, cleaned_text):
    from flask_mail import Mail
    mail = Mail(app)  # 앱 인스턴스에서 Mail 객체 생성

    msg = Message(
        subject=f"[경고] {attack_type} 공격 발생!",
        recipients=['gnlvkfka1592@gmail.com'],  # 관리자 이메일
        body=f"""[보안 경고] {attack_type} 공격 탐지됨!
            시간: {user_input.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            사용자: {user_input.user.username} ({user_input.user.ip})
            원본 입력: {user_input.input_text}
            정제 결과: {cleaned_text}
            """
    )
    mail.send(msg)