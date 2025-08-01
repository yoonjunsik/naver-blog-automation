# 🚀 네이버 블로그 자동화 시스템

네이버 API와 AI를 활용한 블로그 콘텐츠 자동 생성 및 관리 시스템입니다.

## ✨ 주요 기능

- 📊 **트렌드 키워드 자동 추천** (주 1회 자동 업데이트)
- 🔥 **인기 키워드 실시간 추적** (매일 새벽 자동 수집)
- 🎯 **키워드 세분화 및 검색량 분석**
- 🛍️ **상품 검색 및 추천**
- 📝 **AI 기반 콘텐츠 자동 생성**
- 💾 **24시간 자동 캐시 관리**
- 🔧 **관리자 대시보드**

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/yourusername/naverblog-automation.git
cd naverblog-automation

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 입력
```

### 2. 로컬 실행

```bash
# 개발 모드 실행
./start.sh

# 프로덕션 모드 실행
./start.sh production
```

### 3. Docker로 실행

```bash
# Docker Compose 사용
docker-compose up -d

# 브라우저에서 http://localhost:8000 접속
```

## 📋 필수 API 키

1. **네이버 API**
   - [네이버 개발자 센터](https://developers.naver.com)에서 발급
   - 검색, 쇼핑, 블로그 API 사용

2. **OpenAI API**
   - [OpenAI Platform](https://platform.openai.com)에서 발급
   - 콘텐츠 생성용

## 🌐 배포 옵션

### Railway (추천 - 가장 간단)
```bash
railway login
railway init
railway up
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

### Docker
```bash
docker build -t naver-blog-auto .
docker run -p 8000:8000 --env-file .env naver-blog-auto
```

자세한 배포 가이드는 [DEPLOYMENT.md](DEPLOYMENT.md) 참고

## 📱 사용 방법

1. **메인 페이지** (`/`)
   - 트렌드 키워드 선택
   - 세부 키워드 분석
   - 상품 검색 및 콘텐츠 생성

2. **관리자 페이지** (`/admin`)
   - 시스템 상태 모니터링
   - 수동 업데이트 실행
   - 캐시 관리

## 📅 자동 업데이트 스케줄

- **트렌드 키워드**: 매주 월요일 새벽 3시
- **인기 키워드**: 매일 새벽 4시
- **캐시 정리**: 매시간 (24시간 경과 데이터 삭제)

## 🛠️ 기술 스택

- **Backend**: Python 3.9, Flask
- **APIs**: Naver Open API, OpenAI API
- **Scheduler**: Python Schedule
- **Deployment**: Docker, Gunicorn
- **Cache**: In-memory with TTL

## 📁 프로젝트 구조

```
naverblog-automation/
├── web_app.py           # 메인 Flask 애플리케이션
├── auto_updater.py      # 자동 업데이트 시스템
├── keyword_refiner.py   # 키워드 세분화 로직
├── templates/           # HTML 템플릿
│   ├── index.html      # 메인 페이지
│   └── admin.html      # 관리자 페이지
├── data/               # 자동 생성 데이터
├── requirements.txt    # Python 패키지
└── Dockerfile         # Docker 설정
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 있습니다.

## 🆘 문제 해결

문제가 발생하면 [Issues](https://github.com/yourusername/naverblog-automation/issues)에 등록해주세요.
EOF < /dev/null