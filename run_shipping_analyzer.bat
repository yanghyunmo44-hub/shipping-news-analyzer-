@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

set PYTHON_PATH=C:\Users\yangh\AppData\Local\Python\pythoncore-3.14-64\python.exe
cd /d "C:\Users\yangh\OneDrive\바탕 화면\파이썬"

"%PYTHON_PATH%" day7_shipping_analyzer_v2.py >> shipping_analysis.log 2>&1

echo 분석 완료!
pause