#!/usr/bin/env python3
"""
키워드 세분화 및 연관 키워드 분석
"""
import os
import requests
from typing import List, Dict
from dotenv import load_dotenv
import json

load_dotenv()

class KeywordRefiner:
    def __init__(self):
        self.headers = {
            "X-Naver-Client-Id": os.getenv('NAVER_CLIENT_ID'),
            "X-Naver-Client-Secret": os.getenv('NAVER_CLIENT_SECRET')
        }
        
        # 카테고리별 세부 키워드 매핑
        self.keyword_mappings = {
            '선풍기': {
                'categories': ['스탠드선풍기', '탁상용선풍기', '휴대용선풍기', '목걸이선풍기', 
                             '리모컨선풍기', '타워팬', '서큘레이터', '무선선풍기', 'USB선풍기'],
                'brands': ['다이슨', '신일', '한일', '샤오미', '보네이도'],
                'features': ['저소음', '무소음', 'BLDC', '리모컨', '타이머', '에너지효율']
            },
            '에어컨': {
                'categories': ['벽걸이에어컨', '스탠드에어컨', '창문형에어컨', '이동식에어컨', 
                             '시스템에어컨', '천장형에어컨'],
                'brands': ['삼성', 'LG', '캐리어', '위니아'],
                'features': ['인버터', '절전형', '공기청정', '제습기능', '스마트']
            },
            '캠핑': {
                'categories': ['캠핑텐트', '캠핑의자', '캠핑테이블', '캠핑랜턴', '캠핑매트',
                             '캠핑화로', '캠핑식기', '캠핑침낭', '캠핑타프', '캠핑용품세트'],
                'brands': ['코베아', '콜맨', '스노우피크', '헬리녹스', '제드'],
                'features': ['경량', '방수', '4계절용', '패밀리용', '백패킹용']
            },
            '수영복': {
                'categories': ['여성수영복', '남성수영복', '아동수영복', '비키니', '래쉬가드',
                             '원피스수영복', '실내수영복', '비치웨어'],
                'brands': ['아레나', '스피도', '후그', '르까프', '배럴'],
                'features': ['클로린저항', '속건성', 'UV차단', '체형보정']
            },
            '래쉬가드': {
                'categories': ['여성래쉬가드', '남성래쉬가드', '아동래쉬가드', '반팔래쉬가드',
                             '긴팔래쉬가드', '래쉬가드세트', '집업래쉬가드', '후드래쉬가드'],
                'brands': ['배럴', '후그', '르까프', '아레나', '스피도'],
                'features': ['UV차단', '속건성', '신축성', '체온유지']
            },
            '아쿠아슈즈': {
                'categories': ['성인아쿠아슈즈', '아동아쿠아슈즈', '다이빙슈즈', '워터슈즈',
                             '비치슈즈', '수영장슈즈', '아쿠아삭스'],
                'brands': ['아디다스', '나이키', '아레나', '스피도', '리복'],
                'features': ['미끄럼방지', '속건성', '가벼움', '발가락보호']
            },
            '선크림': {
                'categories': ['얼굴용선크림', '바디선크림', '스틱선크림', '쿠션선크림',
                             '무기자차선크림', '유기자차선크림', '워터프루프선크림', '어린이선크림'],
                'brands': ['아이오페', '헤라', '미샤', '이니스프리', '닥터지'],
                'features': ['SPF50+', 'PA+++', '워터프루프', '민감성피부', '톤업']
            },
            '세제': {
                'categories': ['액체세제', '가루세제', '캡슐세제', '아기세제', '울세제',
                             '표백제', '섬유유연제', '세탁비누', '얼룩제거제'],
                'brands': ['퍼실', '다우니', '리큐', '피죤', '테크'],
                'features': ['고농축', '저자극', '친환경', '향균', '표백']
            },
            '샴푸': {
                'categories': ['탈모샴푸', '비듬샴푸', '두피샴푸', '손상모발샴푸', '지성샴푸',
                             '건성샴푸', '어린이샴푸', '약산성샴푸', '천연샴푸'],
                'brands': ['려', '미쟝센', '헤드앤숄더', '팬틴', '케라시스'],
                'features': ['실리콘프리', '약산성', '탈모완화', '두피개선', '손상모발케어']
            },
            '칫솔': {
                'categories': ['일반칫솔', '전동칫솔', '미세모칫솔', '어린이칫솔', '교정용칫솔',
                             '휴대용칫솔', '음파칫솔', '실리콘칫솔'],
                'brands': ['오랄비', '필립스', '브라운', '페리오', '죽염'],
                'features': ['미세모', '잇몸케어', '플라그제거', '휴대용', '충전식']
            },
            '과자': {
                'categories': ['스낵과자', '초콜릿', '사탕', '젤리', '쿠키', '비스킷', 
                             '포테이토칩', '새우깡', '양파링', '초코파이'],
                'brands': ['오리온', '롯데', '농심', '크라운', '해태'],
                'features': ['무방부제', '저칼로리', '수입과자', '어린이간식', '프리미엄']
            },
            '라면': {
                'categories': ['봉지라면', '컵라면', '볶음면', '짜장라면', '비빔면',
                             '매운라면', '건면', '생라면', '수입라면'],
                'brands': ['농심', '오뚝이', '삼양', '팔도', '풀무원'],
                'features': ['저나트륨', '건면', '프리미엄', '매운맛', '순한맛']
            },
            '커피': {
                'categories': ['원두커피', '인스턴트커피', '커피믹스', '캡슐커피', '콜드브루',
                             '더치커피', '디카페인', '아이스커피', '스틱커피'],
                'brands': ['맥심', '카누', '네스프레소', '스타벅스', '이디야'],
                'features': ['아라비카', '로부스타', '디카페인', '프리미엄', '저칼로리']
            },
            '차': {
                'categories': ['녹차', '홍차', '보이차', '허브차', '과일차', '곡물차',
                             '티백', '잎차', '가루차'],
                'brands': ['오설록', '동서', '립톤', '트와이닝', '아모레'],
                'features': ['유기농', '무카페인', '프리미엄', '수입차', '건강차']
            },
            '비타민': {
                'categories': ['종합비타민', '비타민C', '비타민D', '비타민B', '오메가3',
                             '멀티비타민', '어린이비타민', '임산부비타민'],
                'brands': ['센트룸', '뉴트리라이트', 'GNC', '솔가', '네이처메이드'],
                'features': ['천연원료', '고함량', '흡수율', '무첨가', '유기농']
            },
            '생일선물': {
                'categories': ['여자친구선물', '남자친구선물', '부모님선물', '아이선물',
                             '친구선물', '20대선물', '30대선물', '40대선물'],
                'brands': ['샤넬', '디올', '조말론', '애플', '나이키'],
                'features': ['프리미엄', '한정판', '각인서비스', '선물포장', '당일배송']
            },
            '캐리어': {
                'categories': ['기내용캐리어', '화물용캐리어', '하드캐리어', '소프트캐리어',
                             '알루미늄캐리어', '폴리카보네이트캐리어', '백팩캐리어'],
                'brands': ['쌤소나이트', '아메리칸투어리스터', '델시', '리모와', '트래블메이트'],
                'features': ['경량', 'TSA락', '확장형', '360도회전', '충격방지']
            }
        }
    
    def get_related_keywords(self, main_keyword: str) -> Dict:
        """연관 키워드 및 세분화된 카테고리 반환"""
        
        # 1. 자동완성 API로 연관 키워드 수집
        related = self.get_autocomplete_keywords(main_keyword)
        
        # 2. 미리 정의된 카테고리 확인
        predefined = self.keyword_mappings.get(main_keyword, {})
        
        # 3. 쇼핑 카테고리 분석
        shopping_categories = self.analyze_shopping_categories(main_keyword)
        
        # 4. 미리 정의된 카테고리가 없으면 쇼핑 카테고리에서 생성
        if not predefined.get('categories') and shopping_categories:
            # 쇼핑 카테고리에서 키워드 추출
            generated_categories = []
            for cat in shopping_categories[:10]:
                # 카테고리명을 키워드로 변환
                cat_name = cat['name'].split('>')[-1].strip()
                if cat_name and cat_name != main_keyword:
                    generated_categories.append(f"{main_keyword} {cat_name}")
            
            if generated_categories:
                predefined['categories'] = generated_categories
        
        # 5. 각 세부 키워드의 검색량 확인
        refined_keywords = []
        
        # 최대 검색량 추적
        max_volume = 0
        all_keywords_data = []
        
        # 카테고리별 키워드
        if predefined.get('categories'):
            for category in predefined['categories'][:10]:
                metrics = self.get_search_volume(category)
                keyword_data = {
                    'keyword': category,
                    'type': '카테고리',
                    'metrics': metrics,
                    'parent': main_keyword
                }
                all_keywords_data.append(keyword_data)
                max_volume = max(max_volume, metrics['actual_volume'])
        
        # 자동완성 키워드 추가
        for keyword in related[:5]:
            if keyword != main_keyword and len(keyword) > 2:
                metrics = self.get_search_volume(keyword)
                keyword_data = {
                    'keyword': keyword,
                    'type': '연관검색어',
                    'metrics': metrics,
                    'parent': main_keyword
                }
                all_keywords_data.append(keyword_data)
                max_volume = max(max_volume, metrics['actual_volume'])
        
        # 상대적 검색량 계산 및 정리
        for kw_data in all_keywords_data:
            volume = kw_data['metrics']['actual_volume']
            relative_percent = int((volume / max_volume * 100)) if max_volume > 0 else 0
            
            refined_keywords.append({
                'keyword': kw_data['keyword'],
                'type': kw_data['type'],
                'search_volume': relative_percent,  # 상대적 퍼센트
                'actual_volume': volume,  # 실제 추정 검색량
                'shop_count': kw_data['metrics']['shop_total'],  # 상품 수
                'blog_count': kw_data['metrics']['blog_total'],  # 블로그 수
                'parent': kw_data['parent']
            })
        
        # 실제 검색량 기준 정렬
        refined_keywords.sort(key=lambda x: x['actual_volume'], reverse=True)
        
        # 최소 5개 보장 - 부족하면 기본 조합 추가
        if len(refined_keywords) < 5:
            basic_combos = ['추천', '베스트', '인기', '최저가', '후기', '비교', '순위']
            for combo in basic_combos:
                if len(refined_keywords) >= 10:
                    break
                combo_keyword = f"{main_keyword} {combo}"
                if not any(kw['keyword'] == combo_keyword for kw in refined_keywords):
                    metrics = self.get_search_volume(combo_keyword)
                    refined_keywords.append({
                        'keyword': combo_keyword,
                        'type': '추천조합',
                        'search_volume': 50,  # 기본값
                        'actual_volume': metrics['actual_volume'],
                        'shop_count': metrics['shop_total'],
                        'blog_count': metrics['blog_total'],
                        'parent': main_keyword
                    })
        
        return {
            'main_keyword': main_keyword,
            'refined_keywords': refined_keywords[:15],  # 상위 15개
            'brands': predefined.get('brands', []),
            'features': predefined.get('features', []),
            'total_categories': len(shopping_categories)
        }
    
    def get_autocomplete_keywords(self, keyword: str) -> List[str]:
        """네이버 자동완성 API 활용"""
        # 실제로는 네이버 자동완성 API 사용
        # 여기서는 간단한 시뮬레이션
        
        autocomplete_map = {
            '선풍기': ['선풍기 추천', '선풍기 소음', '선풍기 다이슨', '선풍기 가격', 
                     '선풍기 전기세', '무소음 선풍기', 'BLDC 선풍기'],
            '캠핑': ['캠핑장 추천', '캠핑용품', '캠핑 텐트', '캠핑카', '캠핑 초보',
                    '글램핑', '차박 캠핑', '캠핑 요리'],
            '에어컨': ['에어컨 추천', '에어컨 전기세', '에어컨 청소', '에어컨 설치',
                     '이동식 에어컨', '창문형 에어컨', '에어컨 렌탈']
        }
        
        return autocomplete_map.get(keyword, [])
    
    def analyze_shopping_categories(self, keyword: str) -> List[Dict]:
        """쇼핑 검색 결과에서 카테고리 분석"""
        url = "https://openapi.naver.com/v1/search/shop.json"
        params = {
            "query": keyword,
            "display": 100,
            "sort": "sim"
        }
        
        categories = {}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                items = response.json().get('items', [])
                
                # 카테고리별 집계
                for item in items:
                    cat1 = item.get('category1', '')
                    cat2 = item.get('category2', '')
                    cat3 = item.get('category3', '')
                    cat4 = item.get('category4', '')
                    
                    # 가장 구체적인 카테고리 사용
                    category = cat4 or cat3 or cat2 or cat1
                    if category:
                        categories[category] = categories.get(category, 0) + 1
                
                # 상위 카테고리 정렬
                sorted_categories = sorted(
                    categories.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                
                return [
                    {'name': cat[0], 'count': cat[1]} 
                    for cat in sorted_categories[:10]
                ]
                
        except Exception as e:
            print(f"카테고리 분석 실패: {e}")
            
        return []
    
    def get_search_volume(self, keyword: str) -> Dict:
        """키워드 검색량 및 관련 메트릭 수집"""
        metrics = {
            'shop_total': 0,
            'blog_total': 0,
            'news_total': 0,
            'relative_volume': 0,
            'actual_volume': 0
        }
        
        # 1. 쇼핑 검색 결과 수
        url = "https://openapi.naver.com/v1/search/shop.json"
        params = {"query": keyword, "display": 1}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                metrics['shop_total'] = response.json().get('total', 0)
        except:
            pass
        
        # 2. 블로그 검색 결과 수
        url = "https://openapi.naver.com/v1/search/blog.json"
        params = {"query": keyword, "display": 1}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                metrics['blog_total'] = response.json().get('total', 0)
        except:
            pass
        
        # 3. 실제 검색량 추정 (상품수 + 블로그수 기반)
        # 네이버는 실제 검색량을 제공하지 않으므로 추정
        if metrics['shop_total'] > 0:
            # 로그 스케일로 변환하여 더 현실적인 수치 제공
            import math
            metrics['actual_volume'] = int(math.log10(metrics['shop_total'] + 1) * 1000)
        
        return metrics
    
    def get_optimized_keywords(self, main_keyword: str, target_count: int = 5) -> List[Dict]:
        """최적화된 키워드 조합 추천"""
        refined = self.get_related_keywords(main_keyword)
        
        # 상위 키워드 선택
        top_keywords = refined['refined_keywords'][:target_count]
        
        # 각 키워드에 대한 추가 정보
        optimized = []
        for kw in top_keywords:
            # 브랜드 조합
            if refined['brands']:
                for brand in refined['brands'][:2]:
                    optimized.append({
                        'keyword': f"{brand} {kw['keyword']}",
                        'type': '브랜드+카테고리',
                        'competition': 'medium',
                        'potential': 'high'
                    })
            
            # 특성 조합
            if refined['features']:
                for feature in refined['features'][:2]:
                    optimized.append({
                        'keyword': f"{feature} {kw['keyword']}",
                        'type': '특성+카테고리',
                        'competition': 'low',
                        'potential': 'medium'
                    })
        
        return optimized[:10]

# 테스트
if __name__ == "__main__":
    refiner = KeywordRefiner()
    
    test_keywords = ['선풍기', '캠핑', '에어컨']
    
    for keyword in test_keywords:
        print(f"\n{'='*50}")
        print(f"🔍 '{keyword}' 세분화 분석")
        print('='*50)
        
        result = refiner.get_related_keywords(keyword)
        
        print(f"\n📊 세분화된 키워드 (상위 10개):")
        for i, refined in enumerate(result['refined_keywords'][:10], 1):
            print(f"{i:2d}. {refined['keyword']:<20} "
                  f"[{refined['type']}] "
                  f"검색량: {'█' * (refined['search_volume']//20)}{refined['search_volume']}")
        
        if result['brands']:
            print(f"\n🏢 주요 브랜드: {', '.join(result['brands'])}")
        
        if result['features']:
            print(f"✨ 주요 특성: {', '.join(result['features'])}")