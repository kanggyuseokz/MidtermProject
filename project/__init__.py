from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from project.config.comfig import Config

# SQLAlchemy 객체 전역 생성
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    db.init_app(app)

    # 라우트 Blueprint 등록
    from project.routes.api import api_bp
    from project.routes.admin import admin_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # DB 초기화
    with app.app_context():
        from project.models.attack_log import AttackLog
        db.create_all()

    return app
