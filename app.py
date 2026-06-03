from flask import Flask, render_template, request, jsonify
import random
import json
import sqlite3
from difflib import SequenceMatcher

app = Flask(__name__)

DB_FILE = 'conversations.db'

# Function to initialize the database table
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_reply TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# 🔥 CRITICAL FIX: Run initialization at the top-level lifecycle 
# This ensures Render/Gunicorn sets up the database table correctly!
init_db()

# Function to save a chat interaction
def log_conversation(user_msg, bot_resp):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO logs (user_message, bot_reply) VALUES (?, ?)', (user_msg, bot_resp))
    conn.commit()
    conn.close()

# Function to read the knowledge base from our JSON file
def load_knowledge_base():
    with open('knowledge.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def get_best_match(user_input):
    user_input = user_input.lower()
    best_ratio = 0.0
    best_match_key = None
    
    jis_knowledge = load_knowledge_base()

    for keyword_group in jis_knowledge:
        words = user_input.split()
        any_word_match = any(word in keyword_group for word in words if len(word) > 3)
        ratio = SequenceMatcher(None, user_input, keyword_group).ratio()
        
        if any_word_match:
            ratio += 0.4

        if ratio > best_ratio:
            best_ratio = ratio
            best_match_key = keyword_group

    if best_ratio > 0.3 and best_match_key:
        return random.choice(jis_knowledge[best_match_key])
        
    return "I am still learning the various ways students ask questions about JIS University. Could you please rephrase your query or try words like 'admission', 'exams', or 'placement'?"

# Route to serve our frontend UI dashboard webpage
@app.route('/')
def home():
    return render_template('index.html')

# API Endpoint for processing incoming chat payloads
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    bot_reply = get_best_match(user_message)
    
    # Save conversation log automatically inside database record rows
    log_conversation(user_message, bot_reply)
    
    return jsonify({"reply": bot_reply})

# Secret administrative analytics console dashboard to monitor user activity
@app.route('/logs')
def view_logs():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, user_message, bot_reply, timestamp FROM logs ORDER BY id DESC')
        records = cursor.fetchall()
        conn.close()
        
        # In-line administrative styling blueprint
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>CHATJIS - Live Analytics Terminal</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 40px; background: #f8fafc; color: #0f172a; }
                h2 { color: #002147; font-weight: 700; margin-bottom: 20px; }
                table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
                th, td { padding: 15px 20px; text-align: left; border-bottom: 1px solid #e2e8f0; }
                th { background-color: #002147; color: white; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }
                tr:hover { background-color: #f1f5f9; }
                td { font-size: 15px; line-height: 1.5; }
                .timestamp { color: #64748b; font-size: 13px; }
            </style>
        </head>
        <body>
            <h2>📊 ChatJIS Live Analytics Log Stream</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>User Inquiry</th>
                    <th>Bot Transmission Response</th>
                    <th>Timestamp (UTC)</th>
                </tr>
        '''
        
        for row in records:
            html_content += f'''
                <tr>
                    <td>{row[0]}</td>
                    <td><strong>{row[1]}</strong></td>
                    <td>{row[2]}</td>
                    <td class="timestamp">{row[3]}</td>
                </tr>
            '''
            
        html_content += '''
            </table>
        </body>
        </html>
        '''
        return html_content
    except Exception as e:
        return f"Database Fetch Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, port=5000)