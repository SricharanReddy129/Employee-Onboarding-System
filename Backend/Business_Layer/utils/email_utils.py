import smtplib
from email.message import EmailMessage
from ...config.env_loader import get_env_var 
 
EMAIL_USER = get_env_var("EMAIL_USER")
EMAIL_PASSWORD = get_env_var("EMAIL_PASSWORD")
EMAIL_HOST = get_env_var("EMAIL_HOST")
EMAIL_PORT = int(get_env_var("EMAIL_PORT"))
# FRONTEND_URL = get_env_var("FRONTEND_URL")
 
def send_email(to_email: str, subject: str, content: str):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg.set_content(content)

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")