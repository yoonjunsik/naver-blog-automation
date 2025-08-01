#!/usr/bin/env python3
"""
네이버 블로그 자동화 웹 인터페이스
"""
from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
from advanced_keyword_analyzer import AdvancedKeywordAnalyzer
from expanded_keyword_list import KEYWORDS
import requests
from dotenv import load_dotenv
import json
from keyword_refiner import KeywordRefiner
from auto_updater import updater

load_dotenv()

app = Flask(__name__)
analyzer = AdvancedKeywordAnalyzer()
refiner = KeywordRefiner()

# 자동 업데이트 스케줄러 시작
updater.start_scheduler()

# 전역 변수로 분석 결과 저장 (이제 updater의 캐시 사용)
cached_analysis = {}

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """관리자 페이지"""
    return render_template('admin.html')

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """트렌드 키워드 가져오기"""
    category = request.args.get('category', 'all')
    
    # 자동 업데이트된 트렌드 키워드 사용
    trend_keywords = updater.trend_keywords
    
    if category == 'all':
        # 인기 키워드가 있으면 우선 표시
        trends = []
        
        # 인기 키워드 상위 5개 추가
        if updater.popular_keywords.get('keywords'):
            for keyword, data in list(updater.popular_keywords['keywords'].items())[:5]:
                trends.append({
                    'keyword': keyword,
                    'category': '인기급상승'
                })
        
        # 각 카테고리에서 상위 2개씩
        for cat_name, keywords in trend_keywords.items():
            if cat_name != '인기급상승':
                for keyword in keywords[:2]:
                    trends.append({
                        'keyword': keyword,
                        'category': cat_name
                    })
    else:
        keywords = trend_keywords.get(category, [])
        trends = [{'keyword': k, 'category': category} for k in keywords]
    
    return jsonify({'trends': trends})

@app.route('/api/refine-keyword', methods=['POST'])
def refine_keyword():
    """키워드 세분화"""
    data = request.json
    keyword = data.get('keyword')
    
    if not keyword:
        return jsonify({'error': '키워드가 필요합니다'}), 400
    
    # 세분화된 키워드 가져오기
    refined_data = refiner.get_related_keywords(keyword)
    
    return jsonify(refined_data)

@app.route('/api/analyze', methods=['POST'])
def analyze_keyword():
    """키워드 분석"""
    data = request.json
    keyword = data.get('keyword')
    
    if not keyword:
        return jsonify({'error': '키워드가 필요합니다'}), 400
    
    # updater의 캐시 먼저 확인 (24시간 자동 만료)
    cached_data = updater.get_from_cache(f'analysis_{keyword}')
    if cached_data:
        metrics = cached_data
    else:
        # 새로 분석
        metrics = analyzer.analyze_keyword_metrics(keyword)
        # updater 캐시에 저장
        updater.add_to_cache(f'analysis_{keyword}', metrics)
    
    # 결과 정리
    posts_7d = metrics['blog_data']['recent_posts_7d']
    # 문자열("100+")이면 그대로, 숫자면 숫자로
    if isinstance(posts_7d, str):
        blog_posts_7d_display = posts_7d
    else:
        blog_posts_7d_display = posts_7d
    
    result = {
        'keyword': keyword,
        'total_products': metrics['shopping_data']['total_products'],
        'avg_price': int(metrics['shopping_data']['avg_price']),
        'blog_posts_7d': blog_posts_7d_display,
        'posting_frequency': metrics['blog_data']['posting_frequency'],
        'community_interest': metrics['cafe_data']['community_interest'],
        'total_score': metrics['total_score'],
        'recommendation': get_recommendation_text(metrics['total_score'])
    }
    
    return jsonify(result)

