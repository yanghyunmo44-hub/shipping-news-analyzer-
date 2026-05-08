# send_email.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import glob  # ← 추가!
from config import EMAIL_CONFIG


def find_latest_report(directory):
    """
    폴더에서 가장 최신의 monthly_report_*.html 파일을 찾음
    
    Args:
        directory: 파일을 찾을 폴더 경로
    
    Returns:
        str: 최신 리포트 파일의 전체 경로
        None: 파일이 없으면 None 반환
    """
    
    # 폴더에서 monthly_report_*.html 패턴의 모든 파일 찾기
    pattern = os.path.join(directory, "monthly_report_*.html")
    files = glob.glob(pattern)
    
    # 파일이 없으면 None 반환
    if not files:
        return None
    
    # 파일을 정렬 (가장 최신 파일이 마지막)
    files.sort()
    
    # 가장 최신 파일 반환
    latest_file = files[-1]
    return latest_file


class EmailSender:
    """이메일을 보내는 클래스"""
    
    def __init__(self, sender_email, sender_password):
        """
        이메일 발송자 초기화
        
        Args:
            sender_email: Gmail 주소 (예: your_email@gmail.com)
            sender_password: Gmail 앱 비밀번호 (16자리)
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    
    def send_report(self, recipient_email, report_file):
        """
        월간 리포트를 HTML 형식으로 이메일 전송
        
        Args:
            recipient_email: 받는 사람 이메일
            report_file: HTML 리포트 파일 경로
        
        Returns:
            bool: 성공하면 True, 실패하면 False
        """
        
        # Step 1: 리포트 파일이 존재하는지 확인
        if not os.path.exists(report_file):
            print(f"❌ 리포트 파일을 찾을 수 없습니다: {report_file}")
            return False
        
        # Step 2: HTML 파일 읽기
        with open(report_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Step 3: 이메일 메시지 생성
        message = MIMEMultipart("alternative")
        
        # 이메일 헤더
        message["Subject"] = f"🚢 해운시황 월간 리포트 {datetime.now().strftime('%Y년 %m월')}"
        message["From"] = self.sender_email
        message["To"] = recipient_email
        
        # Step 4: HTML 본문 추가
        html_part = MIMEText(html_content, "html", "utf-8")
        message.attach(html_part)
        
        # Step 5: 이메일 발송
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            server.sendmail(
                self.sender_email,
                recipient_email,
                message.as_string()
            )
            
            server.quit()
            
            print(f"✅ 이메일 발송 완료: {recipient_email}")
            return True
        
        except Exception as e:
            print(f"❌ 이메일 발송 실패: {e}")
            return False


# 메인 실행
if __name__ == "__main__":
    sender = EmailSender(
        EMAIL_CONFIG["sender_email"],
        EMAIL_CONFIG["sender_password"]
    )
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 최신 리포트 파일 자동으로 찾기
    report_file = find_latest_report(current_dir)
    
    # 파일이 없으면 프로그램 종료
    if report_file is None:
        print("❌ 리포트 파일을 찾을 수 없습니다")
        print("   먼저 monthly_report_generator.py를 실행해주세요")
        exit()
    
    print(f"📁 최신 리포트 파일: {os.path.basename(report_file)}")
    
    recipients = EMAIL_CONFIG["recipient_list"]
    
    for recipient in recipients:
        print(f"\n📧 {recipient}에게 발송 중...")
        sender.send_report(recipient, report_file)
    
    print("\n🎉 모든 이메일 발송 완료!")