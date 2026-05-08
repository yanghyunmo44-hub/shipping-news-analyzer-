print("\n=== 현모님 실습 ===")

# 당신이 관심 있는 주제 리스트 만들기
topics = ["신용평가", "해운시황", "금융정책", "리스크관리"]

# 아래 함수를 만들어보세요
# 함수 이름: check_interest
# 입력값: topic (주제)
# 기능: "신용평가"나 "금융정책"이 들어오면 "관심있음"
#      나머지는 "관심없음"이라고 리턴

# 함수 정의 시작 (아래에 작성)
def check_interest(topic):
    # 여기에 코드 작성
    if topic == "신용평가" or topic == "금융정책":
        return "관심있음"
    else:        return "관심없음"

# for 루프로 각 주제를 함수에 보내기
for topic in topics:
    result = check_interest(topic)
    print(f"{topic}: {result}")