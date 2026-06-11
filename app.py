from flask import Flask, render_template, request, jsonify, Response
from functools import wraps
import json
import sqlite3
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv(override=True)

# Configure Gemini AI
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("WARNING: GEMINI_API_KEY not found in environment.")

app = Flask(__name__)

DB_FILE = 'conversations.db'

# Function to initialize the database table
def init_db():
    try:
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
    except sqlite3.Error as e:
        print(f"CRITICAL ERROR: Failed to initialize database: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# 🔥 CRITICAL FIX: Run initialization at the top-level lifecycle 
# This ensures Render/Gunicorn sets up the database table correctly!
init_db()

# Function to save a chat interaction
def log_conversation(user_msg, bot_resp):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO logs (user_message, bot_reply) VALUES (?, ?)', (user_msg, bot_resp))
        conn.commit()
    except sqlite3.Error as e:
        print(f"DATABASE ERROR (Logging): Could not save conversation. {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# Function to read the knowledge base from our JSON file
def load_knowledge_base():
    try:
        if not os.path.exists('knowledge.json'):
            print("WARNING: knowledge.json not found. Creating a default one.")
            default_kb = {"hi": ["Hello!"]}
            with open('knowledge.json', 'w', encoding='utf-8') as f:
                json.dump(default_kb, f)
            return default_kb
            
        with open('knowledge.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"JSON ERROR: The knowledge.json file is corrupted or improperly formatted: {e}")
        return {}
    except Exception as e:
        print(f"FILE ERROR: Could not read knowledge base: {e}")
        return {}

def get_best_match(user_input):
    try:
        jis_knowledge = load_knowledge_base()
        
        # Prepare the system prompt using the knowledge base
        system_instruction = (
            "You are CHATJIS, a helpful, professional AI assistant for JIS University. "
            "Use the following knowledge base to answer the user's questions accurately. "
            "If the user asks something completely unrelated to the university or general helpful tasks, politely guide them back. "
            "Knowledge Base:\n" + json.dumps(jis_knowledge, indent=2)
        )
        
        # Initialize the model
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )
        
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        import traceback
        print(f"Error generating AI response: {e}")
        traceback.print_exc()
        return f"AI Error: {str(e)}"

# Route to serve our frontend UI dashboard webpage
@app.route('/')
def home():
    return render_template('index.html')

# Route to serve the Chatbot interface
@app.route('/chatbot')
def chatbot():
    return render_template('chat.html')

# Internal Pages Routes
@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/admissions')
def admissions():
    return render_template('admissions.html')

@app.route('/campus')
def campus():
    return render_template('campus.html')

# API Endpoint for processing incoming chat payloads
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    bot_reply = get_best_match(user_message)
    
    # Save conversation log automatically inside database record rows
    log_conversation(user_message, bot_reply)
    
    return jsonify({"reply": bot_reply})

def check_auth(username, password):
    """Check if a username / password combination is valid."""
    admin_user = os.getenv("ADMIN_USERNAME", "admin")
    admin_pass = os.getenv("ADMIN_PASSWORD", "jisadmin123")
    return username == admin_user and password == admin_pass

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Secret administrative analytics console dashboard to monitor user activity
@app.route('/logs')
@requires_auth
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