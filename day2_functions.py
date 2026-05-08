print("\n=== 현모님의 실습 ===")

# 함수 1: 당신의 정보 출력
def introduce_myself(name, position, years):
    """자신을 소개하는 함수"""
    print(f"저는 {name}입니다.")
    print(f"직급은 {position}이고, {years}년 근무했습니다.")

introduce_myself("양현모", "과장", 7)

print()

# 함수 2: 해운시황을 분석하는 함수
def analyze_shipping_market(market_trend, price_change):
    """
    market_trend: "상승" 또는 "하강"
    price_change: 가격 변화율 (%)
    """
    if market_trend == "상승":
        outlook = "긍정적"
    else:
        outlook = "부정적"
    
    if abs(price_change) > 10:
        volatility = "높음"
    else:
        volatility = "낮음"
    
    return outlook, volatility

# 테스트
trend1 = "상승"
change1 = 15
outlook1, volatility1 = analyze_shipping_market(trend1, change1)
print(f"시장 동향: {trend1}, 전망: {outlook1}, 변동성: {volatility1}")

trend2 = "하강"
change2 = 5
outlook2, volatility2 = analyze_shipping_market(trend2, change2)
print(f"시장 동향: {trend2}, 전망: {outlook2}, 변동성: {volatility2}")

def introduce_kobc():
    print("저는 한국해양진흥공사입니다")
    print("해운산업을 지원합니다")

# 함수 호출
introduce_kobc()
introduce_kobc()  # 두 번 호출

def introduce_myself(name, position, years):
    print(f"이름: {name}")
    print(f"직급: {position}")
    print(f"근무연수: {years}년")

# 당신 정보로 호출
introduce_myself("양현모", "과장", 7)

# 다른 사람 정보로도 호출
introduce_myself("김철수", "부장", 10)
introduce_myself("이영희", "대리", 3)
def evaluate_risk(debt_ratio):
    if debt_ratio < 30:
        return "낮음"
    else:
        return "높음"

# 함수 호출해서 결과 받기
risk1 = evaluate_risk(25)
risk2 = evaluate_risk(50)

print("회사 A 위험도:", risk1)
print("회사 B 위험도:", risk2)
def calculate_bonus(salary):
    """연봉을 받아서 보너스 계산하기"""
    bonus = salary * 0.1  # 연봉의 10%
    return bonus

# 테스트
my_salary = 50000000  # 5천만원
my_bonus = calculate_bonus(my_salary)
print(f"연봉: {my_salary}원")
print(f"보너스: {my_bonus}원")
def should_we_lend(debt_ratio, market_trend):
    """
    부채비율과 시장 동향을 받아서
    대출 여부 결정
    """
    if debt_ratio > 70:
        return "위험 - 대출 불가"
    elif market_trend == "상승":
        return "긍정적 - 대출 가능"
    else:
        return "보류 - 추가 검토 필요"

# 테스트
result1 = should_we_lend(45, "상승")
result2 = should_we_lend(75, "상승")
result3 = should_we_lend(50, "하강")

print("케이스 1:", result1)
print("케이스 2:", result2)
print("케이스 3:", result3)
def evaluate_shipping_company(company_name, debt_ratio):
    """
    해운회사의 신용도 평가
    debt_ratio: 부채비율 (0~100)
    """
    if debt_ratio < 30:
        grade = "A등급 - 매우 안전"
    elif debt_ratio < 60:
        grade = "B등급 - 보통"
    else:
        grade = "C등급 - 위험"
    
    return grade

# 당신이 테스트 케이스 만들어보세요
# (회사명과 부채비율을 정해서 호출)
result = evaluate_shipping_company("한진해운", 45)
print(result)