import logging
from emailocr.email_processor import EmailProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    processor = EmailProcessor()
    processor.run()
