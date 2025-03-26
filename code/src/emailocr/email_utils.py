import poplib
import email
import logging

def connect_email_server():
    try:
        mail = poplib.POP3_SSL(os.getenv('EMAIL_SERVER'))
        mail.user(os.getenv('EMAIL_USER'))
        mail.pass_(os.getenv('EMAIL_PASSWORD'))
        return mail
    except Exception as e:
        logging.error(f"Error connecting to email server: {e}")
        raise

def fetch_emails(mail):
    try:
        _, messages, _ = mail.list()
        for msg_num in messages:
            _, msg_lines, _ = mail.retr(msg_num)
            msg_content = b'\r\n'.join(msg_lines).decode('utf-8')
            yield email.message_from_string(msg_content)
    except Exception as e:
        logging.error(f"Error fetching emails: {e}")
