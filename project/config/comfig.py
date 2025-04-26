class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost/attack_logs'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'CmNZZ7dL_fIylz6d2Rh5W2oL_NSSwOrTfAZ-e91Ujjw'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'kgs021225@gmail.com'   # 관리자 이메일
    MAIL_PASSWORD = 'vlxo fkbo zsyw otka'      # 앱 비밀번호 (Google 계정 → 앱 비밀번호 생성 필요)
    MAIL_DEFAULT_SENDER = 'kgs021225@gmail.com'