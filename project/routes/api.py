from flask import Blueprint, request, jsonify
from project.services.xss_detect import XSSDetect
from project.services.sqli_detect import SQLIDetect
from project.utils.user_info import UserInfo, UserInput
from project.utils.logger import log_attack

api_bp = Blueprint('api', __name__, url_prefix='/api')

# XSS/SQLi 탐지 인스턴스
xss_engine = XSSDetect()
sqli_engine = SQLIDetect()

@api_bp.route('/input', methods=['POST'])
def handle_input():
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
    xss_result = xss_engine.process(user_input.input_text)
    sqli_result = sqli_engine.process(user_input.input_text)

    # 감지된 공격 저장
    detected_attacks = {}
    if xss_result['detected']:
        detected_attacks['XSS'] = xss_result
        log_attack(user_input, "XSS", xss_result['cleaned_input'])

    if sqli_result['detected']:
        detected_attacks['SQL_Injection'] = sqli_result
        log_attack(user_input, "SQLi", sqli_result['cleaned_input'])

    # 결과 응답 생성
    response = {
        "status": "processed",
        "input_summary": str(user_input),
        "detected_attacks": detected_attacks
    }

    if not detected_attacks:
        response["safe"] = True

    return jsonify(response)
