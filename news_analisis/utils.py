# utils.py
# utils.py 맨 위

import requests
import json  # ← 있나요?
import os   # ← 있나요?import requests
from datetime import datetime, timedelta

def fetch_news(queries, language="ko", days_back=7, page_size=10):
    """
    NewsAPI에서 여러 검색어로 뉴스를 수집합니다
    
    Args:
        queries (list): 검색 키워드 리스트
                       예: ["해운", "LNG선", "컨테이너선"]
        language (str): 검색 언어 (기본값: "ko" = 한국어)
        days_back (int): 며칠 전부터의 뉴스 (기본값: 7일)
        page_size (int): 한 번에 가져올 뉴스 개수 (기본값: 10개)
    
    Returns:
        list: 중복 제거된 뉴스 딕셔너리 리스트
              각 항목: {"title": "제목", "description": "설명", ...}
    
    Raises:
        Exception: API 요청 실패 시
    
    Example:
        >>> articles = fetch_news(["해운", "LNG선"])
        >>> print(len(articles))  # 뉴스 개수 출력
    """
    
    from config import NEWSAPI_KEY
    
    # NewsAPI 설정
    api_url = "https://newsapi.org/v2/everything"
    
    # 날짜 계산 (7일 전부터 오늘까지)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    all_articles = []
    
    # 각 검색어로 뉴스 수집
    for query in queries:
        print(f"🔍 '{query}' 검색 중...")
        
        params = {
            "q": query,
            "language": language,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "sortBy": "publishedAt",
            "pageSize": page_size,
            "apiKey": NEWSAPI_KEY
        }
        
        try:
            # API 요청
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()  # 오류 확인
            
            # 응답 처리
            data = response.json()
            articles = data.get("articles", [])
            all_articles.extend(articles)
            
            print(f"  ✅ {len(articles)}개 뉴스 수집")
            
        except requests.exceptions.Timeout:
            print(f"  ⚠️ 요청 타임아웃: {query}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ 요청 실패: {e}")
    
    # 중복 제거
    seen = set()
    unique_articles = []
    
    for article in all_articles:
        title = article.get("title", "")
        if title not in seen:
            seen.add(title)
            unique_articles.append(article)
    
    print(f"\n📊 총 {len(unique_articles)}개 뉴스 수집 완료 (중복 제거됨)\n")
    
    return unique_articles
