from flask import Blueprint, request, jsonify, current_app
from project.utils.emailer import send_attack_alert_mail
from project.services.xss_detect import XSSDetect
from project.services.sqli_detect import SQLIDetect
from project.utils.user_info import UserInfo, UserInput
from project.utils.logger import log_attack
from project.utils.ip_blocker import is_ip_blocked, record_attack_and_check_block

api_bp = Blueprint('api', __name__, url_prefix='/api')

# XSS/SQLi 탐지 인스턴스
xss_engine = XSSDetect()
sqli_engine = SQLIDetect()

@api_bp.route('/input', methods=['POST'])
def handle_input():
    # IP 추출
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    
    # 클라이언트에서 전달한 JSON 데이터 받기
    data = request.get_json()
    if not data or 'inputText' not in data or 'username' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    input_text = data['inputText']
    username = data['username']
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    # 사용자 정보 및 입력 객체 생성
    user = UserInfo(username=username, ip=ip)
    user_input = UserInput(input_text=input_text, user=user)

    # 공격 탐지 실행
    xss_result = xss_engine.processInput(user_input)
    sqli_result = sqli_engine.processInput(user_input)

    # 감지된 공격 저장
    detected_attacks = {}
    if xss_result['detected']:
        detected_attacks['XSS'] = xss_result
        log_attack(user_input, "XSS", xss_result['cleaned_input'])
        send_attack_alert_mail(current_app._get_current_object(), "XSS", user_input, xss_result['cleaned_input'])
        record_attack_and_check_block(ip, "XSS")

    if sqli_result['detected']:
        detected_attacks['SQL_Injection'] = sqli_result
        log_attack(user_input, "SQLi", sqli_result['cleaned_input'])
        send_attack_alert_mail(current_app._get_current_object(), "SQL Injection", user_input, sqli_result['cleaned_input'])
        record_attack_and_check_block(ip, "SQLi")

    # 결과 응답 생성
    response = {
        "status": "processed",
        "input_summary": str(user_input),
        "detected_attacks": detected_attacks
    }

    if not detected_attacks:
        response["safe"] = True

    # 차단된 IP인지 먼저 확인
    if is_ip_blocked(ip):
        return jsonify({"error": "Your IP is blocked"}), 403

    return jsonify(response)
