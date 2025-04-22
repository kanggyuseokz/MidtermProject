import bleach
from project.utils.user_info import UserInput, UserInfo

# XSS탐지 클래스
class XSSDetect:
    def __init__(self, ml_model=None):
        self.ml_model = ml_model

    def detect(self, input: UserInput) -> bool:
        """단순 룰 기반 탐지 (bleach 없이 패턴 기반)"""
        text = input.input_text.lower()
        return any(keyword in text for keyword in ["<script", "onerror", "javascript:", "iframe", "<img"])

    def cleanInput(self, input: UserInput) -> str:
        """bleach로 입력값 정제"""
        return bleach.clean(input.input_text)

    def predictML(self, input: UserInput) -> bool:
        """머신러닝 예측 (모델이 연결되어 있을 때만)"""
        if self.ml_model:
            return self.ml_model.predict([input.input_text])[0] == 1
        return False
    
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