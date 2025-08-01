# 🚀 Render.com 배포 상세 가이드

## 📋 사전 준비

### 1. 계정 생성
- [GitHub](https://github.com) 계정 생성 (이미 있다면 스킵)
- [Render.com](https://render.com) 계정 생성 (GitHub으로 가입 추천)

### 2. API 키 준비
다음 정보를 메모장에 준비하세요:
- `NAVER_CLIENT_ID`: 네이버 개발자센터에서 발급
- `NAVER_CLIENT_SECRET`: 네이버 개발자센터에서 발급
- `OPENAI_API_KEY`: OpenAI에서 발급

## 🔧 배포 과정

### Step 1: GitHub에 코드 업로드

```bash
# 1. 프로젝트 폴더에서 Git 초기화
git init

# 2. 모든 파일 추가
git add .

# 3. 첫 커밋
git commit -m "Initial commit: 네이버 블로그 자동화 시스템"

# 4. GitHub에서 새 저장소 생성
# - https://github.com/new 접속
# - Repository name: naver-blog-automation
# - Public 선택
# - Create repository 클릭

# 5. 원격 저장소 연결 (YOUR_USERNAME을 실제 GitHub 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/naver-blog-automation.git

# 6. 코드 푸시
git branch -M main
git push -u origin main
```

### Step 2: Render.com에서 배포

1. **Render.com 로그인**
   - https://dashboard.render.com 접속

2. **새 웹 서비스 생성**
   - Dashboard에서 `New +` 버튼 클릭
   - `Web Service` 선택

3. **GitHub 저장소 연결**
   - `Connect a repository` 섹션에서 GitHub 계정 연결
   - 방금 만든 `naver-blog-automation` 저장소 선택
   - `Connect` 클릭

4. **서비스 설정**
   ```
   Name: naver-blog-automation (또는 원하는 이름)
   Region: Singapore (아시아 지역 추천)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT wsgi:app
   Instance Type: Free
   ```

5. **환경 변수 설정**
   `Environment Variables` 섹션에서 다음 추가:
   
   | Key | Value |
   |-----|-------|
   | NAVER_CLIENT_ID | your_naver_client_id |
   | NAVER_CLIENT_SECRET | your_naver_client_secret |
   | OPENAI_API_KEY | your_openai_api_key |
   | FLASK_ENV | production |
   | PYTHON_VERSION | 3.9 |

6. **배포 시작**
   - `Create Web Service` 클릭
   - 배포 진행 상황 확인 (약 5-10분 소요)

### Step 3: 배포 확인

1. **서비스 URL 확인**
   - 배포 완료 후 `https://naver-blog-automation.onrender.com` 형태의 URL 제공
   - 클릭하여 접속 확인

2. **관리자 페이지 확인**
   - `https://your-service.onrender.com/admin` 접속
   - 시스템 상태 확인

## ⚠️ 주의사항

### 무료 플랜 제한사항
1. **자동 슬립 모드**
   - 15분간 요청이 없으면 슬립 모드 진입
   - 다음 요청 시 30초 정도 웨이크업 시간 필요

2. **해결 방법**
   - 외부 모니터링 서비스 활용 (예: UptimeRobot)
   - 14분마다 자동 ping 설정

### 스케줄러 관련
- Render 무료 플랜에서도 스케줄러는 작동합니다
- 단, 앱이 슬립 모드일 때는 실행되지 않음
- 중요한 업데이트는 관리자 페이지에서 수동 실행 권장

## 🔍 문제 해결

### 배포 실패 시
1. **로그 확인**
   - Render 대시보드 > Logs 탭
   - 에러 메시지 확인

2. **일반적인 문제**
   - `ModuleNotFoundError`: requirements.txt 확인
   - `Port binding error`: PORT 환경변수 확인
   - API 키 오류: 환경 변수 재확인

### 느린 응답 시간
- 첫 요청 시 30초 정도 소요 (웨이크업)
- 이후 요청은 정상 속도

## 📱 배포 후 사용

1. **메인 페이지**
   ```
   https://your-service.onrender.com
   ```

2. **관리자 페이지**
   ```
   https://your-service.onrender.com/admin
   ```

3. **API 상태 확인**
   ```
   https://your-service.onrender.com/api/admin/status
   ```

## 🎉 축하합니다!

배포가 완료되었습니다. 이제 어디서든 웹 브라우저로 접속하여 사용할 수 있습니다!