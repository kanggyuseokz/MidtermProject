import re
from project.utils.user_info import UserInput, UserInfo

# SQL Injection 탐지
class SQLIDetect:
    def __init__(self):
        # 기본적인 SQL 인젝션 패턴들
        self.patterns = [
            r"(?i)(\bor\b|\band\b).*(=|like)",  # OR 1=1, AND 조건
            r"(?i)union\s+select",              # UNION SELECT
            r"(?i)insert\s+into",               # INSERT INTO
            r"(?i)select.+from",                # SELECT FROM
            r"(?i)drop\s+table",                # DROP TABLE
            r"--",                              # 주석 기호
            r"'[ ]*or[ ]*'1'='1"                # ' OR '1'='1'
        ]

    def detect(self, input: UserInput) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, input.input_text):
                return True
        return False

    def cleanInput(self, input: UserInput) -> str:
        # 위험 키워드 제거 (기초적 방법)
        cleaned = re.sub(r"(--|;|'|\b(or|and|union|select|insert|drop)\b)", "", input.input_text, flags=re.IGNORECASE)
        return cleaned

    def processInput(self, input: UserInput):
        # 입력값이 공격인지 감지 
        is_attack = self.detect(input)
        # 공격이면 입력값을 정제(clean), 아니라면 원본을 그대로 사용
        cleaned = self.cleanInput(input) if is_attack else input.input_text
        # 최종 결과를 딕셔너리로 반환 (REST API에서 JSON으로 응답할 수 있게)
        return {
            "detected": is_attack,         # 공격 여부 (True/False)
            "cleaned_input": cleaned       # 정제된 입력값 or 원본 입력값
        }