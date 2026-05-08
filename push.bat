@echo off
chcp 65125 > nul

echo 📝 파일 추가 중...
git add .

echo 💬 메시지 입력:
set /p message="커밋 메시지: "

echo 📤 커밋 중...
git commit -m "%message%"

echo 🚀 GitHub에 푸시 중...
git push

echo ✅ 완료!
pause