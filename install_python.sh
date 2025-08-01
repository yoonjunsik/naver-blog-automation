#!/bin/bash

echo "🚀 Python 설치 스크립트 시작!"
echo ""

# 1. Homebrew 설치
if ! command -v brew &> /dev/null; then
    echo "📦 Homebrew 설치 중..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # M1/M2 맥의 경우 PATH 설정
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "✅ Homebrew가 이미 설치되어 있습니다."
fi

# 2. Python 설치
echo ""
echo "🐍 Python 설치 중..."
brew install python@3.11

# 3. 설치 확인
echo ""
echo "✅ 설치 완료!"
echo ""
python3 --version

echo ""
echo "📌 사용 방법:"
echo "   python3 명령어를 사용하세요"
echo "   예: python3 blog_automation.py"