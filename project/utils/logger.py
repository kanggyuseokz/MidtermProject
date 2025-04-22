from project import db
from project.models.attack_log import AttackLog

def log_attack(user_input, attack_type: str, cleaned_text: str):
    """
    공격 로그를 데이터베이스에 저장하는 함수
    :param user_input: UserInput 객체
    :param attack_type: 'XSS' 또는 'SQLi'
    :param cleaned_text: 필터링 또는 정제된 입력값
    """
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
