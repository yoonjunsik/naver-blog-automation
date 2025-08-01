#!/usr/bin/env python3
"""
WSGI 엔트리 포인트 - 프로덕션 배포용
"""
from web_app import app

if __name__ == "__main__":
    app.run()