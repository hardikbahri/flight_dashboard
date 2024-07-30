import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_via_yahoo(sender_email, app_password, recipient_email, subject, body):
    try:
        # Set up the SMTP server with SSL
        server = smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465)

        # Login to the server
        server.login(sender_email, app_password)
        
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Attach the email body
        msg.attach(MIMEText(body, 'plain'))
        
        # Send the email
        server.send_message(msg)
        server.quit()
        
        print(f"Email sent to {recipient_email}")
    
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

# Example usage
if __name__ == "__main__":
    sender_email = "your_yahoo_email@yahoo.com"  # Yahoo email address
    app_password = "your_app_specific_password"  # Use the app-specific password generated
    recipient_email = "recipient@example.com"
    subject = "Test Email"
    body = "This is a test email sent using Yahoo Mail."

    send_email_via_yahoo(sender_email, app_password, recipient_email, subject, body)
