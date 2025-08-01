# 네이버 블로그 자동화 시스템 배포 가이드

## 🚀 배포 옵션

### 1. Railway 배포 (추천 - 가장 간단)

Railway는 GitHub 연동으로 자동 배포가 가능한 플랫폼입니다.

```bash
# 1. Railway CLI 설치
npm install -g @railway/cli

# 2. 프로젝트 초기화
railway login
railway init

# 3. 환경 변수 설정
railway variables set NAVER_CLIENT_ID=your_id
railway variables set NAVER_CLIENT_SECRET=your_secret
railway variables set OPENAI_API_KEY=your_key
railway variables set FLASK_ENV=production

# 4. 배포
railway up
```

### 2. Heroku 배포

```bash
# 1. Heroku CLI 설치 후 로그인
heroku login

# 2. Heroku 앱 생성
heroku create naver-blog-automation

# 3. 환경 변수 설정
heroku config:set NAVER_CLIENT_ID=your_id
heroku config:set NAVER_CLIENT_SECRET=your_secret
heroku config:set OPENAI_API_KEY=your_key
heroku config:set FLASK_ENV=production

# 4. Procfile 생성
echo "web: gunicorn wsgi:app" > Procfile

# 5. 배포
git add .
git commit -m "Heroku deployment"
git push heroku main
```

### 3. Google Cloud Run 배포

```bash
# 1. Google Cloud SDK 설치 및 인증
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Docker 이미지 빌드
docker build -t gcr.io/YOUR_PROJECT_ID/naver-blog-auto .

# 3. 이미지 푸시
docker push gcr.io/YOUR_PROJECT_ID/naver-blog-auto

# 4. Cloud Run에 배포
gcloud run deploy naver-blog-auto \
  --image gcr.io/YOUR_PROJECT_ID/naver-blog-auto \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --set-env-vars FLASK_ENV=production \
  --set-env-vars NAVER_CLIENT_ID=your_id \
  --set-env-vars NAVER_CLIENT_SECRET=your_secret \
  --set-env-vars OPENAI_API_KEY=your_key
```

### 4. AWS EC2 배포

```bash
# 1. EC2 인스턴스 생성 (Ubuntu 22.04 LTS)

# 2. SSH 접속 후 설정
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. 필요한 패키지 설치
sudo apt update
sudo apt install -y python3-pip python3-venv git nginx

# 4. 프로젝트 클론
git clone https://github.com/yourusername/naver-blog-automation.git
cd naver-blog-automation

# 5. 가상환경 생성 및 패키지 설치
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. 환경 변수 설정
cat > .env << EOF
NAVER_CLIENT_ID=your_id
NAVER_CLIENT_SECRET=your_secret
OPENAI_API_KEY=your_key
FLASK_ENV=production
EOF

# 7. Systemd 서비스 생성
sudo nano /etc/systemd/system/blog-automation.service
```

서비스 파일 내용:
```ini
[Unit]
Description=Naver Blog Automation
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/naver-blog-automation
Environment="PATH=/home/ubuntu/naver-blog-automation/venv/bin"
ExecStart=/home/ubuntu/naver-blog-automation/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:app

[Install]
WantedBy=multi-user.target
```

```bash
# 8. 서비스 시작
sudo systemctl start blog-automation
sudo systemctl enable blog-automation

# 9. Nginx 설정
sudo nano /etc/nginx/sites-available/blog-automation
```

Nginx 설정:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# 10. Nginx 활성화
sudo ln -s /etc/nginx/sites-available/blog-automation /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

### 5. Docker 로컬 테스트

```bash
# Docker Compose로 로컬 테스트
docker-compose up --build

# 브라우저에서 http://localhost:8000 접속
```

## 📝 배포 전 체크리스트

- [ ] `.env` 파일에 모든 API 키 설정
- [ ] `FLASK_ENV=production` 설정
- [ ] 방화벽에서 필요한 포트 열기
- [ ] HTTPS 설정 (Let's Encrypt 추천)
- [ ] 도메인 연결 (선택사항)

## 🔐 보안 주의사항

1. **API 키 보호**: 절대로 API 키를 코드에 하드코딩하지 마세요
2. **HTTPS 사용**: 프로덕션 환경에서는 반드시 HTTPS를 사용하세요
3. **접근 제한**: 관리자 페이지(`/admin`)에 인증 추가 고려
4. **정기 업데이트**: 의존성 패키지를 정기적으로 업데이트하세요

## 📊 모니터링

배포 후 다음 엔드포인트로 상태 확인:
- 메인 페이지: `https://your-domain.com/`
- 관리자 페이지: `https://your-domain.com/admin`
- API 상태: `https://your-domain.com/api/admin/status`

## 🆘 문제 해결

### 포트 충돌
```bash
# 사용 중인 포트 확인
sudo lsof -i :8000
# 프로세스 종료
sudo kill -9 [PID]
```

### 메모리 부족
- 서버 스펙 업그레이드
- Worker 수 감소 (`--workers 2`)

### API 제한
- 네이버 API 일일 제한 확인
- 캐시 시간 늘리기