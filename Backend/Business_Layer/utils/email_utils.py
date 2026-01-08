import http
import smtplib
from email.message import EmailMessage
from ...config.env_loader import get_env_var 
from datetime import datetime
 
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

def send_offer_accepted_email(
    to_email: str,
    name: str,
    subject: str = "Offer Accepted – Next Steps"
    ,onboarding_url: str = ""
    ):
        """
        Sends a professional offer acceptance email to the candidate.
        """
        content = f"""
    Hello {name},

    Congratulations and thank you for accepting the offer!

    We are delighted to welcome you to the team. Your acceptance marks the beginning
    of an exciting journey with us, and we are thrilled to have you onboard.

    To proceed with the onboarding process, we kindly request you to upload the
    required documents using the secure link below:

    🔗 Upload Documents: {onboarding_url}

    Please ensure that all documents are submitted at your earliest convenience so
    we can complete the remaining formalities without delay.

    If you have any questions or need assistance, feel free to reach out to us.

    Once again, welcome aboard — we look forward to working with you!

    Warm regards,  
    Employee Onboarding System  
    Paves Technologies
    """

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
            return "Email sent successfully"
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return f"Failed to send email: {e}"
        # ----------------------------
def send_otp_email(
    to_email: str,
    otp: str,
    subject: str = "Email Verification OTP"
):
    """
    Sends a professional OTP verification email.
    """

    content = f"""
Hello,

We received a request to verify your email address as part of the Employee
Onboarding process.

Your One-Time Password (OTP) is:

🔐 OTP: {otp}

This OTP is valid for the next 5 minutes. Please do not share this OTP with
anyone for security reasons.

If you did not request this verification, please ignore this email.

Warm regards,  
Employee Onboarding System  
Paves Technologies
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(content)

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ OTP email sent to {to_email}")
        return "OTP email sent successfully"
    except Exception as e:
        print(f"❌ Failed to send OTP email to {to_email}: {e}")
        return f"Failed to send OTP email: {e}"

def send_candidate_onboarding_submitted_email(
    to_email: str,
    candidate_name: str,
    subject: str = "Onboarding Submitted Successfully"
):
    """
    Email sent to candidate after final onboarding submit
    """

    content = f"""
Hello {candidate_name},

Your onboarding details have been successfully submitted.

Our HR team will review your information and verify the submitted documents.
You will be notified if any additional action is required from your side.

Thank you for completing the onboarding process.

Warm regards,  
Employee Onboarding System  
Paves Technologies
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(content)

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Candidate onboarding email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send candidate onboarding email: {e}")

def send_hr_onboarding_submitted_email(
    hr_email: str,
    candidate_name: str,
    candidate_uuid: str,
    submitted_at: datetime,
    verify_documents_url: str,
    subject: str = "Candidate Onboarding Submitted"
):
    """
    Email sent to HR when candidate submits onboarding
    """

    submitted_time = submitted_at.strftime("%d-%m-%Y %H:%M:%S")

    content = f"""
Hello HR Team,

A candidate has completed the onboarding submission.

Candidate Details:
-------------------
Candidate Name : {candidate_name}
Candidate UUID : {candidate_uuid}
Submitted At   : {submitted_time}

Verify Documents:
-----------------
{verify_documents_url}


Regards,  
Employee Onboarding System  
Paves Technologies
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = hr_email
    msg.set_content(content)

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ HR onboarding notification email sent to {hr_email}")
    except Exception as e:
        print(f"❌ Failed to send HR onboarding email: {e}")

