# run.py

import subprocess
import sys
import os

# 현재 폴더 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# day7 프로그램 실행
script_path = os.path.join(current_dir, "day7_shipping_analyzer_v2.py")

try:
    subprocess.run([sys.executable, script_path], check=True)
    print("✅ 분석 완료!")
except Exception as e:
    print(f"❌ 오류: {e}")