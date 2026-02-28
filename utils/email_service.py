import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_email(to_email, subject, body):
    try:
        smtp_server = current_app.config['SMTP_SERVER']
        smtp_port = current_app.config['SMTP_PORT']
        smtp_username = current_app.config['SMTP_USERNAME']
        smtp_password = current_app.config['SMTP_PASSWORD']
        
        if not smtp_username or not smtp_password:
            print("Email configuration not set. Skipping email send.")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_complaint_status_email(user_email, complaint_id, status):
    subject = f"Complaint #{complaint_id} Status Update"
    body = f"""
    <html>
        <body>
            <h2>TrackMyWaste - Complaint Status Update</h2>
            <p>Your complaint (ID: {complaint_id}) status has been updated to: <strong>{status}</strong></p>
            <p>Thank you for using TrackMyWaste!</p>
        </body>
    </html>
    """
    return send_email(user_email, subject, body)