@app.route('/api/products', methods=['POST'])
def search_products():
    """상품 검색"""
    data = request.json
    keyword = data.get('keyword')
    
    if not keyword:
        return jsonify({'error': '키워드가 필요합니다'}), 400
    
    print(f"\n🔍 상품 검색 요청: {keyword}")
    
    # 네이버 쇼핑 API 호출
    headers = {
        "X-Naver-Client-Id": os.getenv('NAVER_CLIENT_ID'),
        "X-Naver-Client-Secret": os.getenv('NAVER_CLIENT_SECRET')
    }
    
    url = "https://openapi.naver.com/v1/search/shop.json"
    params = {
        "query": keyword,
        "display": 20,  # 더 많이 가져와서 선별
        "sort": "sim"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"API 응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            items = data.get('items', [])
            
            print(f"검색 결과: 총 {total}개, 받은 항목: {len(items)}개")
            
            products = []
            
            # 가격이 있는 상품만 필터링
            valid_items = [item for item in items if item.get('lprice') and int(item['lprice']) > 0]
            
            for item in valid_items[:8]:
                try:
                    product = {
                        'title': item['title'].replace('<b>', '').replace('</b>', ''),
                        'price': f"{int(item['lprice']):,}",
                        'link': item['link'],
                        'image': item.get('image', ''),
                        'mall': item.get('mallName', '네이버쇼핑'),
                        'category': item.get('category1', '')
                    }
                    products.append(product)
                except Exception as e:
                    print(f"상품 처리 오류: {e}")
                    continue
            
            if not products and total > 0:
                # 상품은 있지만 처리할 수 없는 경우
                print("⚠️ 상품은 있지만 유효한 데이터가 없습니다.")
                return jsonify({
                    'products': [],
                    'message': '상품 정보를 불러올 수 없습니다. 다른 키워드를 시도해보세요.'
                })
            
            return jsonify({'products': products})
        else:
            error_msg = f"API 오류: {response.status_code}"
            print(f"❌ {error_msg}")
            return jsonify({'error': error_msg, 'products': []}), 200
            
    except Exception as e:
        print(f"❌ 상품 검색 실패: {str(e)}")
        return jsonify({'error': '상품 검색 중 오류가 발생했습니다', 'products': []}), 200

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    """콘텐츠 생성"""
    data = request.json
    keyword = data.get('keyword')
    product = data.get('product')
    
    if not keyword or not product:
        return jsonify({'error': '키워드와 상품 정보가 필요합니다'}), 400
    
    # 블로그 후기 수집
    reviews = collect_blog_reviews(keyword)
    
    # 콘텐츠 생성
    content = create_blog_content(keyword, product, reviews)
    
    # 파일로 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"generated_content/{timestamp}_{keyword}.txt"
    os.makedirs("generated_content", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return jsonify({
        'content': content,
        'filename': filename
    })

def collect_blog_reviews(keyword):
    """블로그 후기 수집"""
    headers = {
        "X-Naver-Client-Id": os.getenv('NAVER_CLIENT_ID'),
        "X-Naver-Client-Secret": os.getenv('NAVER_CLIENT_SECRET')
    }
    
    url = "https://openapi.naver.com/v1/search/blog.json"
    params = {
        "query": f"{keyword} 후기",
        "display": 5,
        "sort": "sim"
    }
    
    reviews = []
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            items = response.json().get('items', [])
            for item in items:
                reviews.append({
                    'title': item['title'].replace('<b>', '').replace('</b>', ''),
                    'description': item['description'].replace('<b>', '').replace('</b>', '')[:200]
                })
    except:
        pass
    
    return reviews

def create_blog_content(keyword, product, reviews):
    """블로그 콘텐츠 생성"""
    content = f"""# {keyword} 구매 가이드 - {product['title']}

안녕하세요! 오늘은 많은 분들이 관심 있어 하시는 '{keyword}'에 대해 알아보겠습니다.
특히 '{product['title']}' 제품을 중심으로 자세히 살펴보도록 하겠습니다.

## 📌 제품 정보

- **제품명**: {product['title']}
- **가격**: {product['price']}원
- **판매처**: {product['mall']}
- **카테고리**: {product['category']}

## 🛍️ 구매 링크
[👉 최저가 구매하기]({product['link']})

## 💬 실제 사용자 후기

"""
    
    # 수집된 후기 추가
    if reviews:
        for i, review in enumerate(reviews[:3], 1):
            content += f"""
### 후기 {i}
**{review['title']}**
{review['description']}...

"""
    else:
        content += "아직 상세한 후기가 없습니다.\n\n"
    
    content += f"""
## 🎯 구매 포인트

1. **가격대**: 현재 {product['price']}원으로 판매 중
2. **판매처**: {product['mall']}에서 안전하게 구매 가능
3. **배송**: 빠른 배송으로 바로 사용 가능

## 📝 구매 시 체크리스트

- [ ] 정품 인증 여부 확인
- [ ] A/S 가능 여부 확인
- [ ] 배송비 포함 최종 가격 확인
- [ ] 리뷰 및 평점 확인

## 마무리

오늘 소개해드린 {keyword} 제품이 도움이 되셨길 바랍니다.
구매 전 꼭 여러 후기를 확인하시고, 본인에게 맞는 제품을 선택하세요!

---
*이 포스팅은 쿠팡 파트너스 활동의 일환으로, 일정액의 수수료를 제공받을 수 있습니다.*

#네이버쇼핑 #{keyword} #{keyword}추천 #{keyword}구매가이드
"""
    
    return content

def get_recommendation_text(score):
    """점수에 따른 추천 텍스트"""
    if score >= 80:
        return "💎 매우 추천"
    elif score >= 60:
        return "✅ 추천"
    elif score >= 40:
        return "⚡ 보통"
    else:
        return "⚠️ 신중히 검토"

@app.route('/api/admin/status', methods=['GET'])
def admin_status():
    """관리자 상태 확인"""
    status = {
        'trend_keywords_count': len(updater.trend_keywords),
        'popular_keywords_count': len(updater.popular_keywords.get('keywords', {})),
        'cache_entries': len(updater.cache_data),
        'last_trend_update': updater.trend_keywords.get('updated_at', 'N/A'),
        'last_popular_update': updater.popular_keywords.get('updated_at', 'N/A')
    }
    return jsonify(status)

@app.route('/api/admin/force-update', methods=['POST'])
def admin_force_update():
    """강제 업데이트"""
    update_type = request.json.get('type', 'all')
    
    try:
        if update_type == 'trends':
            updater.update_trend_keywords()
        elif update_type == 'popular':
            updater.update_popular_keywords()
        elif update_type == 'cache':
            updater.clean_expired_cache()
        else:
            updater.force_update_all()
        
        return jsonify({'success': True, 'message': f'{update_type} 업데이트 완료'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('generated_content', exist_ok=True)
    
    # 환경 변수로 프로덕션/개발 모드 구분
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        print("🌐 프로덕션 서버 시작")
        app.run(host='0.0.0.0', debug=False, port=int(os.environ.get('PORT', 8000)))
    else:
        print("🌐 개발 서버 시작: http://localhost:8890")
        app.run(host='127.0.0.1', debug=True, port=8890)