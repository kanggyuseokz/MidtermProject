from flask import Flask
from flask import Flask
from project.config.config import Config
from project.extensions import db, mail  # 확장 모듈 가져오기

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 확장 초기화
    db.init_app(app)
    mail.init_app(app)

    # Blueprint 등록
    from project.routes.api import api_bp
    from project.routes.admin import admin_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # DB 테이블 생성
    with app.app_context():
        from project.models import attack_log, blocked_ip  # 모델 import 필수
        db.create_all()

    return app