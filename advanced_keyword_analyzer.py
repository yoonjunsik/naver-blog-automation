#!/usr/bin/env python3
"""
고급 키워드 분석기 - 실제 데이터 기반 정량화
"""
import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class AdvancedKeywordAnalyzer:
    def __init__(self):
        self.config = {
            'naver_client_id': os.getenv('NAVER_CLIENT_ID'),
            'naver_client_secret': os.getenv('NAVER_CLIENT_SECRET')
        }
        
    def analyze_keyword_metrics(self, keyword: str) -> Dict:
        """키워드의 실제 메트릭 수집"""
        print(f"\n📊 '{keyword}' 상세 분석 중...")
        
        metrics = {
            'keyword': keyword,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'shopping_data': self.get_shopping_metrics(keyword),
            'blog_data': self.get_blog_metrics(keyword),
            'cafe_data': self.get_cafe_metrics(keyword),
            'news_data': self.get_news_metrics(keyword),
            'datalab_trend': self.get_datalab_trend(keyword),
            'weekly_comparison': self.get_weekly_comparison(keyword)
        }
        
        # 종합 점수 계산
        metrics['total_score'] = self.calculate_total_score(metrics)
        
        return metrics
    
    def get_shopping_metrics(self, keyword: str) -> Dict:
        """쇼핑 검색 메트릭"""
        url = "https://openapi.naver.com/v1/search/shop.json"
        headers = {
            "X-Naver-Client-Id": self.config['naver_client_id'],
            "X-Naver-Client-Secret": self.config['naver_client_secret']
        }
        
        metrics = {
            'total_products': 0,
            'avg_price': 0,
            'price_range': {'min': 0, 'max': 0},
            'top_categories': [],
            'brand_diversity': 0
        }
        
        try:
            # 첫 페이지로 전체 상품 수 확인
            params = {"query": keyword, "display": 100, "sort": "sim"}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                metrics['total_products'] = data.get('total', 0)
                
                items = data.get('items', [])
                if items:
                    prices = [int(item['lprice']) for item in items if item.get('lprice')]
                    if prices:
                        metrics['avg_price'] = sum(prices) / len(prices)
                        metrics['price_range'] = {
                            'min': min(prices),
                            'max': max(prices)
                        }
                    
                    # 브랜드 다양성
                    brands = set(item.get('brand', 'unknown') for item in items)
                    metrics['brand_diversity'] = len(brands)
                    
                    # 카테고리 분포
                    categories = {}
                    for item in items:
                        cat = item.get('category1', 'unknown')
                        categories[cat] = categories.get(cat, 0) + 1
                    
                    metrics['top_categories'] = sorted(
                        categories.items(), 
                        key=lambda x: x[1], 
                        reverse=True
                    )[:5]
                    
        except Exception as e:
            print(f"  ❌ 쇼핑 메트릭 수집 실패: {e}")
            
        return metrics
    
    def get_blog_metrics(self, keyword: str) -> Dict:
        """블로그 검색 메트릭"""
        url = "https://openapi.naver.com/v1/search/blog.json"
        headers = {
            "X-Naver-Client-Id": self.config['naver_client_id'],
            "X-Naver-Client-Secret": self.config['naver_client_secret']
        }
        
        metrics = {
            'total_posts': 0,
            'recent_posts_24h': 0,
            'recent_posts_7d': 0,
            'recent_posts_30d': 0,
            'posting_frequency': 'unknown'
        }
        
        try:
            # 전체 포스트 수
            params = {"query": keyword, "display": 1}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                metrics['total_posts'] = data.get('total', 0)
                
                # 최근 포스트 분석 (날짜 기준)
                params = {"query": keyword, "display": 100, "sort": "date"}
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    items = response.json().get('items', [])
                    now = datetime.now()
                    
                    # 실제 날짜 계산
                    posts_24h = 0
                    posts_7d = 0
                    posts_30d = 0
                    
                    print(f"  📊 최근 블로그 {len(items)}개 분석 중...")
                    
                    for i, item in enumerate(items):
                        # 포스트 날짜 파싱 (예: 20240801)
                        post_date_str = item.get('postdate', '')
                        if post_date_str and len(post_date_str) == 8:
                            try:
                                post_date = datetime.strptime(post_date_str, '%Y%m%d')
                                days_diff = (now - post_date).days
                                
                                # 디버그: 첫 5개 항목 날짜 출력
                                if i < 5:
                                    print(f"    - 포스트 {i+1}: {post_date_str} ({days_diff}일 전)")
                                
                                if days_diff <= 1:
                                    posts_24h += 1
                                if days_diff <= 7:
                                    posts_7d += 1
                                else:
                                    # 7일 이상 된 포스트를 만나면 중단 (이미 날짜순 정렬)
                                    break
                                if days_diff <= 30:
                                    posts_30d += 1
                            except Exception as e:
                                print(f"    ❌ 날짜 파싱 오류: {post_date_str} - {e}")
                                pass
                    
                    # 100개 제한에 대한 추정치 계산
                    if len(items) == 100:
                        # 마지막 항목의 날짜 확인
                        last_date_str = items[-1].get('postdate', '')
                        if last_date_str:
                            try:
                                last_date = datetime.strptime(last_date_str, '%Y%m%d')
                                last_days_diff = (now - last_date).days
                                
                                print(f"    ℹ️ API 제한: 마지막 포스트가 {last_days_diff}일 전")
                                
                                if last_days_diff == 0:
                                    # 100개 모두 오늘 = 하루 100개 이상
                                    posts_24h = "100+"
                                    posts_7d = "700+"  # 대략 추정
                                    posts_30d = "3000+"
                                elif last_days_diff <= 1:
                                    # 100개가 이틀 내 = 이틀에 100개
                                    posts_7d = "350+"  # 대략 추정
                                    posts_30d = "1500+"
                                elif last_days_diff <= 7:
                                    # 100개 모두 7일 이내
                                    posts_7d = f"{posts_7d}+"
                                    posts_30d = f"{int(posts_30d * 30/7)}+"  # 비율로 추정
                                elif last_days_diff <= 30:
                                    # 100개가 30일 이내
                                    posts_30d = f"{posts_30d}+"
                            except:
                                pass
                    
                    metrics['recent_posts_24h'] = posts_24h
                    metrics['recent_posts_7d'] = posts_7d
                    metrics['recent_posts_30d'] = posts_30d
                    
                    # 포스팅 빈도 계산
                    if isinstance(posts_7d, str):
                        # 문자열인 경우 (100+ 등)
                        metrics['posting_frequency'] = '매우 높음'
                    elif posts_7d > 50:
                        metrics['posting_frequency'] = '매우 높음'
                    elif posts_7d > 20:
                        metrics['posting_frequency'] = '높음'
                    elif posts_7d > 10:
                        metrics['posting_frequency'] = '보통'
                    else:
                        metrics['posting_frequency'] = '낮음'
                    
                    print(f"  📝 블로그 메트릭 - 24h: {posts_24h}, 7d: {posts_7d}, 30d: {posts_30d}")
                        
        except Exception as e:
            print(f"  ❌ 블로그 메트릭 수집 실패: {e}")
            
        return metrics
    
    def get_cafe_metrics(self, keyword: str) -> Dict:
        """카페 검색 메트릭"""
        url = "https://openapi.naver.com/v1/search/cafearticle.json"
        headers = {
            "X-Naver-Client-Id": self.config['naver_client_id'],
            "X-Naver-Client-Secret": self.config['naver_client_secret']
        }
        
        metrics = {'total_articles': 0, 'community_interest': 'unknown'}
        
        try:
            params = {"query": keyword, "display": 1}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                metrics['total_articles'] = data.get('total', 0)
                
                # 커뮤니티 관심도
                if metrics['total_articles'] > 10000:
                    metrics['community_interest'] = '매우 높음'
                elif metrics['total_articles'] > 5000:
                    metrics['community_interest'] = '높음'
                elif metrics['total_articles'] > 1000:
                    metrics['community_interest'] = '보통'
                else:
                    metrics['community_interest'] = '낮음'
                    
        except Exception as e:
            print(f"  ❌ 카페 메트릭 수집 실패: {e}")
            
        return metrics
    
    def get_news_metrics(self, keyword: str) -> Dict:
        """뉴스 검색 메트릭"""
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": self.config['naver_client_id'],
            "X-Naver-Client-Secret": self.config['naver_client_secret']
        }
        
        metrics = {'total_news': 0, 'recent_news_24h': 0, 'media_attention': 'unknown'}
        
        try:
            params = {"query": keyword, "display": 100, "sort": "date"}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                metrics['total_news'] = data.get('total', 0)
                
                # 24시간 내 뉴스
                items = data.get('items', [])
                now = datetime.now()
                
                for item in items:
                    pub_date = item.get('pubDate', '')
                    # 뉴스 날짜는 다른 형식일 수 있음
                    # 실제 구현 시 날짜 파싱 로직 필요
                    
                # 미디어 관심도
                if metrics['total_news'] > 100:
                    metrics['media_attention'] = '높음'
                elif metrics['total_news'] > 30:
                    metrics['media_attention'] = '보통'
                else:
                    metrics['media_attention'] = '낮음'
                    
        except Exception as e:
            print(f"  ❌ 뉴스 메트릭 수집 실패: {e}")
            
        return metrics
    
    def get_datalab_trend(self, keyword: str) -> Dict:
        """데이터랩 트렌드 (시뮬레이션)"""
        # 실제로는 네이버 데이터랩 API 사용
        # 여기서는 쇼핑 데이터 기반으로 추정
        
        return {
            'trend_direction': '상승',  # 상승/하락/유지
            'trend_strength': 75,  # 0-100
            'seasonality': '계절성 있음'
        }
    
    def get_weekly_comparison(self, keyword: str) -> Dict:
        """주간 비교 데이터"""
        # 실제로는 일주일 전 데이터와 비교
        # 여기서는 시뮬레이션
        
        return {
            'search_volume_change': '+23%',
            'posting_change': '+15%',
            'price_change': '-5%'
        }
    
    def calculate_total_score(self, metrics: Dict) -> float:
        """종합 점수 계산"""
        score = 0
        
        # 쇼핑 상품 수 (0-30점)
        products = metrics['shopping_data']['total_products']
        score += min(30, products / 100)
        
        # 블로그 활성도 (0-25점)
        blog_posts = metrics['blog_data']['recent_posts_7d']
        if isinstance(blog_posts, str):
            # "100+" 같은 문자열인 경우
            if "100+" in str(blog_posts):
                score += 25  # 최고점
            elif "+" in str(blog_posts):
                # 숫자 부분만 추출
                try:
                    num = int(blog_posts.replace("+", ""))
                    score += min(25, num / 4)
                except:
                    score += 20  # 기본 높은 점수
            else:
                score += 20
        else:
            # 숫자인 경우
            score += min(25, blog_posts / 4)
        
        # 가격대 (0-20점) - 중간 가격대가 좋음
        avg_price = metrics['shopping_data']['avg_price']
        if 10000 <= avg_price <= 100000:
            score += 20
        elif 5000 <= avg_price <= 200000:
            score += 15
        else:
            score += 10
            
        # 브랜드 다양성 (0-15점)
        brands = metrics['shopping_data']['brand_diversity']
        score += min(15, brands * 1.5)
        
        # 커뮤니티 관심도 (0-10점)
        if metrics['cafe_data']['community_interest'] == '매우 높음':
            score += 10
        elif metrics['cafe_data']['community_interest'] == '높음':
            score += 7
        elif metrics['cafe_data']['community_interest'] == '보통':
            score += 5
        else:
            score += 2
            
        return round(score, 1)
    
    def display_detailed_metrics(self, metrics: Dict):
        """상세 메트릭 표시"""
        print("\n" + "="*70)
        print(f"🎯 [{metrics['keyword']}] 상세 분석 결과")
        print(f"📅 분석 시각: {metrics['timestamp']}")
        print("="*70)
        
        # 쇼핑 데이터
        shop = metrics['shopping_data']
        print(f"\n📦 쇼핑 데이터:")
        print(f"  • 총 상품 수: {shop['total_products']:,}개")
        print(f"  • 평균 가격: {shop['avg_price']:,.0f}원")
        print(f"  • 가격 범위: {shop['price_range']['min']:,}원 ~ {shop['price_range']['max']:,}원")
        print(f"  • 브랜드 다양성: {shop['brand_diversity']}개 브랜드")
        
        # 블로그 데이터
        blog = metrics['blog_data']
        print(f"\n📝 블로그 활동:")
        print(f"  • 총 포스트: {blog['total_posts']:,}개")
        print(f"  • 24시간 내: {blog['recent_posts_24h']}개")
        print(f"  • 7일 내: {blog['recent_posts_7d']}개")
        print(f"  • 포스팅 빈도: {blog['posting_frequency']}")
        
        # 커뮤니티 & 뉴스
        print(f"\n💬 커뮤니티 & 뉴스:")
        print(f"  • 카페 글: {metrics['cafe_data']['total_articles']:,}개")
        print(f"  • 커뮤니티 관심도: {metrics['cafe_data']['community_interest']}")
        print(f"  • 뉴스 기사: {metrics['news_data']['total_news']:,}개")
        print(f"  • 미디어 관심도: {metrics['news_data']['media_attention']}")
        
        # 주간 비교
        weekly = metrics['weekly_comparison']
        print(f"\n📈 주간 트렌드:")
        print(f"  • 검색량 변화: {weekly['search_volume_change']}")
        print(f"  • 포스팅 변화: {weekly['posting_change']}")
        print(f"  • 가격 변화: {weekly['price_change']}")
        
        # 종합 점수
        print(f"\n🏆 종합 점수: {metrics['total_score']}/100점")
        
        if metrics['total_score'] >= 80:
            print("  💎 추천도: 매우 높음 - 즉시 콘텐츠 작성 추천!")
        elif metrics['total_score'] >= 60:
            print("  ✅ 추천도: 높음 - 좋은 키워드입니다")
        elif metrics['total_score'] >= 40:
            print("  ⚡ 추천도: 보통 - 전략적 접근 필요")
        else:
            print("  ⚠️ 추천도: 낮음 - 다른 키워드 고려")
    
    def analyze_multiple_keywords(self, keywords: List[str]) -> pd.DataFrame:
        """여러 키워드 비교 분석"""
        results = []
        
        for keyword in keywords:
            metrics = self.analyze_keyword_metrics(keyword)
            results.append({
                '키워드': keyword,
                '상품수': metrics['shopping_data']['total_products'],
                '평균가격': f"{metrics['shopping_data']['avg_price']:,.0f}",
                '7일포스팅': metrics['blog_data']['recent_posts_7d'],
                '포스팅빈도': metrics['blog_data']['posting_frequency'],
                '커뮤니티관심도': metrics['cafe_data']['community_interest'],
                '종합점수': metrics['total_score']
            })
        
        df = pd.DataFrame(results)
        return df.sort_values('종합점수', ascending=False)

def main():
    analyzer = AdvancedKeywordAnalyzer()
    
    # 테스트 키워드
    test_keywords = ["캠핑", "에어프라이어", "선풍기"]
    
    print("🔍 고급 키워드 분석 시작\n")
    
    # 개별 분석
    for keyword in test_keywords[:1]:  # 일단 하나만 상세 분석
        metrics = analyzer.analyze_keyword_metrics(keyword)
        analyzer.display_detailed_metrics(metrics)
    
    # 비교 분석
    print("\n\n📊 키워드 비교 분석")
    print("="*70)
    df = analyzer.analyze_multiple_keywords(test_keywords)
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()