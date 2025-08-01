#!/bin/bash

# 네이버 블로그 자동화 시스템 시작 스크립트

echo "🚀 네이버 블로그 자동화 시스템 시작"

# 환경 확인
if [ ! -f .env ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사하여 설정해주세요."
    exit 1
fi

# 가상환경 확인 및 활성화
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv venv
fi

source venv/bin/activate

# 패키지 설치
echo "📦 필요한 패키지 설치 중..."
pip install -r requirements.txt

# 데이터 디렉토리 생성
mkdir -p data generated_content

# 환경 변수 확인
source .env

if [ -z "$NAVER_CLIENT_ID" ] || [ -z "$NAVER_CLIENT_SECRET" ]; then
    echo "❌ 네이버 API 키가 설정되지 않았습니다."
    exit 1
fi

# 개발/프로덕션 모드 선택
if [ "$1" == "production" ]; then
    echo "🌐 프로덕션 모드로 시작합니다..."
    export FLASK_ENV=production
    gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 wsgi:app
else
    echo "🔧 개발 모드로 시작합니다..."
    export FLASK_ENV=development
    python3 web_app.py
fi