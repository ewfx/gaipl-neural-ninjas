from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

@app.route('/emails', methods=['GET'])
def get_emails():
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emails')
    emails = cursor.fetchall()
    conn.close()
    return jsonify(emails)

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    email_id = data['id']
    feedback = data['feedback']
    # Update feedback in the database
    processor = EmailProcessor()
    processor.update_feedback(email_id, feedback)
    return jsonify({'status': 'success'})

@app.route('/')
def dashboard():
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emails')
    emails = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', emails=emails)

if __name__ == '__main__':
    app.run(debug=True)