def analyze_articles(articles, client, model_config):
    """
    Claude AI로 각 뉴스 기사의 감정을 분석합니다
    
    Args:
        articles (list): 분석할 뉴스 기사 리스트
        client: Anthropic API 클라이언트
        model_config (dict): 모델 설정
                           {"model": "claude-haiku-4-5", 
                            "max_tokens": 300, 
                            "temperature": 0.7}
    
    Returns:
        list: 분석 결과 딕셔너리 리스트
              각 항목: {"제목": "...", "감정": "긍정/부정/중립", "토큰": {...}}
    
    Example:
        >>> analyses = analyze_articles(articles, client, CLAUDE_CONFIG)
    """
    
    all_analyses = []
    sentiment_count = {"긍정": 0, "부정": 0, "중립": 0}
    total_input_tokens = 0
    total_output_tokens = 0
    
    # 각 뉴스 분석
    for i, article in enumerate(articles, 1):
        title = article.get("title", "제목 없음")
        description = article.get("description", "")
        content = article.get("content", "")
        
        # Claude에게 보낼 메시지
        prompt = f"""다음 뉴스 기사의 감정을 분석해줄래요.

제목: {title}
요약: {description}
본문: {content}

감정을 "긍정", "부정", "중립" 중 하나로 분류해줘. 
한 단어로만 대답해줘."""
        
        try:
            # Claude API 호출
            response = client.messages.create(
                model=model_config["model"],
                max_tokens=model_config["max_tokens"],
                temperature=model_config["temperature"],
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # 응답 처리
            sentiment = response.content[0].text.strip()
            
            # 유효한 감정인지 확인
            if sentiment not in ["긍정", "부정", "중립"]:
                sentiment = "중립"  # 오류 시 중립으로 처리
            
            sentiment_count[sentiment] += 1
            
            # 토큰 계산
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            
            # 결과 저장
            result = {
                "제목": title,
                "요약": description,
                "본문": content,
                "출처": article.get("source", {}).get("name", "알 수 없음"),
                "발행일": article.get("publishedAt", "").split("T")[0],  # YYYY-MM-DD 형식만 추출
                "감정": sentiment,
                "토큰": {
                    "입력": input_tokens,
                    "출력": output_tokens
                }
            }
            
            all_analyses.append(result)
            
            print(f"[{i}] {title[:30]}... → {sentiment}")
            
        except Exception as e:
            print(f"[{i}] {title[:30]}... → 분석 실패: {e}")
    
    print(f"\n📊 분석 완료!")
    print(f"  긍정: {sentiment_count['긍정']}")
    print(f"  부정: {sentiment_count['부정']}")
    print(f"  중립: {sentiment_count['중립']}")
    print(f"  총 토큰: {total_input_tokens + total_output_tokens}\n")
    
    return all_analyses
def save_results(analyses, output_dir):
    """
    분석 결과를 JSON 파일로 저장합니다
    
    Args:
        analyses (list): 분석 결과 리스트
                        각 항목: {"제목": "...", "감정": "...", "토큰": {...}}
        output_dir (str): 저장할 폴더 경로
                         예: "C:\\...\\reports"
    
    Returns:
        str: 저장된 파일의 전체 경로
             예: "C:\\...\\analysis_results_20240605_143022.json"
    
    Example:
        >>> filepath = save_results(analyses, "reports")
        >>> print(filepath)
    """
    
    import json
    import os
    
    # 저장 폴더 생성 (없으면)
    os.makedirs(output_dir, exist_ok=True)
    
    # 타임스탬프가 포함된 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_results_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # JSON으로 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(analyses, f, ensure_ascii=False, indent=2)
    
    print(f"💾 결과 저장 완료!")
    print(f"📁 저장 위치: {filepath}\n")
    
    return filepath
def print_statistics(analyses):
    """
    분석 결과의 통계를 계산하고 출력합니다
    
    Args:
        analyses (list): 분석 결과 리스트
                        각 항목: {"제목": "...", "감정": "...", "토큰": {...}}
    
    Returns:
        dict: 통계 정보 딕셔너리
              {"총_뉴스": 10, 
               "긍정": 3, 
               "부정": 2, 
               "중립": 5,
               "총_토큰": 5000,
               "예상_비용_원": 65}
    
    Example:
        >>> stats = print_statistics(analyses)
        >>> print(stats["예상_비용_원"])  # 예상 비용 출력
    """
    
    # 감정별 집계
    sentiment_count = {"긍정": 0, "부정": 0, "중립": 0}
    total_input_tokens = 0
    total_output_tokens = 0
    
    # 각 분석 결과 집계
    for analysis in analyses:
        sentiment = analysis.get("감정", "중립")
        sentiment_count[sentiment] += 1
        
        tokens = analysis.get("토큰", {})
        total_input_tokens += tokens.get("입력", 0)
        total_output_tokens += tokens.get("출력", 0)
    
    # 비용 계산
    # Claude Haiku 가격: 입력 $0.8/1M, 출력 $4/1M
    input_cost = total_input_tokens * 0.0000008  # $
    output_cost = total_output_tokens * 0.000004  # $
    total_cost = input_cost + output_cost
    total_cost_krw = int(total_cost * 1300)  # 원화 (1$ ≈ 1300원)
    
    # 통계 정보 딕셔너리 생성
    stats = {
        "총_뉴스": len(analyses),
        "긍정": sentiment_count["긍정"],
        "부정": sentiment_count["부정"],
        "중립": sentiment_count["중립"],
        "총_입력_토큰": total_input_tokens,
        "총_출력_토큰": total_output_tokens,
        "총_토큰": total_input_tokens + total_output_tokens,
        "예상_비용_원": total_cost_krw
    }
    
    # 통계 출력
    print("=" * 70)
    print("📊 분석 통계")
    print("=" * 70)
    print(f"총 분석 뉴스: {stats['총_뉴스']}개")
    print(f"  - 긍정: {stats['긍정']}개")
    print(f"  - 부정: {stats['부정']}개")
    print(f"  - 중립: {stats['중립']}개")
    print(f"\n💰 토큰 사용")
    print(f"  - 입력: {stats['총_입력_토큰']:,}개")
    print(f"  - 출력: {stats['총_출력_토큰']:,}개")
    print(f"  - 합계: {stats['총_토큰']:,}개")
    print(f"\n💵 예상 비용: 약 {stats['예상_비용_원']:,}원")
    print("=" * 70 + "\n")
    
    return stats