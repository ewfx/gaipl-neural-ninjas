import os
import poplib
import email
from email.utils import parsedate_to_datetime
import pytesseract
from PIL import Image
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import io
from dotenv import load_dotenv
import logging
from PyPDF2 import PdfReader
from docx import Document
import sqlite3

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmailProcessor:
    def __init__(self):
        self.processed_hashes = set()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.email_server = os.getenv('EMAIL_SERVER')
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.similarity_threshold = 0.95  # For duplicate detection
        openai.api_key = self.openai_api_key
        self.db_connection = sqlite3.connect('emails.db', check_same_thread=False)
        self._initialize_database()

    def _initialize_database(self):
        with self.db_connection:
            self.db_connection.execute('''
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT,
                    subject TEXT,
                    date TEXT,
                    body TEXT,
                    priority TEXT,
                    intent TEXT,
                    requires_followup TEXT
                )
            ''')

    def connect_email_server(self):
        try:
            self.mail = poplib.POP3_SSL(self.email_server)
            self.mail.user(self.email_user)
            self.mail.pass_(self.email_password)
        except Exception as e:
            logging.error(f"Error connecting to email server: {e}")
            raise

    def fetch_emails(self):
        try:
            _, messages, _ = self.mail.list()
            for msg_num in messages:
                _, msg_lines, _ = self.mail.retr(msg_num)
                msg_content = b'\r\n'.join(msg_lines).decode('utf-8')
                yield email.message_from_string(msg_content)
        except Exception as e:
            logging.error(f"Error fetching emails: {e}")

    def process_attachments(self, msg):
        extracted_text = ""
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue

            file_name = part.get_filename()
            if file_name:
                file_data = part.get_payload(decode=True)
                content_type = part.get_content_type()
                try:
                    if content_type.startswith('image/'):
                        extracted_text += self._process_image(file_data)
                    elif content_type == 'application/pdf':
                        extracted_text += self._process_pdf(file_data)
                    elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                        extracted_text += self._process_docx(file_data)
                    elif content_type == 'text/plain':
                        extracted_text += file_data.decode('utf-8')
                except Exception as e:
                    logging.warning(f"Failed to process attachment {file_name}: {e}")
        return extracted_text

    def _process_image(self, file_data):
        try:
            image = Image.open(io.BytesIO(file_data))
            return pytesseract.image_to_string(image) + "\n"
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            return ""

    def _process_pdf(self, file_data):
        try:
            pdf = PdfReader(io.BytesIO(file_data))
            return "\n".join([page.extract_text() for page in pdf.pages])
        except Exception as e:
            logging.error(f"Error processing PDF: {e}")
            return ""

    def _process_docx(self, file_data):
        try:
            doc = Document(io.BytesIO(file_data))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logging.error(f"Error processing DOCX: {e}")
            return ""

    def analyze_email(self, text):
        prompt = f"""Analyze this email and return JSON with:
- Primary intent (sales, support, billing, other)
- Priority (high, medium, low)
- Key entities (names, dates, amounts)
- Multiple requests (list of individual requests)
- Summary
- Sentiment (positive, neutral, negative)

Email: {text[:3000]}"""  # Truncate to fit context window

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return json.loads(response.choices[0].message['content'])
        except Exception as e:
            logging.error(f"Error analyzing email: {e}")
            return {}

    def detect_duplicate(self, content):
        try:
            embedding = openai.Embedding.create(
                input=content,
                model="text-embedding-ada-002"
            )['data'][0]['embedding']

            for existing in self.processed_hashes:
                if cosine_similarity([embedding], [existing])[0][0] > self.similarity_threshold:
                    return True
            self.processed_hashes.add(tuple(embedding))  # Store as tuple for hashability
            return False
        except Exception as e:
            logging.error(f"Error in duplicate detection: {e}")
            return False

    def save_to_database(self, email_data):
        try:
            with self.db_connection:
                self.db_connection.execute('''
                    INSERT INTO emails (sender, subject, date, body, priority, intent, requires_followup)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    email_data['from'],
                    email_data['subject'],
                    email_data['date'].isoformat(),
                    email_data['body'],
                    email_data['priority'],
                    email_data['analysis'].get('primary_intent', 'unknown'),
                    email_data['requires_followup']
                ))
        except Exception as e:
            logging.error(f"Error saving email to database: {e}")

    def process_email(self, msg):
        email_data = {
            'from': msg.get('from', 'unknown'),
            'subject': msg.get('subject', 'No Subject'),
            'date': parsedate_to_datetime(msg.get('date', '')),
            'body': "",
            'attachments': []
        }

        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        email_data['body'] += part.get_payload(decode=True).decode(errors='ignore')
                    elif content_type == "text/html":
                        html_content = part.get_payload(decode=True).decode(errors='ignore')
                        email_data['body'] += self.extract_html_content(html_content)
            else:
                email_data['body'] = msg.get_payload(decode=True).decode(errors='ignore')
        except Exception as e:
            logging.error(f"Error extracting email body: {e}")

        attachment_text = self.process_attachments(msg)
        full_text = email_data['body'] + "\n" + attachment_text

        if self.detect_duplicate(full_text):
            logging.info(f"Duplicate email detected: {email_data['subject']}")
            return None

        analysis = self.analyze_email(full_text)
        email_data.update({
            'analysis': analysis,
            'priority': analysis.get('priority', 'medium'),
            'requires_followup': 'yes' if analysis.get('multiple_requests') else 'no'
        })
        self.save_to_database(email_data)
        return email_data

    def run(self):
        self.connect_email_server()
        try:
            for email_msg in self.fetch_emails():
                result = self.process_email(email_msg)
                if result:
                    logging.info(f"Processed email: {result['subject']}")
                    logging.info(f"Priority: {result['priority']}")
                    logging.info(f"Intent: {result['analysis'].get('primary_intent', 'unknown')}")
                    logging.info("-" * 50)
        except Exception as e:
            logging.error(f"Error during email processing: {e}")
        finally:
            self.mail.quit()

if __name__ == "__main__":
    processor = EmailProcessor()
    processor.run()
