# day7_shipping_analyzer_v2.py

"""
해운시황 자동 뉴스 분석 프로그램 (리팩토링 버전)

흐름:
1. NewsAPI에서 뉴스 수집 (fetch_news)
2. Claude AI로 감정 분석 (analyze_articles)
3. JSON 파일로 저장 (save_results)
4. 통계 출력 (print_statistics)
"""
import os
from datetime import datetime
from utils import fetch_news, analyze_articles, save_results, print_statistics
from config import NEWS_CONFIG, CLAUDE_CONFIG, CLAUDE_API_KEY
from anthropic import Anthropic


def main():
    """
    메인 함수: 뉴스 수집부터 분석, 저장, 통계까지 전체 흐름 처리
    """
    
    print("=" * 70)
    print("🚢 해운시황 뉴스 자동 분석 프로그램 (개선 버전)")
    print("=" * 70 + "\n")
    
    print("📱 Step 1: Claude 클라이언트 준비 중...\n")
    client = Anthropic(api_key=CLAUDE_API_KEY)  # ← API 키 전달!
    
    # Step 2: 뉴스 수집
    print("📱 Step 2: 뉴스 수집 중...\n")
    articles = fetch_news(
        queries=NEWS_CONFIG["queries"],
        language=NEWS_CONFIG["language"],
        days_back=NEWS_CONFIG["days_back"],
        page_size=NEWS_CONFIG["page_size"]
    )
    
    # 뉴스가 없으면 종료
    if not articles:
        print("❌ 수집된 뉴스가 없습니다")
        return
    
    # Step 3: 감정 분석
    print("📱 Step 3: 감정 분석 중...\n")
    analyses = analyze_articles(articles, client, CLAUDE_CONFIG)
    
    # Step 4: 결과 저장
    print("📱 Step 4: 결과 저장 중...\n")
    
    # 현재 스크립트 폴더를 기준으로 절대 경로 생성
    script_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(script_dir, "reports")
    
    filepath = save_results(analyses, reports_dir)
    
    # Step 5: 통계 출력
    print("📱 Step 5: 통계 출력 중...\n")
    stats = print_statistics(analyses)
    
    # 최종 완료 메시지
    print("=" * 70)
    print("✅ 모든 작업 완료!")
    print("=" * 70)
    print(f"\n📁 결과 파일: {filepath}")
    print(f"📊 분석한 뉴스: {stats['총_뉴스']}개")
    print(f"💵 예상 비용: 약 {stats['예상_비용_원']:,}원\n")


if __name__ == "__main__":
    main()