# 🚀 네이버 블로그 자동화 시작 가이드

## 📋 시작 전 체크리스트
- [ ] Python3 설치 확인
- [ ] 네이버 개발자 계정
- [ ] OpenAI 계정
- [ ] 터미널 사용법 기본 이해

## 🎯 빠른 시작 (5분)

### 1단계: 터미널 열기
- 맥: Spotlight(🔍) → "Terminal" 입력
- 윈도우: 시작 → "CMD" 입력

### 2단계: 프로젝트 폴더로 이동
```bash
cd /Users/junsikyoon/naverblog1
```

### 3단계: 테스트 실행
```bash
python3 simple_run.py
```

## 💪 본격 설정 (15분)

### 1단계: Python3 확인
```bash
python3 --version
# 결과: Python 3.x.x 가 나와야 함
```

### 2단계: 패키지 설치
```bash
# pip3 업그레이드 (선택사항)
python3 -m pip install --upgrade pip

# 필요한 패키지 설치
pip3 install -r requirements.txt
```

### 3단계: API 키 설정
```bash
# 설정 파일 복사
cp .env.example .env

# 텍스트 에디터로 열기 (택 1)
nano .env          # 터미널에서 편집
open -e .env       # 텍스트 편집기로 열기
code .env          # VS Code로 열기
```

### 4단계: API 키 입력
`.env` 파일에 다음 정보 입력:
```
NAVER_CLIENT_ID=네이버에서_발급받은_ID
NAVER_CLIENT_SECRET=네이버에서_발급받은_SECRET
OPENAI_API_KEY=sk-로_시작하는_OpenAI_키
```

### 5단계: 실행!
```bash
python3 blog_automation.py
```

## 🔧 문제 해결

### "pip3: command not found" 오류
```bash
python3 -m pip install -r requirements.txt
```

### "ModuleNotFoundError" 오류
```bash
pip3 install [모듈이름]
# 예: pip3 install requests
```

### 권한 오류
```bash
pip3 install --user -r requirements.txt
```

## 🎮 일일 사용법

### 수동 실행
```bash
cd /Users/junsikyoon/naverblog1
python3 blog_automation.py
```

### 자동 실행 설정 (고급)
```bash
# crontab 편집
crontab -e

# 매일 오전 8시 실행 추가
0 8 * * * cd /Users/junsikyoon/naverblog1 && /usr/bin/python3 blog_automation.py
```

## 📞 도움말
- API 키 발급: [네이버 개발자 센터](https://developers.naver.com)
- OpenAI 키: [OpenAI Platform](https://platform.openai.com)
- 문제 발생시: GitHub Issues에 문의