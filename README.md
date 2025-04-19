# Capstone Design Project
## 2025년 1학기 캡스톤
---
# 🛡️ Flask XSS & SQL Injection 방어 시스템

이 프로젝트는 **Flask** 기반으로 개발된 웹 보안 시스템으로, **XSS(Cross-Site Scripting)** 및 **SQL Injection** 공격을 탐지 및 방어하며, 모든 공격 로그를 **MySQL 데이터베이스**에 저장하고 실시간 모니터링할 수 있도록 설계되었습니다.

---

## 🧩 주요 기능 (현재 구현 완료)

| 기능 항목                | 설명                                                                 |
|-------------------------|----------------------------------------------------------------------|
| ✅ Flask 서버 및 API     | Flask 기반 REST API 구축 및 서버 실행                               |
| ✅ MySQL 연동            | 사용자 데이터 및 공격 로그 저장용 데이터베이스 연동                |
| ✅ XSS 방어              | `bleach` 라이브러리를 이용한 입력값 필터링                         |
| ✅ SQL Injection 방어    | SQLAlchemy ORM + 파라미터화 쿼리 사용                               |
| ✅ 로그 기록             | 공격 탐지 시 로그 파일 + DB 저장                                     |
| ✅ 관리자 API            | 관리자 전용 로그 조회/필터링 기능                                   |
| ✅ JSON 응답             | 모든 결과는 JSON 형식으로 반환 (Postman 테스트 가능)               |

---

## 🚀 향후 구현 예정

- 🔔 **실시간 알림 시스템** (공격 발생 시 관리자 알림)
- 🔐 **API 사용 제한 (Rate Limit)**
- ⛔ **공격자 IP 차단 기능**
- 💾 **로그 파일 백업 및 다운로드**
- 🖥️ **관리자 대시보드 UI 개발**

---

## 🧱 시스템 아키텍처

```text
사용자 (Postman 등)
        ↓
[Flask Web Server]
        ↓
[SQL Injection 방어 레이어] → (DB 안전 처리)
        ↓
[XSS 방어 레이어] → (입력값 필터링)
        ↓
[MySQL DB]
   └─ 사용자 데이터
   └─ 공격 로그
        ↓
[실시간 공격 탐지 시스템]
        ↓
[관리자 대시보드 / 알림 시스템]
```
```
📂 프로젝트 구조
bash
복사
편집
project/
│
├── app.py               # Flask 메인 서버
├── models.py            # SQLAlchemy 모델 정의
├── database.py          # DB 연결 모듈
├── detection/           # XSS / SQL Injection 탐지 로직
├── logs/                # 공격 로그 저장
├── templates/           # 향후 대시보드 UI용 HTML
└── README.md
```
🛠️ 사용 기술 스택
Language: Python

Web Framework: Flask

Database: MySQL + SQLAlchemy

Security Modules: bleach, logging

Testing Tool: Postman

Future Tools: Flask-Mail, JWT, Flask-Admin 등
