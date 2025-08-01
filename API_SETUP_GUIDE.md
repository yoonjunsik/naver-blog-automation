# 네이버 블로그 자동화 API 설정 가이드

## 1. .env 파일 생성
```bash
# .env.example 파일을 복사하여 .env 생성
cp .env.example .env

# 또는 직접 생성
nano .env
```

## 2. .env 파일 내용
```
# 네이버 API 설정
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here

# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here

# Google API 설정 (선택사항)
GOOGLE_SHEETS_ID=your_google_sheets_id_here
```

## 3. API 키 발급 방법

### 네이버 API
1. https://developers.naver.com 접속
2. 애플리케이션 등록
3. 사용 API: 검색, 데이터랩
4. Client ID와 Secret 복사

### OpenAI API
1. https://platform.openai.com 접속
2. API Keys 메뉴에서 생성
3. sk-로 시작하는 키 복사

### Google Sheets API (선택)
1. https://console.cloud.google.com 접속
2. 새 프로젝트 생성
3. API 라이브러리에서 Google Sheets API 활성화
4. 서비스 계정 생성 및 키 다운로드

## 4. 주의사항
- .env 파일은 절대 git에 커밋하지 마세요
- API 키는 안전하게 보관하세요
- OpenAI는 사용량에 따라 과금됩니다