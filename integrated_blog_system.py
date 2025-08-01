#!/usr/bin/env python3
"""
통합 블로그 자동화 시스템
- 대량 키워드 분석
- Google Sheets 자동 저장
- 선택적 콘텐츠 생성
"""
import os
from datetime import datetime
from advanced_keyword_analyzer import AdvancedKeywordAnalyzer
from google_sheets_integration import GoogleSheetsManager
from expanded_keyword_list import get_all_keywords, KEYWORDS
import time

class IntegratedBlogSystem:
    def __init__(self):
        self.analyzer = AdvancedKeywordAnalyzer()
        try:
            self.sheets_manager = GoogleSheetsManager()
            self.use_sheets = True
        except:
            print("⚠️ Google Sheets 연동 실패. 로컬 저장만 사용합니다.")
            self.use_sheets = False
    
    def analyze_category(self, category_name: str):
        """카테고리별 키워드 분석"""
        keywords = KEYWORDS.get(category_name, [])
        if not keywords:
            print(f"❌ '{category_name}' 카테고리를 찾을 수 없습니다.")
            return
        
        print(f"\n📂 [{category_name}] 카테고리 분석 시작")
        print(f"키워드 {len(keywords)}개 분석 중...")
        
        results = []
        for i, keyword in enumerate(keywords, 1):
            print(f"\n[{i}/{len(keywords)}] {keyword} 분석 중...")
            metrics = self.analyzer.analyze_keyword_metrics(keyword)
            
            # 결과 정리
            result = {
                'keyword': keyword,
                'total_products': metrics['shopping_data']['total_products'],
                'avg_price': metrics['shopping_data']['avg_price'],
                'posts_7d': metrics['blog_data']['recent_posts_7d'],
                'posts_24h': metrics['blog_data']['recent_posts_24h'],
                'posting_freq': metrics['blog_data']['posting_frequency'],
                'community_interest': metrics['cafe_data']['community_interest'],
                'total_score': metrics['total_score']
            }
            results.append(result)
            
            # API 제한 방지
            time.sleep(0.5)
        
        return results
    
    def run_full_analysis(self):
        """전체 카테고리 분석"""
        print("\n🚀 통합 블로그 키워드 분석 시스템")
        print("="*60)
        
        all_results = []
        
        # 카테고리 선택
        print("\n분석할 카테고리를 선택하세요:")
        categories = list(KEYWORDS.keys())
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat} ({len(KEYWORDS[cat])}개 키워드)")
        print(f"{len(categories)+1}. 전체 분석")
        
        choice = input("\n선택 (번호 입력): ")
        
        try:
            choice_num = int(choice)
            if choice_num == len(categories) + 1:
                # 전체 분석
                for category in categories:
                    results = self.analyze_category(category)
                    all_results.extend(results)
            elif 1 <= choice_num <= len(categories):
                # 특정 카테고리 분석
                category = categories[choice_num - 1]
                all_results = self.analyze_category(category)
            else:
                print("❌ 잘못된 선택입니다.")
                return
        except:
            print("❌ 숫자를 입력해주세요.")
            return
        
        # 결과 저장
        self.save_results(all_results)
        
        # 상위 키워드 표시
        self.display_top_keywords(all_results)
        
        # 콘텐츠 생성 여부 확인
        self.generate_content_for_top(all_results)
    
    def save_results(self, results: list):
        """결과 저장"""
        # Google Sheets 저장
        if self.use_sheets:
            try:
                sheet_url = self.sheets_manager.save_keyword_analysis(results)
                print(f"\n✅ Google Sheets 저장 완료!")
                print(f"🔗 {sheet_url}")
            except Exception as e:
                print(f"❌ Sheets 저장 실패: {e}")
        
        # 로컬 CSV 저장
        import pandas as pd
        df = pd.DataFrame(results)
        filename = f"keyword_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 로컬 저장: {filename}")
    
    def display_top_keywords(self, results: list, top_n: int = 10):
        """상위 키워드 표시"""
        sorted_results = sorted(results, key=lambda x: x['total_score'], reverse=True)
        
        print(f"\n🏆 상위 {top_n}개 키워드")
        print("="*80)
        print(f"{'순위':<4} {'키워드':<15} {'점수':<6} {'상품수':<10} {'7일포스팅':<10} {'추천도':<10}")
        print("-"*80)
        
        for i, item in enumerate(sorted_results[:top_n], 1):
            score = item['total_score']
            if score >= 80:
                recommend = "💎 매우높음"
            elif score >= 60:
                recommend = "✅ 높음"
            elif score >= 40:
                recommend = "⚡ 보통"
            else:
                recommend = "⚠️ 낮음"
            
            print(f"{i:<4} {item['keyword']:<15} {score:<6.1f} {item['total_products']:<10,} "
                  f"{item['posts_7d']:<10} {recommend:<10}")
    
    def generate_content_for_top(self, results: list):
        """상위 키워드 콘텐츠 생성"""
        sorted_results = sorted(results, key=lambda x: x['total_score'], reverse=True)
        top_keywords = [r['keyword'] for r in sorted_results[:5]]
        
        print(f"\n📝 콘텐츠 생성 옵션")
        print(f"상위 5개 키워드: {', '.join(top_keywords)}")
        
        choice = input("\n콘텐츠를 생성하시겠습니까? (y/n): ")
        if choice.lower() == 'y':
            # 기존 blog_automation_no_openai.py의 콘텐츠 생성 로직 활용
            print("✅ 콘텐츠 생성을 시작합니다...")
            # 여기에 콘텐츠 생성 로직 추가
            
            # Sheets에 로그 저장
            if self.use_sheets:
                for keyword in top_keywords[:3]:  # 상위 3개만
                    self.sheets_manager.save_content_log(
                        keyword, 
                        f"blog_posts/{keyword}_{datetime.now().strftime('%Y%m%d')}.md"
                    )

def main():
    system = IntegratedBlogSystem()
    system.run_full_analysis()

if __name__ == "__main__":
    main()