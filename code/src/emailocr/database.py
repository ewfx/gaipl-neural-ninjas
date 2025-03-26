import sqlite3
import logging

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('emails.db', check_same_thread=False)
        self._initialize_database()

    def _initialize_database(self):
        with self.connection:
            self.connection.execute('''
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

    def save_email(self, email_data):
        try:
            with self.connection:
                self.connection.execute('''
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
