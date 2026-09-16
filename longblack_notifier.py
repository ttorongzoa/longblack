import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from playwright.sync_api import sync_playwright

def get_longblack_url():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # 롱블랙 메인 접속
        page.goto("https://www.longblack.co", timeout=60000)
        
        # 노트 링크 요소가 뜰 때까지 대기
        page.wait_for_selector("a[href*='/note/']")
        
        # 오늘 올라온 무료 노트 링크 추출
        note_element = page.query_selector("a[href*='/note/']")
        if note_element:
            href = note_element.get_attribute("href")
            title = note_element.inner_text().strip().split('\n')[0]
            link = f"https://www.longblack.co{href}" if href.startswith('/') else href
        else:
            title = "오늘의 롱블랙 노트"
            link = "https://www.longblack.co"
            
        browser.close()
        return title, link

def send_email(title, link):
    # Step 2에서 설정한 Secrets에서 안전하게 가져오기
    sender_email = os.environ.get("MY_GMAIL")
    app_password = os.environ.get("MY_GMAIL_APP_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_GMAIL")

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
    send_email(title, link)
    print("성공적으로 이메일을 발송했습니다!")
