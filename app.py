from flask import Flask, render_template, request, jsonify
import random
import json
from difflib import SequenceMatcher

app = Flask(__name__)

# Function to read the knowledge base from our JSON file
def load_knowledge_base():
    with open('knowledge.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def get_best_match(user_input):
    user_input = user_input.lower()
    best_ratio = 0.0
    best_match_key = None
    
    # Dynamically load the dataset on every question
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    bot_reply = get_best_match(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    app.run(debug=True, port=5000)