# Python 3.9 이미지 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 데이터 디렉토리 생성
RUN mkdir -p data templates static generated_content

# 환경 변수 설정
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8000

# Gunicorn으로 애플리케이션 실행
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "wsgi:app"]