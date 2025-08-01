#!/usr/bin/env python3
"""
Google Sheets 연동 - 키워드 분석 결과 자동 저장
"""
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class GoogleSheetsManager:
    def __init__(self):
        # 서비스 계정 인증
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        self.SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_ID')
        
        if not self.SERVICE_ACCOUNT_FILE or not self.SPREADSHEET_ID:
            raise ValueError("Google Sheets 설정이 필요합니다.")
        
        # 인증 및 서비스 객체 생성
        self.creds = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES
        )
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.sheet = self.service.spreadsheets()
    
    def create_analysis_sheet(self):
        """분석 결과 저장용 시트 생성"""
        sheet_name = f"키워드분석_{datetime.now().strftime('%Y%m%d')}"
        
        # 새 시트 추가
        body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name,
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 20
                        }
                    }
                }
            }]
        }
        
        try:
            self.sheet.batchUpdate(
                spreadsheetId=self.SPREADSHEET_ID,
                body=body
            ).execute()
            print(f"✅ 새 시트 생성: {sheet_name}")
            return sheet_name
        except:
            # 이미 존재하는 경우
            return sheet_name
    
    def save_keyword_analysis(self, analysis_data: list, sheet_name: str = None):
        """키워드 분석 결과 저장"""
        if not sheet_name:
            sheet_name = self.create_analysis_sheet()
        
        # 헤더 행
        headers = [
            ['키워드 분석 결과', '', '', '', '', '', '', ''],
            [f'분석 일시: {datetime.now().strftime("%Y-%m-%d %H:%M")}', '', '', '', '', '', '', ''],
            [''],
            ['키워드', '총 상품수', '평균가격', '7일 포스팅', '24시간 포스팅', 
             '포스팅 빈도', '커뮤니티 관심도', '종합점수', '추천도']
        ]
        
        # 데이터 행
        data_rows = []
        for item in analysis_data:
            row = [
                item.get('keyword', ''),
                item.get('total_products', 0),
                item.get('avg_price', 0),
                item.get('posts_7d', 0),
                item.get('posts_24h', 0),
                item.get('posting_freq', ''),
                item.get('community_interest', ''),
                item.get('total_score', 0),
                self.get_recommendation(item.get('total_score', 0))
            ]
            data_rows.append(row)
        
        # 통계 추가
        data_rows.append([''])
        data_rows.append(['통계 요약', '', '', '', '', '', '', ''])
        data_rows.append([
            '평균 점수:', 
            f"=AVERAGE(H5:H{4+len(analysis_data)})",
            '', '', '', '', '', ''
        ])
        
        # 전체 데이터 결합
        all_data = headers + data_rows
        
        # Google Sheets에 쓰기
        body = {
            'values': all_data
        }
        
        result = self.sheet.values().update(
            spreadsheetId=self.SPREADSHEET_ID,
            range=f'{sheet_name}!A1',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        print(f"✅ {result.get('updatedCells')}개 셀 업데이트 완료")
        
        # 서식 적용
        self.format_sheet(sheet_name, len(analysis_data))
        
        return f"https://docs.google.com/spreadsheets/d/{self.SPREADSHEET_ID}"
    
    def format_sheet(self, sheet_name: str, data_count: int):
        """시트 서식 적용"""
        sheet_id = self.get_sheet_id(sheet_name)
        
        requests = [
            # 헤더 행 굵게
            {
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 3,
                        'endRowIndex': 4
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat.textFormat.bold'
                }
            },
            # 숫자 열 서식
            {
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 4,
                        'endRowIndex': 4 + data_count,
                        'startColumnIndex': 1,
                        'endColumnIndex': 2
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'numberFormat': {
                                'type': 'NUMBER',
                                'pattern': '#,##0'
                            }
                        }
                    },
                    'fields': 'userEnteredFormat.numberFormat'
                }
            }
        ]
        
        body = {'requests': requests}
        self.sheet.batchUpdate(
            spreadsheetId=self.SPREADSHEET_ID,
            body=body
        ).execute()
    
    def get_sheet_id(self, sheet_name: str):
        """시트 ID 가져오기"""
        sheet_metadata = self.sheet.get(
            spreadsheetId=self.SPREADSHEET_ID
        ).execute()
        
        for sheet in sheet_metadata.get('sheets', []):
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']['sheetId']
        return None
    
    def get_recommendation(self, score: float) -> str:
        """점수에 따른 추천도"""
        if score >= 80:
            return "💎 매우 높음"
        elif score >= 60:
            return "✅ 높음"
        elif score >= 40:
            return "⚡ 보통"
        else:
            return "⚠️ 낮음"
    
    def save_content_log(self, keyword: str, content_path: str):
        """생성된 콘텐츠 로그 저장"""
        log_sheet = "콘텐츠_로그"
        
        # 로그 데이터
        log_data = [[
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            keyword,
            content_path,
            "생성 완료"
        ]]
        
        # 추가 모드로 저장
        body = {'values': log_data}
        
        try:
            self.sheet.values().append(
                spreadsheetId=self.SPREADSHEET_ID,
                range=f'{log_sheet}!A:D',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
        except:
            # 시트가 없으면 생성
            self.create_log_sheet()
            self.sheet.values().append(
                spreadsheetId=self.SPREADSHEET_ID,
                range=f'{log_sheet}!A:D',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
    
    def create_log_sheet(self):
        """로그 시트 생성"""
        body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': '콘텐츠_로그'
                    }
                }
            }]
        }
        
        self.sheet.batchUpdate(
            spreadsheetId=self.SPREADSHEET_ID,
            body=body
        ).execute()
        
        # 헤더 추가
        headers = [['생성일시', '키워드', '파일경로', '상태']]
        body = {'values': headers}
        
        self.sheet.values().update(
            spreadsheetId=self.SPREADSHEET_ID,
            range='콘텐츠_로그!A1:D1',
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

def demo_sheets_integration():
    """시트 연동 데모"""
    try:
        manager = GoogleSheetsManager()
        
        # 테스트 데이터
        test_data = [
            {
                'keyword': '캠핑',
                'total_products': 23252007,
                'avg_price': 98947,
                'posts_7d': 100,
                'posts_24h': 100,
                'posting_freq': '매우 높음',
                'community_interest': '매우 높음',
                'total_score': 100
            },
            {
                'keyword': '에어프라이어',
                'total_products': 355767,
                'avg_price': 151552,
                'posts_7d': 100,
                'posts_24h': 85,
                'posting_freq': '매우 높음',
                'community_interest': '매우 높음',
                'total_score': 95
            }
        ]
        
        # 분석 결과 저장
        sheet_url = manager.save_keyword_analysis(test_data)
        print(f"\n📊 분석 결과가 Google Sheets에 저장되었습니다!")
        print(f"🔗 확인하기: {sheet_url}")
        
        # 콘텐츠 로그 저장
        manager.save_content_log('캠핑', '/blog_posts/camping.md')
        print("\n📝 콘텐츠 로그도 저장되었습니다!")
        
    except Exception as e:
        print(f"❌ Google Sheets 연동 실패: {e}")
        print("설정을 확인해주세요:")
        print("1. 서비스 계정 JSON 파일이 있나요?")
        print("2. Google Sheets ID가 .env에 있나요?")
        print("3. 서비스 계정에 시트 편집 권한을 부여했나요?")

if __name__ == "__main__":
    demo_sheets_integration()