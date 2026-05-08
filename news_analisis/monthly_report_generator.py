# monthly_report_generator.py

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from config import EMAIL_CONFIG  # config.py에서 이메일 정보 가져오기

current_dir = os.path.dirname(os.path.abspath(__file__))


def find_recent_analysis_files(days=30):
    """지난 N일간의 분석 JSON 파일 찾기"""
    
    # reports 폴더 경로
    reports_dir = os.path.join(current_dir, "reports")
    
    files = []
    
    # reports 폴더가 없으면 현재 폴더 사용
    if not os.path.exists(reports_dir):
        reports_dir = current_dir
    
    for filename in os.listdir(reports_dir):
        if filename.startswith("analysis_results_") and filename.endswith(".json"):
            files.append(filename)
    
    files.sort()
    
    print(f"📁 찾은 분석 파일: {len(files)}개")
    for f in files:
        print(f"  - {f}")
    
    return files, reports_dir


def load_and_merge_data(files, reports_dir):
    """여러 JSON 파일을 읽어서 통합"""
    
    all_data = []
    weekly_stats = {}
    
    for filename in files:
        filepath = os.path.join(reports_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_data.extend(data)
                
                week_key = filename.split('_')[2][:8]
                if week_key not in weekly_stats:
                    weekly_stats[week_key] = {
                        "긍정": 0,
                        "부정": 0,
                        "중립": 0
                    }
                
                for article in data:
                    sentiment = article.get('감정', '중립')
                    weekly_stats[week_key][sentiment] += 1
                    
        except Exception as e:
            print(f"❌ {filename} 읽기 실패: {e}")
    
    return all_data, weekly_stats


def calculate_statistics(all_data, weekly_stats):
    """전체 통계 계산"""
    
    total_sentiment = {"긍정": 0, "부정": 0, "중립": 0}
    total_input_tokens = 0
    total_output_tokens = 0
    
    for article in all_data:
        sentiment = article.get('감정', '중립')
        total_sentiment[sentiment] += 1
        
        tokens = article.get('토큰', {})
        total_input_tokens += tokens.get('입력', 0)
        total_output_tokens += tokens.get('출력', 0)
    
    input_cost = total_input_tokens * 0.0000008
    output_cost = total_output_tokens * 0.000004
    total_cost = input_cost + output_cost
    
    stats = {
        "총_뉴스": len(all_data),
        "감정": total_sentiment,
        "긍정_비율": round(total_sentiment["긍정"] / len(all_data) * 100, 1) if len(all_data) > 0 else 0,
        "부정_비율": round(total_sentiment["부정"] / len(all_data) * 100, 1) if len(all_data) > 0 else 0,
        "중립_비율": round(total_sentiment["중립"] / len(all_data) * 100, 1) if len(all_data) > 0 else 0,
        "총_입력_토큰": total_input_tokens,
        "총_출력_토큰": total_output_tokens,
        "총_토큰": total_input_tokens + total_output_tokens,
        "예상_비용": int(total_cost * 1300)
    }
    
    return stats


def get_sentiment_description(stats):
    """감정 분석에 따른 설명"""
    positive = stats['긍정_비율']
    negative = stats['부정_비율']
    
    if positive > negative + 10:
        return "긍정적 💚"
    elif negative > positive + 10:
        return "부정적 ❌"
    else:
        return "중립적 ⚖️"


def generate_html_report(stats, weekly_stats, all_data):
    """HTML 리포트 생성"""
    
    # 현재 월
    now = datetime.now()
    month_str = now.strftime("%Y년 %m월")
    filename = now.strftime("monthly_report_%Y%m.html")
    
    # 주간 통계 HTML 생성
    weekly_rows = ""
    for week_date in sorted(weekly_stats.keys()):
        week_stats = weekly_stats[week_date]
        total = week_stats['긍정'] + week_stats['부정'] + week_stats['중립']
        weekly_rows += f"""
        <tr>
            <td>{week_date}</td>
            <td style="color: #27ae60; font-weight: bold;">{week_stats['긍정']}</td>
            <td style="color: #e74c3c; font-weight: bold;">{week_stats['부정']}</td>
            <td style="color: #95a5a6; font-weight: bold;">{week_stats['중립']}</td>
            <td>{total}</td>
        </tr>
        """
    
    # HTML 템플릿
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>해운시황 {month_str} 분석 리포트</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 5px solid #667eea;
        }}
        
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #666;
        }}
        
        .positive {{
            color: #27ae60 !important;
            border-left-color: #27ae60 !important;
        }}
        
        .negative {{
            color: #e74c3c !important;
            border-left-color: #e74c3c !important;
        }}
        
        .neutral {{
            color: #95a5a6 !important;
            border-left-color: #95a5a6 !important;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 15px;
            text-align: center;
            border-bottom: 1px solid #eee;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: bold;
            color: #333;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #eee;
        }}
        
        .progress-bar {{
            background: #eee;
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-positive {{
            background: #27ae60;
            height: 100%;
            width: {stats['긍정_비율']}%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚢 해운시황 분석 리포트</h1>
            <p>{month_str}</p>
        </div>
        
        <div class="content">
            <!-- 전체 통계 -->
            <div class="section">
                <h2 class="section-title">📊 전체 통계</h2>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{stats['총_뉴스']}</div>
                        <div class="stat-label">총 분석 뉴스</div>
                    </div>
                    
                    <div class="stat-card positive">
                        <div class="stat-value">{stats['감정']['긍정']}</div>
                        <div class="stat-label">긍정 ({stats['긍정_비율']}%)</div>
                    </div>
                    
                    <div class="stat-card negative">
                        <div class="stat-value">{stats['감정']['부정']}</div>
                        <div class="stat-label">부정 ({stats['부정_비율']}%)</div>
                    </div>
                    
                    <div class="stat-card neutral">
                        <div class="stat-value">{stats['감정']['중립']}</div>
                        <div class="stat-label">중립 ({stats['중립_비율']}%)</div>
                    </div>
                </div>
                
                <h3 style="margin-top: 20px; margin-bottom: 10px; color: #333;">감정 분포</h3>
                <div class="progress-bar">
                    <div class="progress-positive" style="width: {stats['긍정_비율']}%; background: linear-gradient(90deg, #27ae60, #2ecc71);">
                        {stats['긍정_비율']}%
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-positive" style="width: {stats['부정_비율']}%; background: linear-gradient(90deg, #e74c3c, #ec7063);">
                        {stats['부정_비율']}%
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-positive" style="width: {stats['중립_비율']}%; background: linear-gradient(90deg, #95a5a6, #bdc3c7);">
                        {stats['중립_비율']}%
                    </div>
                </div>
            </div>
            
            <!-- 주간 추이 -->
            <div class="section">
                <h2 class="section-title">📈 주간 추이</h2>
                
                <table>
                    <thead>
                        <tr>
                            <th>주차 (날짜)</th>
                            <th style="color: #27ae60;">긍정</th>
                            <th style="color: #e74c3c;">부정</th>
                            <th style="color: #95a5a6;">중립</th>
                            <th>합계</th>
                        </tr>
                    </thead>
                    <tbody>
                        {weekly_rows}
                    </tbody>
                </table>
            </div>
            
            <!-- 토큰 & 비용 -->
            <div class="section">
                <h2 class="section-title">💰 토큰 사용 & 비용</h2>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{stats['총_토큰']:,}</div>
                        <div class="stat-label">총 토큰 사용</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-value">{stats['총_입력_토큰']:,}</div>
                        <div class="stat-label">입력 토큰</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-value">{stats['총_출력_토큰']:,}</div>
                        <div class="stat-label">출력 토큰</div>
                    </div>
                    
                    <div class="stat-card" style="border-left-color: #f39c12;">
                        <div class="stat-value" style="color: #f39c12;">약 {stats['예상_비용']:,}원</div>
                        <div class="stat-label">예상 비용</div>
                    </div>
                </div>
            </div>
            
            <!-- 핵심 발견사항 -->
            <div class="section">
                <h2 class="section-title">🎯 핵심 발견사항</h2>
                
                <div style="background: #f0f3ff; padding: 20px; border-radius: 10px; line-height: 1.8; color: #333;">
                    <p>• <strong>전반적 분위기:</strong> {get_sentiment_description(stats)}</p>
                    <p>• <strong>강점:</strong> {'긍정 뉴스 증가 추세' if stats['긍정_비율'] > 40 else '중립적 시장 분위기 유지'}</p>
                    <p>• <strong>주의:</strong> {'부정 뉴스 주의' if stats['부정_비율'] > 30 else '시장 전반 안정적'}</p>
                    <p>• <strong>추세:</strong> 주간 데이터를 통해 장기 추이 모니터링 중</p>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
            <p>🚢 KOBC 해운시황 자동 분석 시스템</p>
        </div>
    </div>
</body>
</html>
"""
    
    # 파일로 저장
    filepath = os.path.join(current_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename


# 메인 실행
if __name__ == "__main__":
    print("=" * 70)
    print("🚢 해운시황 월간 리포트 생성기")
    print("=" * 70)
    
    # Step 1: 파일 찾기
    print("\n📁 Step 1: 분석 파일 찾는 중...\n")
    files, reports_dir = find_recent_analysis_files(days=30)
    
    if len(files) == 0:
        print("❌ 분석 파일이 없습니다")
        print("   먼저 day7_shipping_analyzer_v2.py를 실행해주세요")
        exit()
    
    # Step 2: 데이터 통합
    print(f"\n📊 Step 2: 데이터 통합 중...\n")
    all_data, weekly_stats = load_and_merge_data(files, reports_dir)
    print(f"  ✅ 총 {len(all_data)}개 뉴스 통합")
    
    # Step 3: 통계 계산
    print(f"\n📈 Step 3: 통계 계산 중...\n")
    stats = calculate_statistics(all_data, weekly_stats)
    print(f"  ✅ 긍정: {stats['감정']['긍정']}개 ({stats['긍정_비율']}%)")
    print(f"  ✅ 부정: {stats['감정']['부정']}개 ({stats['부정_비율']}%)")
    print(f"  ✅ 중립: {stats['감정']['중립']}개 ({stats['중립_비율']}%)")
    
    # Step 4: HTML 리포트 생성
    print(f"\n🎨 Step 4: HTML 리포트 생성 중...\n")
    report_file = generate_html_report(stats, weekly_stats, all_data)
    report_filepath = os.path.join(current_dir, report_file)
    
    print("=" * 70)
    print("✅ 리포트 생성 완료!")
    print("=" * 70)
    print(f"\n📁 저장 위치: {report_filepath}")
    
    # Step 5: 이메일로 자동 전송 (선택 사항)
    print(f"\n📧 Step 5: 이메일 발송 중...\n")
    
    try:
        # send_email 모듈 가져오기
        from send_email import EmailSender
        
        # config.py에서 이메일 정보 가져오기
        sender = EmailSender(
            EMAIL_CONFIG["sender_email"],
            EMAIL_CONFIG["sender_password"]
        )
        
        # 이메일 발송
        recipient = EMAIL_CONFIG["sender_email"]
        result = sender.send_report(recipient, report_filepath)
        
        if result:
            print("  ✅ 이메일 발송 성공!")
        else:
            print("  ⚠️ 이메일 발송 실패 (설정 확인 필요)")
    
    except ImportError:
        print("  💡 send_email 모듈이 없습니다 (선택 사항)")
    except Exception as e:
        print(f"  ⚠️ 이메일 발송 중 오류: {e}")
    
    print("\n🎉 모든 작업 완료!")