#!/bin/bash

echo "🚀 네이버 블로그 자동화 설정 시작!"
echo ""

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# Python3 확인
echo "1️⃣ Python3 버전 확인..."
python3 --version
echo ""

# 가상환경 생성 (선택사항이지만 권장)
echo "2️⃣ 가상환경 생성..."
python3 -m venv venv
source venv/bin/activate
echo "✅ 가상환경 활성화 완료"
echo ""

# 패키지 설치
echo "3️⃣ 필요한 패키지 설치 중..."
pip3 install -r requirements.txt
echo "✅ 패키지 설치 완료"
echo ""

# .env 파일 생성
if [ ! -f .env ]; then
    echo "4️⃣ 환경 설정 파일 생성..."
    cp .env.example .env
    echo "⚠️  .env 파일이 생성되었습니다."
    echo "⚠️  .env 파일을 열어서 API 키를 입력해주세요!"
    echo ""
    echo "설정 방법:"
    echo "1. 다른 터미널에서: nano .env"
    echo "2. API 키 입력 후 저장"
    echo "3. 이 스크립트를 다시 실행"
    exit 1
fi

# 실행
echo "5️⃣ 블로그 자동화 실행!"
python3 blog_automation.py