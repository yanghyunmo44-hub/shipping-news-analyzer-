# day7_shipping_analyzer_v2.py

import requests
import json
from anthropic import Anthropic
from datetime import datetime
from config import NEWSAPI_KEY, CLAUDE_API_KEY, NEWS_CONFIG, CLAUDE_CONFIG

print("=" * 70)
print("🚢 해운시황 자동 분석 시스템 v2.0")
print("=" * 70)

# 1단계: 여러 검색어로 뉴스 수집
print("\n📰 Step 1: 뉴스 수집 중...\n")

all_articles = []

for query in NEWS_CONFIG["queries"]:
    print(f"  검색어: '{query}'...", end=" ")
    
    try:
        news_response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "language": NEWS_CONFIG["language"],
                "sortBy": NEWS_CONFIG["sort_by"],
                "pageSize": NEWS_CONFIG["page_size"],
                "apiKey": NEWSAPI_KEY
            },
            timeout=10
        )
        
        if news_response.status_code == 200:
            news_data = news_response.json()
            articles = news_data.get('articles', [])
            all_articles.extend(articles)
            print(f"✅ {len(articles)}개")
        else:
            print(f"❌ 상태 코드: {news_response.status_code}")
            
    except requests.exceptions.Timeout:
        print("❌ 타임아웃 (네트워크 느림)")
    except requests.exceptions.ConnectionError:
        print("❌ 연결 오류 (인터넷 확인)")
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

# 중복 제거
print("\n🔍 중복 제거 중...\n")

unique_articles = []
seen_titles = set()

for article in all_articles:
    title = article['title']
    if title not in seen_titles:
        unique_articles.append(article)
        seen_titles.add(title)

print(f"총 {len(unique_articles)}개 뉴스 수집 완료 (중복 제거)\n")

if len(unique_articles) == 0:
    print("❌ 분석할 뉴스가 없습니다")
    exit()

# 2단계: Claude API 준비
print("🤖 Step 2: Claude API 준비 중...\n")

client = Anthropic(api_key=CLAUDE_API_KEY)

# 3단계: 각 뉴스 분석
print("📊 Step 3: 뉴스 분석 중...\n")

all_analyses = []
sentiment_count = {"긍정": 0, "부정": 0, "중립": 0}

for i, article in enumerate(unique_articles, 1):
    title = article['title']
    source = article['source']['name']
    description = article.get('description', '')  # ← 추가
    content = article.get('content', '')          # ← 추가
    
    print(f"[{i}/{len(unique_articles)}] {title[:45]}...")
    
    try:
        # Claude에게 분석 요청
        response = client.messages.create(
            model=CLAUDE_CONFIG["model"],
            max_tokens=CLAUDE_CONFIG["max_tokens"],
            messages=[{
                "role": "user",
                "content": f"""
제목: {title}
출처: {source}
요약: {description}
본문: {content}

다음을 분석해줄래? 간단하게 3~4줄로:

1. 긍정/부정/중립 판단 (반드시 한 단어로 답변)
2. KOBC 신용리스크 영향
3. 추천 조치

형식:
판단: [긍정/부정/중립]
영향: [내용]
조치: [내용]
"""
            }]
        )
        
        analysis_text = response.content[0].text
        
        # 감정 추출
        sentiment = "중립"
        if "긍정" in analysis_text:
            sentiment = "긍정"
            sentiment_count["긍정"] += 1
        elif "부정" in analysis_text:
            sentiment = "부정"
            sentiment_count["부정"] += 1
        else:
            sentiment_count["중립"] += 1
        
        # 결과 저장
        result = {
            "순번": i,
            "제목": title,
            "출처": source,
            "발행일": article.get('publishedAt', '미정'),
            "요약": description,      # ← 추가
            "본문": content,         # ← 추가
            "분석": analysis_text,
            "감정": sentiment,
            "토큰": {
                "입력": response.usage.input_tokens,
                "출력": response.usage.output_tokens
            }
        }
        
        all_analyses.append(result)
        print(f"   ✅ 분석 완료 ({sentiment})\n")
        
    except Exception as e:
        print(f"   ❌ 분석 실패: {str(e)}\n")
        continue

if len(all_analyses) == 0:
    print("❌ 분석된 뉴스가 없습니다")
    exit()

# 4단계: 결과 저장
print("💾 Step 4: 결과 저장 중...\n")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"analysis_results_{timestamp}.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_analyses, f, ensure_ascii=False, indent=2)

# 5단계: 통계 및 요약
print("=" * 70)
print("📋 분석 완료 요약")
print("=" * 70)

total_input_tokens = sum(r['토큰']['입력'] for r in all_analyses)
total_output_tokens = sum(r['토큰']['출력'] for r in all_analyses)
total_tokens = total_input_tokens + total_output_tokens

# 비용 계산 (Haiku: $0.8/$4 per 1M tokens)
input_cost = total_input_tokens * 0.0000008
output_cost = total_output_tokens * 0.000004
total_cost = input_cost + output_cost

print(f"\n📊 분석 통계:")
print(f"  분석한 뉴스: {len(all_analyses)}개")
print(f"  긍정: {sentiment_count['긍정']}개")
print(f"  부정: {sentiment_count['부정']}개")
print(f"  중립: {sentiment_count['중립']}개")

print(f"\n💰 토큰 사용:")
print(f"  입력: {total_input_tokens}")
print(f"  출력: {total_output_tokens}")
print(f"  합계: {total_tokens}")

print(f"\n💵 예상 비용:")
print(f"  입력: ${input_cost:.6f} (약 {int(input_cost * 1300)}원)")
print(f"  출력: ${output_cost:.6f} (약 {int(output_cost * 1300)}원)")
print(f"  합계: ${total_cost:.6f} (약 {int(total_cost * 1300)}원)")

print(f"\n📁 저장 위치: {output_file}")
print("\n✅ 모든 작업 완료!")