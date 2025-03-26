# 🚀 Email Classification and Data Extraction System

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Challenges](#challenges)
- [Future Enhancements](#future-enhancements)
- [Team](#team)

---

## 🎯 Introduction
This project automates email classification and data extraction using Generative AI and machine learning. It processes emails, extracts meaningful information from attachments, and classifies emails into categories like sales, support, and billing. The system also detects duplicate emails and stores processed data in a database for further analysis.

---

## 🎥 Demo
🔗 [Live Demo](#) (if applicable)  
📹 [Video Demo](#) (if applicable)  
🖼️ Screenshots:

![Screenshot 1](link-to-image)

---

## ✨ Features
- Automatically fetches emails from a POP3 server.
- Extracts text from attachments (PDF, DOCX, images, etc.).
- Classifies emails using OpenAI's GPT-3.5 model.
- Detects duplicate emails using embeddings and cosine similarity.
- Stores processed email data in an SQLite database.
- Provides a Flask-based API for querying and updating email data.

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```sh
git clone https://github.com/your-repo.git
cd your-repo
```

### 2. Install Dependencies
Ensure you have Python 3.8+ installed. Then, install the required packages:
```sh
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and add the following:
```
OPENAI_API_KEY=your_openai_api_key
EMAIL_SERVER=your_email_server
EMAIL_USER=your_email_user
EMAIL_PASSWORD=your_email_password
```

### 4. Initialize the Database
The database will be automatically created when you run the application for the first time.

### 5. Run the Email Processor
```sh
python code/src/emailocr.py
```

### 6. Start the Flask API
```sh
python code/src/app.py
```

### 7. Access the API
- **Get Emails**: `GET /emails`
- **Submit Feedback**: `POST /feedback`

---

## 🏗️ Tech Stack
- **Backend**: Python, Flask
- **Database**: SQLite
- **AI Models**: OpenAI GPT-3.5, OpenAI Embeddings
- **Libraries**:
  - Email Parsing: `email`, `poplib`
  - Attachment Processing: `PyPDF2`, `python-docx`, `pytesseract`
  - Database: `sqlite3`
  - Web Framework: `Flask`

---

## ⚙️ How It Works
1. **Email Fetching**: Connects to a POP3 server to fetch emails.
2. **Attachment Processing**: Extracts text from supported file types (PDF, DOCX, images, etc.).
3. **Classification**: Uses OpenAI GPT-3.5 to classify emails and extract key information.
4. **Duplicate Detection**: Compares email embeddings to detect duplicates.
5. **Database Storage**: Stores processed email data in an SQLite database.
6. **API**: Provides endpoints for querying and updating email data.

---

## 🚧 Challenges
- Handling diverse attachment formats and large files.
- Optimizing API usage to reduce costs and latency.
- Ensuring accurate duplicate detection with embeddings.

---

## 🚀 Future Enhancements
- Add support for more attachment types (e.g., `.xlsx`, `.csv`).
- Integrate with IMAP for real-time email fetching.
- Build a frontend dashboard for visualizing email data.
- Add sentiment analysis for email prioritization.

---

## 👥 Team
- **Your Name** - [GitHub](#) | [LinkedIn](#)
- **Teammate 2** - [GitHub](#) | [LinkedIn](#)