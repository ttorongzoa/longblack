import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from playwright.sync_api import sync_playwright

def get_longblack_url():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 실제 브라우저처럼 보이도록 User-Agent 설정
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            page.goto("https://www.longblack.co", timeout=60000, wait_until="networkidle")
            
            # /note/ 경로가 들어간 첫 번째 텍스트 링크 탐색
            note_element = page.locator("a[href*='/note/']").first
            
            if note_element.count() > 0:
                href = note_element.get_attribute("href")
                title = note_element.inner_text().strip().split('\n')[0]
                if not title:
                    title = "오늘의 롱블랙 노트"
                link = f"https://www.longblack.co{href}" if href.startswith('/') else href
            else:
                title = "오늘의 롱블랙 노트 (직접 확인)"
                link = "https://www.longblack.co"
        except Exception as e:
            print(f"페이지 로딩 중 오류 발생: {e}")
            title = "오늘의 롱블랙 노트 (접속 불가)"
            link = "https://www.longblack.co"
            
        browser.close()
        return title, link

def send_email(title, link):
    sender_email = os.environ.get("MY_GMAIL")
    app_password = os.environ.get("MY_GMAIL_APP_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_GMAIL")

    if not sender_email or not app_password or not receiver_email:
        raise ValueError("Secrets 값이 설정되지 않았습니다. Settings -> Secrets를 확인해주세요.")

    # 앱 비밀번호 공백 제거
    app_password = app_password.replace(" ", "")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"[롱블랙] 오늘 매일 무료 아티클: {title}"

    body = f"""안녕하세요!

오늘의 롱블랙 무료 아티클이 발행되었습니다.
오늘 하루 동안만 무료로 읽으실 수 있으니 확인해 보세요!

📌 아티클: {title}
🔗 읽으러 가기: {link}
"""
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()

if __name__ == "__main__":
    title, link = get_longblack_url()
    print(f"추출 성공 - 제목: {title}, 링크: {link}")
    send_email(title, link)
    print("성공적으로 이메일을 발송했습니다!")
