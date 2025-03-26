import logging
from email.utils import parsedate_to_datetime
from emailocr.attachment_processors import AttachmentProcessorFactory
from emailocr.database import Database
from emailocr.openai_utils import analyze_email, detect_duplicate
from emailocr.email_utils import connect_email_server, fetch_emails

class EmailProcessor:
    def __init__(self):
        self.db = Database()
        self.processed_hashes = set()
        self.similarity_threshold = 0.95  # For duplicate detection

    def process_attachments(self, msg):
        """
        Process attachments using the factory pattern.
        """
        extracted_text = ""
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                continue

            file_name = part.get_filename()
            if file_name:
                file_data = part.get_payload(decode=True)
                content_type = part.get_content_type()
                processor = AttachmentProcessorFactory.get_processor(content_type)
                if processor:
                    extracted_text += processor.process(file_data)
                else:
                    logging.warning(f"No processor found for content type: {content_type}")
        return extracted_text

    def process_email(self, msg):
        """
        Template method for processing an email.
        """
        email_data = self._extract_email_metadata(msg)
        attachment_text = self.process_attachments(msg)
        full_text = email_data['body'] + "\n" + attachment_text

        if detect_duplicate(full_text, self.processed_hashes, self.similarity_threshold):
            logging.info(f"Duplicate email detected: {email_data['subject']}")
            return None

        analysis = analyze_email(full_text)
        email_data.update({
            'analysis': analysis,
            'priority': analysis.get('priority', 'medium'),
            'requires_followup': 'yes' if analysis.get('multiple_requests') else 'no'
        })
        self.db.save_email(email_data)
        return email_data

    def _extract_email_metadata(self, msg):
        """
        Extract metadata (e.g., sender, subject, body) from the email.
        """
        email_data = {
            'from': msg.get('from', 'unknown'),
            'subject': msg.get('subject', 'No Subject'),
            'date': parsedate_to_datetime(msg.get('date', '')),
            'body': ""
        }

        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        email_data['body'] += part.get_payload(decode=True).decode(errors='ignore')
                    elif content_type == "text/html":
                        html_content = part.get_payload(decode=True).decode(errors='ignore')
                        email_data['body'] += html_content
            else:
                email_data['body'] = msg.get_payload(decode=True).decode(errors='ignore')
        except Exception as e:
            logging.error(f"Error extracting email body: {e}")

        return email_data

    def run(self):
        mail = connect_email_server()
        try:
            for email_msg in fetch_emails(mail):
                result = self.process_email(email_msg)
                if result:
                    logging.info(f"Processed email: {result['subject']}")
                    logging.info(f"Priority: {result['priority']}")
                    logging.info(f"Intent: {result['analysis'].get('primary_intent', 'unknown')}")
                    logging.info("-" * 50)
        except Exception as e:
            logging.error(f"Error during email processing: {e}")
        finally:
            mail.quit()
