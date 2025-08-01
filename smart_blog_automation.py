#!/usr/bin/env python3
"""
스마트 블로그 자동화 시스템
- 데이터랩 + 쇼핑 API 시너지
- 키워드 선택 인터페이스
- 인기 콘텐츠 분석
"""
import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv
import time

load_dotenv()

class SmartBlogAutomation:
    def __init__(self):
        self.config = {
            'naver_client_id': os.getenv('NAVER_CLIENT_ID'),
            'naver_client_secret': os.getenv('NAVER_CLIENT_SECRET'),
            'openai_api_key': os.getenv('OPENAI_API_KEY')
        }
        
    def collect_trending_keywords(self) -> List[Dict]:
        """데이터랩 + 쇼핑 트렌드 통합 분석"""
        print("\n🔍 스마트 키워드 분석 시작...")
        
        trending_keywords = []
        
        # 1. 네이버 데이터랩 트렌드 (실제 구현 시)
        # self.get_datalab_trends()
        
        # 2. 쇼핑 인사이트 API (실제 구현 시)
        # self.get_shopping_insights()
        
        # 3. 계절별/이벤트별 키워드
        seasonal_keywords = self.get_seasonal_keywords()
        
        # 4. 각 키워드에 대한 시장 분석
        for keyword in seasonal_keywords:
            analysis = self.analyze_keyword_potential(keyword)
            trending_keywords.append(analysis)
            
        return trending_keywords
    
    def get_seasonal_keywords(self) -> List[str]:
        """계절/이벤트 기반 키워드"""
        month = datetime.now().month
        
        seasonal_map = {
            1: ["새해 선물", "다이어트", "헬스용품"],
            2: ["발렌타인 선물", "졸업선물"],
            3: ["봄 패션", "신학기 용품"],
            4: ["봄나들이", "캠핑용품"],
            5: ["어버이날 선물", "가정의달"],
            6: ["여름 준비", "에어컨", "선풍기"],
            7: ["여름휴가", "수영복", "선크림"],
            8: ["무더위", "캠핑", "바캉스"],
            9: ["가을 패션", "개학준비"],
            10: ["할로윈", "가을여행"],
            11: ["수능선물", "겨울준비", "블랙프라이데이"],
            12: ["크리스마스", "연말선물", "새해준비"]
        }
        
        return seasonal_map.get(month, ["인기상품"])
    
    def analyze_keyword_potential(self, keyword: str) -> Dict:
        """키워드별 잠재력 분석"""
        print(f"  📊 '{keyword}' 분석 중...")
        
        # 쇼핑 검색량 체크
        search_volume = self.get_search_volume(keyword)
        
        # 경쟁도 분석
        competition = self.analyze_competition(keyword)
        
        # 수익성 분석
        profitability = self.analyze_profitability(keyword)
        
        return {
            'keyword': keyword,
            'search_volume': search_volume,
            'competition': competition,
            'profitability': profitability,
            'score': (search_volume * 0.4 + profitability * 0.4 - competition * 0.2)
        }
    
    def get_search_volume(self, keyword: str) -> float:
        """검색량 분석 (0-100)"""
        url = "https://openapi.naver.com/v1/search/shop.json"
        headers = {
            "X-Naver-Client-Id": self.config['naver_client_id'],
            "X-Naver-Client-Secret": self.config['naver_client_secret']
        }
        params = {"query": keyword, "display": 1}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                total = response.json().get('total', 0)
                # 정규화 (0-100)
                return min(100, total / 10000)
        except:
            pass
        return 50  # 기본값
    
    def analyze_competition(self, keyword: str) -> float:
        """경쟁도 분석 (0-100, 낮을수록 좋음)"""
        # 실제로는 블로그 검색 API로 경쟁 글 수 확인
        # 여기서는 시뮬레이션
        competition_map = {
            "크리스마스": 80,
            "에어프라이어": 70,
            "캠핑용품": 60,
            "여름휴가": 75
        }
        return competition_map.get(keyword, 50)
    
    def analyze_profitability(self, keyword: str) -> float:
        """수익성 분석 (0-100)"""
        # 평균 상품 가격, 커미션율 등 고려
        # 여기서는 시뮬레이션
        profit_map = {
            "크리스마스 선물": 80,
            "에어프라이어": 90,
            "캠핑용품": 85,
            "다이어트": 70
        }
        return profit_map.get(keyword, 60)
    
    def display_keyword_analysis(self, keywords: List[Dict]):
        """키워드 분석 결과 표시"""
        print("\n" + "="*60)
        print("📊 키워드 분석 결과")
        print("="*60)
        
        # 점수순 정렬
        sorted_keywords = sorted(keywords, key=lambda x: x['score'], reverse=True)
        
        for i, kw in enumerate(sorted_keywords, 1):
            print(f"\n{i}. {kw['keyword']}")
            print(f"   검색량: {'🟢' * int(kw['search_volume']/20)} {kw['search_volume']:.0f}")
            print(f"   경쟁도: {'🔴' * int(kw['competition']/20)} {kw['competition']:.0f}")
            print(f"   수익성: {'💰' * int(kw['profitability']/20)} {kw['profitability']:.0f}")
            print(f"   종합점수: ⭐ {kw['score']:.1f}")
    
    def select_keywords(self, keywords: List[Dict]) -> List[str]:
        """사용자가 키워드 선택"""
        print("\n" + "="*60)
        print("🎯 콘텐츠 작성할 키워드를 선택하세요")
        print("="*60)
        print("번호를 입력하세요 (콤마로 구분, 예: 1,3,5)")
        print("전체 선택: all, 추천 선택: top3")
        
        choice = input("\n선택: ").strip()
        
        if choice.lower() == 'all':
            return [kw['keyword'] for kw in keywords]
        elif choice.lower() == 'top3':
            return [kw['keyword'] for kw in keywords[:3]]
        else:
            try:
                indices = [int(x.strip())-1 for x in choice.split(',')]
                return [keywords[i]['keyword'] for i in indices if 0 <= i < len(keywords)]
            except:
                print("❌ 잘못된 입력입니다. 상위 3개를 선택합니다.")
                return [kw['keyword'] for kw in keywords[:3]]
    
    def analyze_popular_content(self, keyword: str) -> Dict:
        """인기 콘텐츠 분석"""
        print(f"\n📈 '{keyword}' 인기 콘텐츠 분석 중...")
        
        # 블로그 검색 API로 인기글 수집
        url = "https://openapi.naver.com/v1/search/blog.json"
        headers = {
            "X-Naver-Client-Id": self.config['naver_client_id'],
            "X-Naver-Client-Secret": self.config['naver_client_secret']
        }
        params = {
            "query": keyword,
            "display": 10,
            "sort": "sim"  # 정확도순
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                items = response.json().get('items', [])
                
                # 인기 콘텐츠 패턴 분석
                titles = [item['title'] for item in items[:5]]
                common_patterns = self.extract_content_patterns(titles)
                
                return {
                    'keyword': keyword,
                    'popular_titles': titles,
                    'content_patterns': common_patterns,
                    'recommended_style': self.recommend_content_style(common_patterns)
                }
        except Exception as e:
            print(f"❌ 분석 실패: {e}")
            
        return {'keyword': keyword, 'popular_titles': [], 'content_patterns': []}
    
    def extract_content_patterns(self, titles: List[str]) -> List[str]:
        """콘텐츠 패턴 추출"""
        patterns = []
        
        # 자주 사용되는 패턴 확인
        if any("추천" in title for title in titles):
            patterns.append("추천/순위형")
        if any("비교" in title for title in titles):
            patterns.append("비교분석형")
        if any("후기" in title or "리뷰" in title for title in titles):
            patterns.append("체험후기형")
        if any("가이드" in title or "방법" in title for title in titles):
            patterns.append("가이드형")
        if any("TOP" in title or "BEST" in title for title in titles):
            patterns.append("랭킹형")
            
        return patterns
    
    def recommend_content_style(self, patterns: List[str]) -> str:
        """콘텐츠 스타일 추천"""
        if "추천/순위형" in patterns and "랭킹형" in patterns:
            return "TOP 10 스타일의 순위형 콘텐츠"
        elif "비교분석형" in patterns:
            return "장단점 비교 분석 콘텐츠"
        elif "체험후기형" in patterns:
            return "실사용 후기 중심 콘텐츠"
        else:
            return "종합 가이드형 콘텐츠"
    
    def create_content_direction(self, keyword: str, content_analysis: Dict) -> Dict:
        """콘텐츠 방향 설계"""
        print(f"\n📝 '{keyword}' 콘텐츠 방향 설계...")
        
        direction = {
            'keyword': keyword,
            'title_style': f"{keyword} {content_analysis['recommended_style']}",
            'structure': self.design_content_structure(content_analysis),
            'key_points': self.extract_key_points(keyword, content_analysis),
            'target_length': "1500-2000자",
            'tone': "친근하고 전문적인"
        }
        
        return direction
    
    def design_content_structure(self, analysis: Dict) -> List[str]:
        """콘텐츠 구조 설계"""
        style = analysis.get('recommended_style', '')
        
        if "순위형" in style:
            return [
                "도입부 - 왜 이 제품이 필요한가?",
                "선정 기준 설명",
                "TOP 5-10 제품 상세 소개",
                "제품별 장단점 분석",
                "구매 가이드",
                "마무리 및 추천"
            ]
        elif "비교" in style:
            return [
                "도입부 - 선택의 어려움",
                "비교 기준 설정",
                "주요 제품 3-5개 선정",
                "상세 비교표",
                "사용 시나리오별 추천",
                "최종 결론"
            ]
        else:
            return [
                "도입부",
                "제품/서비스 소개",
                "주요 특징",
                "사용 방법",
                "장단점",
                "추천 대상"
            ]
    
    def extract_key_points(self, keyword: str, analysis: Dict) -> List[str]:
        """핵심 포인트 추출"""
        return [
            f"{keyword} 선택 시 가장 중요한 기준",
            "가격대별 추천 제품",
            "실사용자 리뷰 요약",
            "구매 시 주의사항",
            "A/S 및 보증 정보"
        ]
    
    def display_content_direction(self, direction: Dict):
        """콘텐츠 방향 표시"""
        print("\n" + "="*60)
        print(f"📋 [{direction['keyword']}] 콘텐츠 방향")
        print("="*60)
        print(f"제목 스타일: {direction['title_style']}")
        print(f"목표 길이: {direction['target_length']}")
        print(f"톤앤매너: {direction['tone']}")
        print("\n구성:")
        for i, section in enumerate(direction['structure'], 1):
            print(f"  {i}. {section}")
        print("\n핵심 포인트:")
        for point in direction['key_points']:
            print(f"  • {point}")
    
    def run(self):
        """메인 실행 워크플로우"""
        print("\n🚀 스마트 블로그 자동화 시스템 시작")
        print("="*60)
        
        # 1. 트렌드 키워드 수집 및 분석
        trending_keywords = self.collect_trending_keywords()
        self.display_keyword_analysis(trending_keywords)
        
        # 2. 키워드 선택 (사용자 인터랙션)
        selected_keywords = self.select_keywords(trending_keywords)
        print(f"\n✅ 선택된 키워드: {', '.join(selected_keywords)}")
        
        # 3. 각 키워드별 처리
        for keyword in selected_keywords:
            # 인기 콘텐츠 분석
            content_analysis = self.analyze_popular_content(keyword)
            
            # 콘텐츠 방향 설계
            direction = self.create_content_direction(keyword, content_analysis)
            self.display_content_direction(direction)
            
            # 사용자 확인
            proceed = input(f"\n이 방향으로 '{keyword}' 콘텐츠를 생성할까요? (y/n): ")
            if proceed.lower() == 'y':
                print(f"✅ '{keyword}' 콘텐츠 생성을 시작합니다...")
                # 실제 콘텐츠 생성 로직 호출
                self.generate_and_save_content(keyword, direction)
            else:
                print(f"⏭️  '{keyword}' 건너뜁니다.")
            
            time.sleep(1)
        
        print("\n✅ 스마트 블로그 자동화 완료!")
    
    def generate_and_save_content(self, keyword: str, direction: Dict):
        """콘텐츠 생성 및 저장"""
        # 상품 검색
        products = self.search_products(keyword)
        
        # 콘텐츠 생성
        content = self.create_content(keyword, direction, products)
        
        # 파일로 저장
        self.save_content(content, keyword)
    
    def search_products(self, keyword: str) -> List[Dict]:
        """네이버 쇼핑 상품 검색"""
        url = "https://openapi.naver.com/v1/search/shop.json"
        headers = {
            "X-Naver-Client-Id": self.config['naver_client_id'],
            "X-Naver-Client-Secret": self.config['naver_client_secret']
        }
        params = {"query": keyword, "display": 10, "sort": "sim"}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                items = response.json().get('items', [])
                products = []
                for item in items[:5]:
                    products.append({
                        'title': item['title'].replace('<b>', '').replace('</b>', ''),
                        'price': int(item['lprice']),
                        'link': item['link'],
                        'mall': item['mallName']
                    })
                return products
        except:
            pass
        return []
    
    def create_content(self, keyword: str, direction: Dict, products: List[Dict]) -> str:
        """콘텐츠 생성"""
        content = f"# {direction['title_style']}\n\n"
        
        # 구조에 따른 콘텐츠 생성
        for section in direction['structure']:
            if "도입부" in section:
                content += f"## {section}\n\n"
                content += f"{keyword}에 대한 관심이 높아지고 있습니다. "
                content += f"오늘은 {keyword} 관련 최고의 제품들을 소개해드리겠습니다.\n\n"
            
            elif "제품" in section and "소개" in section:
                content += f"## {section}\n\n"
                for i, product in enumerate(products[:5], 1):
                    content += f"### {i}. {product['title']}\n"
                    content += f"- 가격: {product['price']:,}원\n"
                    content += f"- 판매처: {product['mall']}\n"
                    content += f"- [상품 바로가기]({product['link']})\n\n"
            
            elif "주요 특징" in section:
                content += f"## {section}\n\n"
                for point in direction['key_points'][:3]:
                    content += f"- {point}\n"
                content += "\n"
        
        content += f"\n---\n"
        content += f"*이 포스팅은 쿠팡 파트너스 활동의 일환으로, 일정액의 수수료를 제공받을 수 있습니다.*\n"
        
        return content
    
    def save_content(self, content: str, keyword: str):
        """콘텐츠 저장"""
        import os
        os.makedirs("smart_blog_posts", exist_ok=True)
        
        filename = f"smart_blog_posts/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{keyword}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📄 콘텐츠 저장 완료: {filename}")

if __name__ == "__main__":
    automation = SmartBlogAutomation()
    automation.run()