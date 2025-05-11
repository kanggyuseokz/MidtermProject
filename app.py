from project import create_app
from project.extensions import db

app = create_app()          # 앱 인스턴스 생성
if __name__ == '__main__':
    with app.app_context():     # 앱 컨텍스트 활성화
        db.create_all()         # 모델 기반 테이블 생성
    app.run(debug=True)         # 서버 실행