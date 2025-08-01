#!/usr/bin/env python3
"""
자동 업데이트 시스템
- 트렌드 키워드: 주 1회 자동 업데이트
- 캐시 데이터: 24시간 후 자동 만료
- 인기 키워드: 매일 새벽 자동 수집
"""
import os
import json
import requests
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv
import logging

load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoUpdater:
    def __init__(self):
        self.headers = {
            "X-Naver-Client-Id": os.getenv('NAVER_CLIENT_ID'),
            "X-Naver-Client-Secret": os.getenv('NAVER_CLIENT_SECRET')
        }
        self.trend_keywords_file = 'data/trend_keywords.json'
        self.popular_keywords_file = 'data/popular_keywords.json'
        self.cache_file = 'data/cache_data.json'
        
        # 데이터 디렉토리 생성
        os.makedirs('data', exist_ok=True)
        
        # 초기 데이터 로드
        self.load_data()
    
    def load_data(self):
        """저장된 데이터 로드"""
        # 트렌드 키워드
        if os.path.exists(self.trend_keywords_file):
            with open(self.trend_keywords_file, 'r', encoding='utf-8') as f:
                self.trend_keywords = json.load(f)
        else:
            self.trend_keywords = self.get_default_keywords()
            
        # 인기 키워드
        if os.path.exists(self.popular_keywords_file):
            with open(self.popular_keywords_file, 'r', encoding='utf-8') as f:
                self.popular_keywords = json.load(f)
        else:
            self.popular_keywords = {}
            
        # 캐시 데이터
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.cache_data = json.load(f)
            self.clean_expired_cache()
        else:
            self.cache_data = {}
    
    def get_default_keywords(self) -> Dict:
        """기본 키워드 세트"""
        return {
            '여름시즌': [
                '에어컨', '선풍기', '서큘레이터', '제습기', '캠핑',
                '수영복', '래쉬가드', '아쿠아슈즈', '선크림', '모기퇴치'
            ],
            '전자제품': [
                '에어프라이어', '전기밥솥', '믹서기', '커피머신', '로봇청소기',
                '공기청정기', '무선이어폰', '스마트워치', '노트북', '태블릿'
            ],
            '생활용품': [
                '매트리스', '이불', '베개', '수건', '칫솔',
                '샴푸', '바디워시', '세제', '주방세제', '화장지'
            ],
            '패션': [
                '운동화', '샌들', '백팩', '크로스백', '지갑',
                '반팔티', '반바지', '원피스', '모자', '선글라스'
            ],
            '식품': [
                '비타민', '유산균', '다이어트보조제', '단백질보충제', '콜라겐',
                '커피', '차', '과자', '라면', '즉석식품'
            ],
            '선물': [
                '생일선물', '답례품', '출산선물', '집들이선물', '명절선물',
                '기념일선물', '졸업선물', '승진선물', '화장품세트', '와인선물세트'
            ],
            '여행': [
                '캐리어', '여행가방', '여권케이스', '목베개', '여행용파우치',
                '셀카봉', '보조배터리', '유니버셜어댑터', '압축팩', '여행용세면도구'
            ],
            '뷰티': [
                '스킨케어', '메이크업', '향수', '바디로션', '클렌징폼',
                '마스크팩', '선크림', '립스틱', '쿠션', '아이크림'
            ],
            '육아': [
                '기저귀', '분유', '젖병', '유모차', '아기띠',
                '카시트', '아기침대', '이유식', '장난감', '아기옷'
            ],
            '운동': [
                '요가매트', '덤벨', '런닝화', '헬스장갑', '보충제',
                '스포츠웨어', '실내자전거', '폼롤러', '밴드', '짐볼'
            ]
        }
    
    def update_trend_keywords(self):
        """트렌드 키워드 업데이트 (주 1회)"""
        logger.info("트렌드 키워드 업데이트 시작")
        
        try:
            # 네이버 쇼핑 인사이트 API 사용 (실제로는 별도 신청 필요)
            # 여기서는 시뮬레이션으로 구현
            new_trends = self.collect_shopping_trends()
            
            # 계절별 키워드 자동 조정
            current_month = datetime.now().month
            if 3 <= current_month <= 5:  # 봄
                seasonal_keywords = ['봄옷', '미세먼지마스크', '화분', '캠핑용품']
            elif 6 <= current_month <= 8:  # 여름
                seasonal_keywords = ['에어컨', '선풍기', '수영복', '선크림']
            elif 9 <= current_month <= 11:  # 가을
                seasonal_keywords = ['가디건', '부츠', '전기장판', '가습기']
            else:  # 겨울
                seasonal_keywords = ['패딩', '전기히터', '핫팩', '목도리']
            
            # 기존 키워드와 병합
            self.trend_keywords['시즌추천'] = seasonal_keywords[:10]
            
            # 파일 저장
            with open(self.trend_keywords_file, 'w', encoding='utf-8') as f:
                json.dump(self.trend_keywords, f, ensure_ascii=False, indent=2)
            
            logger.info(f"트렌드 키워드 업데이트 완료: {len(self.trend_keywords)}개 카테고리")
            
        except Exception as e:
            logger.error(f"트렌드 키워드 업데이트 실패: {e}")
    
    def collect_shopping_trends(self) -> List[str]:
        """쇼핑 트렌드 수집"""
        trends = []
        
        # 인기 검색어 수집 (네이버 쇼핑 API)
        categories = ['50000000', '50000001', '50000002']  # 패션, 뷰티, 생활
        
        for cat_id in categories:
            try:
                url = "https://openapi.naver.com/v1/search/shop.json"
                params = {
                    "query": " ",  # 전체 검색
                    "display": 100,
                    "sort": "date",
                    "filter": f"category:{cat_id}"
                }
                
                response = requests.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    items = response.json().get('items', [])
                    # 카테고리별 상위 키워드 추출
                    keywords = {}
                    for item in items:
                        title_words = item['title'].split()
                        for word in title_words:
                            if len(word) > 1:
                                keywords[word] = keywords.get(word, 0) + 1
                    
                    # 상위 5개 키워드
                    top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]
                    trends.extend([kw[0] for kw in top_keywords])
                    
            except Exception as e:
                logger.error(f"카테고리 {cat_id} 트렌드 수집 실패: {e}")
        
        return trends
    
    def update_popular_keywords(self):
        """인기 키워드 업데이트 (매일 새벽)"""
        logger.info("인기 키워드 업데이트 시작")
        
        try:
            popular = {}
            
            # 모든 카테고리의 키워드 검색량 확인
            all_keywords = []
            for category, keywords in self.trend_keywords.items():
                all_keywords.extend(keywords)
            
            for keyword in all_keywords[:50]:  # API 제한으로 상위 50개만
                try:
                    # 블로그 검색량 확인
                    url = "https://openapi.naver.com/v1/search/blog.json"
                    params = {
                        "query": keyword,
                        "display": 1,
                        "sort": "date"
                    }
                    
                    response = requests.get(url, headers=self.headers, params=params)
                    if response.status_code == 200:
                        total = response.json().get('total', 0)
                        
                        # 최근 포스팅 수 확인
                        params['display'] = 100
                        response = requests.get(url, headers=self.headers, params=params)
                        if response.status_code == 200:
                            items = response.json().get('items', [])
                            recent_count = len([i for i in items if self.is_recent_post(i)])
                            
                            popular[keyword] = {
                                'total_posts': total,
                                'recent_7days': recent_count,
                                'score': total * 0.3 + recent_count * 100,
                                'last_updated': datetime.now().isoformat()
                            }
                    
                    time.sleep(0.1)  # API 제한 방지
                    
                except Exception as e:
                    logger.error(f"키워드 '{keyword}' 분석 실패: {e}")
            
            # 점수 기준 상위 30개 저장
            sorted_popular = dict(sorted(popular.items(), 
                                       key=lambda x: x[1]['score'], 
                                       reverse=True)[:30])
            
            self.popular_keywords = {
                'keywords': sorted_popular,
                'updated_at': datetime.now().isoformat()
            }
            
            # 파일 저장
            with open(self.popular_keywords_file, 'w', encoding='utf-8') as f:
                json.dump(self.popular_keywords, f, ensure_ascii=False, indent=2)
            
            logger.info(f"인기 키워드 업데이트 완료: {len(sorted_popular)}개")
            
        except Exception as e:
            logger.error(f"인기 키워드 업데이트 실패: {e}")
    
    def is_recent_post(self, post: Dict) -> bool:
        """최근 7일 이내 포스트인지 확인"""
        try:
            post_date = post.get('postdate', '')
            if post_date and len(post_date) == 8:
                post_datetime = datetime.strptime(post_date, '%Y%m%d')
                days_diff = (datetime.now() - post_datetime).days
                return days_diff <= 7
        except:
            pass
        return False
    
    def clean_expired_cache(self):
        """만료된 캐시 정리 (24시간)"""
        logger.info("캐시 정리 시작")
        
        now = datetime.now()
        expired_keys = []
        
        for key, value in self.cache_data.items():
            if 'timestamp' in value:
                cache_time = datetime.fromisoformat(value['timestamp'])
                if (now - cache_time) > timedelta(hours=24):
                    expired_keys.append(key)
        
        # 만료된 캐시 삭제
        for key in expired_keys:
            del self.cache_data[key]
        
        if expired_keys:
            # 파일 저장
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"캐시 정리 완료: {len(expired_keys)}개 항목 삭제")
    
    def add_to_cache(self, key: str, data: Dict):
        """캐시에 데이터 추가"""
        self.cache_data[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        # 파일 저장
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
    
    def get_from_cache(self, key: str) -> Dict:
        """캐시에서 데이터 가져오기"""
        if key in self.cache_data:
            cache_entry = self.cache_data[key]
            # 24시간 이내인지 확인
            cache_time = datetime.fromisoformat(cache_entry['timestamp'])
            if (datetime.now() - cache_time) < timedelta(hours=24):
                return cache_entry['data']
        return None
    
    def start_scheduler(self):
        """스케줄러 시작"""
        # 주 1회 트렌드 업데이트 (매주 월요일 새벽 3시)
        schedule.every().monday.at("03:00").do(self.update_trend_keywords)
        
        # 매일 새벽 인기 키워드 업데이트 (매일 새벽 4시)
        schedule.every().day.at("04:00").do(self.update_popular_keywords)
        
        # 매시간 캐시 정리
        schedule.every().hour.do(self.clean_expired_cache)
        
        # 스케줄러 실행
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
        
        # 백그라운드 스레드로 실행
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("자동 업데이트 스케줄러 시작")
    
    def force_update_all(self):
        """모든 데이터 강제 업데이트"""
        logger.info("전체 데이터 강제 업데이트 시작")
        self.update_trend_keywords()
        self.update_popular_keywords()
        self.clean_expired_cache()
        logger.info("전체 데이터 강제 업데이트 완료")

# 싱글톤 인스턴스
updater = AutoUpdater()

if __name__ == "__main__":
    # 테스트 실행
    print("자동 업데이트 시스템 테스트")
    updater.force_update_all()
    print("완료!")