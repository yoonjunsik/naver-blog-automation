#!/usr/bin/env python3
"""
애플리케이션 설정
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 기본 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # API 키
    NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
    NAVER_CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # 데이터베이스 (향후 확장용)
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///blog_automation.db'
    
    # 캐시 설정
    CACHE_DEFAULT_TIMEOUT = 86400  # 24시간
    
    # 스케줄러 설정
    SCHEDULER_API_ENABLED = True
    
class DevelopmentConfig(Config):
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 8890

class ProductionConfig(Config):
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 8000))
    
    # 프로덕션 보안 설정
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

# 환경별 설정 선택
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])