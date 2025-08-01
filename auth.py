#!/usr/bin/env python3
"""
간단한 인증 시스템
"""
import os
from functools import wraps
from flask import request, Response, session, redirect, url_for, render_template_string
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

load_dotenv()

# 환경 변수에서 관리자 비밀번호 가져오기
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')  # 기본값은 변경하세요!

def check_auth(password):
    """비밀번호 확인"""
    # 실제로는 해시된 비밀번호와 비교해야 함
    return password == ADMIN_PASSWORD

def authenticate():
    """인증 요청 응답"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>관리자 로그인</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #f5f5f5;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .login-box {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 400px;
            }
            h2 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                color: #666;
                font-size: 14px;
            }
            input[type="password"] {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            input[type="password"]:focus {
                outline: none;
                border-color: #03c75a;
            }
            button {
                width: 100%;
                padding: 12px;
                background-color: #03c75a;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #02a048;
            }
            .error {
                color: #dc3545;
                font-size: 14px;
                margin-top: 10px;
                text-align: center;
            }
            .logo {
                text-align: center;
                font-size: 40px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="login-box">
            <div class="logo">🔐</div>
            <h2>관리자 로그인</h2>
            <form method="post" action="/admin/login">
                <div class="form-group">
                    <label for="password">비밀번호</label>
                    <input type="password" id="password" name="password" required autofocus>
                </div>
                <button type="submit">로그인</button>
            </form>
            ''' + ('''<p class="error">비밀번호가 올바르지 않습니다.</p>''' if request.method == 'POST' else '') + '''
        </div>
    </body>
    </html>
    '''
    return Response(html, mimetype='text/html')

def requires_auth(f):
    """인증이 필요한 뷰 데코레이터"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 세션에 인증 정보가 있는지 확인
        if not session.get('authenticated'):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def login_page():
    """로그인 페이지"""
    return authenticate()

def handle_login():
    """로그인 처리"""
    password = request.form.get('password')
    if check_auth(password):
        session['authenticated'] = True
        session.permanent = True  # 세션 유지
        return redirect(url_for('admin'))
    else:
        return authenticate()

def logout():
    """로그아웃"""
    session.pop('authenticated', None)
    return redirect(url_for('index'))