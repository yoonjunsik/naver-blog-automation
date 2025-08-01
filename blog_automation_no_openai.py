#!/usr/bin/env python3
"""
네이버 블로그 자동화 - OpenAI 없는 버전
"""
import os
import json
import requests
from datetime import datetime
from typing import List, Dict
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time

# .env 파일 로드
load_dotenv()

class BlogAutomationSimple:
    def __init__(self):
        self.config = {
            'naver_client_id': os.getenv('NAVER_CLIENT_ID'),
            'naver_client_secret': os.getenv('NAVER_CLIENT_SECRET'),
        }
        
    def collect_trending_keywords(self) -> List[str]:
        """네이버 쇼핑 인기 키워드 수집"""
        print("🔍 트렌드 키워드 수집 중...")
        
        # 인기 키워드 (실제로는 크롤링이나 API로 수집)
        keywords = [
            "크리스마스 선물",
            "겨울 패딩",
            "에어프라이어",
            "무선 이어폰",
            "공기청정기"
        ]
        
        return keywords
    
    def search_products(self, keyword: str) -> Dict:
        """네이버 쇼핑 상품 검색"""
        print(f"🛍️ '{keyword}' 상품 검색 중...")
        
        url = "https://openapi.naver.com/v1/search/shop.json"
        headers = {
            "X-Naver-Client-Id": self.config['naver_client_id'],
            "X-Naver-Client-Secret": self.config['naver_client_secret']
        }
        params = {
            "query": keyword,
            "display": 5,
            "sort": "sim"  # 정확도순으로 변경
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 검색 성공! 총 {data.get('total', 0)}개 결과")
                products = []
                
                if 'items' in data and data['items']:
                    for item in data['items'][:3]:
                        product = {
                            'title': item['title'].replace('<b>', '').replace('</b>', ''),
                            'link': item['link'],
                            'price': int(item['lprice']),
                            'mall': item['mallName'],
                            'image': item['image']
                        }
                        products.append(product)
                    
                return {
                    'keyword': keyword,
                    'products': products
                }
        except Exception as e:
            print(f"❌ 상품 검색 실패: {e}")
        
        return {'keyword': keyword, 'products': []}
    
    def generate_blog_content_template(self, product_data: Dict) -> str:
        """템플릿 기반 블로그 콘텐츠 생성"""
        print(f"✍️ '{product_data['keyword']}' 콘텐츠 생성 중...")
        
        keyword = product_data['keyword']
        products = product_data['products']
        
        if not products:
            return ""
        
        # 블로그 포스트 템플릿
        content = f"""# {keyword} 추천 BEST 3 - 2025년 최신 상품 비교

안녕하세요! 오늘은 많은 분들이 찾고 계신 '{keyword}'에 대해 알아보겠습니다.
최근 인기 있는 제품들을 꼼꼼히 비교해보고, 여러분께 가장 좋은 선택을 도와드리겠습니다.

## 🏆 {keyword} TOP 3 제품 소개

"""
        
        for i, product in enumerate(products, 1):
            content += f"""
### {i}위. {product['title']}
- 💰 **가격**: {product['price']:,}원
- 🏪 **판매처**: {product['mall']}
- 🔗 [**제품 상세보기**]({product['link']})

**주요 특징**:
- 검증된 인기 상품
- 합리적인 가격대
- 빠른 배송 가능

---
"""
        
        content += f"""
## 💡 {keyword} 구매 가이드

1. **예산 설정**: 먼저 구매 예산을 정하세요
2. **용도 확인**: 사용 목적에 맞는 제품 선택
3. **리뷰 확인**: 실제 구매자들의 후기 확인
4. **가격 비교**: 여러 쇼핑몰 가격 비교

## 마무리

오늘 소개해드린 {keyword} 제품들은 모두 검증된 베스트셀러입니다.
본인의 필요와 예산에 맞는 제품을 선택하시면 좋겠습니다!

_이 포스팅은 쿠팡 파트너스 활동의 일환으로, 일정액의 수수료를 제공받을 수 있습니다._

#네이버쇼핑 #{keyword} #{keyword}추천 #인기상품
"""
        
        return content
    
    def save_content(self, content: str, keyword: str):
        """콘텐츠를 파일로 저장"""
        print(f"📄 콘텐츠 저장 중...")
        
        # blog_posts 폴더 생성
        os.makedirs("blog_posts", exist_ok=True)
        
        # 파일명 생성 (특수문자 제거)
        safe_keyword = keyword.replace(" ", "_").replace("/", "_")
        filename = f"blog_posts/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_keyword}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ 저장 완료: {filename}")
        
        # HTML 버전도 생성
        html_filename = filename.replace('.md', '.html')
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{keyword} 추천</title>
    <style>
        body {{ font-family: 'Noto Sans KR', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #03c75a; }}
        h2 {{ color: #333; margin-top: 30px; }}
        h3 {{ color: #666; }}
        a {{ color: #03c75a; }}
        hr {{ border: 1px solid #eee; margin: 20px 0; }}
    </style>
</head>
<body>
{content.replace('#', '').replace('**', '').replace('*', '•')}
</body>
</html>
"""
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML 버전도 저장: {html_filename}")
    
    def run(self):
        """메인 실행"""
        print(f"\n{'='*50}")
        print(f"🚀 블로그 자동화 시작 (OpenAI 없는 버전)")
        print(f"{'='*50}\n")
        
        # 1. 키워드 수집
        keywords = self.collect_trending_keywords()
        print(f"✅ 수집된 키워드: {len(keywords)}개")
        
        # 2. 각 키워드별 처리
        for keyword in keywords[:3]:  # 3개만 처리
            print(f"\n--- {keyword} 처리 중 ---")
            
            # 상품 검색
            product_data = self.search_products(keyword)
            
            if product_data['products']:
                # 콘텐츠 생성
                content = self.generate_blog_content_template(product_data)
                
                if content:
                    # 저장
                    self.save_content(content, keyword)
                    
            time.sleep(1)  # API 제한 방지
        
        print(f"\n✅ 자동화 완료! blog_posts 폴더를 확인하세요.")
        print(f"{'='*50}\n")

if __name__ == "__main__":
    automation = BlogAutomationSimple()
    automation.run()