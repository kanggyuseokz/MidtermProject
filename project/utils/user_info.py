from datetime import datetime

class UserInfo:
    def __init__(self, username: str, ip: str):
        self.username = username
        self.ip = ip

    def __str__(self):
        return f"{self.username} ({self.ip})"

class UserInput:
    def __init__(self, input_text: str, user: UserInfo, timestamp: datetime = None):
        self.input_text = input_text
        self.user = user
        self.timestamp = timestamp if timestamp else datetime.now()

    def __str__(self):
        return f"[{self.timestamp}] {self.user}: {self.input_text}"
