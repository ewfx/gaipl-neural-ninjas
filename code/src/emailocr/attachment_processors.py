import logging
import io
from PIL import Image
from PyPDF2 import PdfReader
from docx import Document
import pytesseract

class AttachmentProcessorFactory:
    @staticmethod
    def get_processor(content_type):
        if content_type.startswith('image/'):
            return ImageProcessor()
        elif content_type == 'application/pdf':
            return PDFProcessor()
        elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return DOCXProcessor()
        elif content_type == 'text/plain':
            return TextProcessor()
        else:
            return None

class BaseAttachmentProcessor:
    def process(self, file_data):
        raise NotImplementedError("Subclasses must implement the process method.")

class ImageProcessor(BaseAttachmentProcessor):
    def process(self, file_data):
        try:
            image = Image.open(io.BytesIO(file_data))
            return pytesseract.image_to_string(image) + "\n"
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            return ""

class PDFProcessor(BaseAttachmentProcessor):
    def process(self, file_data):
        try:
            pdf = PdfReader(io.BytesIO(file_data))
            return "\n".join([page.extract_text() for page in pdf.pages])
        except Exception as e:
            logging.error(f"Error processing PDF: {e}")
            return ""

class DOCXProcessor(BaseAttachmentProcessor):
    def process(self, file_data):
        try:
            doc = Document(io.BytesIO(file_data))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logging.error(f"Error processing DOCX: {e}")
            return ""

class TextProcessor(BaseAttachmentProcessor):
    def process(self, file_data):
        try:
            return file_data.decode('utf-8') + "\n"
        except Exception as e:
            logging.error(f"Error processing text file: {e}")
            return ""
