from flask import Flask, render_template, request, jsonify
import random
import os
from difflib import SequenceMatcher

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Upgraded Knowledge Base: Mapping realistic variations to answers
jis_knowledge = {
    "admission process jiseee requirements rules how to join apply": [
        "JIS University offers undergraduate, postgraduate, and Ph.D. programs. You can apply online via the official website (jisuniversity.ac.in) or visit the campus admission cell.",
        "Admissions are based on merit and entrance exams like JISUEE, WBJEE, or JEE Main depending on the course."
    ],
    "campus life hostels clubs sports facilities fest canteen culture": [
        "The JIS University campus features modern labs, a well-stocked central library, digital classrooms, separate hostels for boys and girls, and sports facilities.",
        "Campus life is vibrant with various clubs (cultural, technical, sports) and our annual fest!"
    ],
    "examination routines dates semester schedules attendance 75 threshold": [
        "Semester examinations are conducted twice a year (Odd Semesters in Nov/Dec and Even Semesters in May/June). Check the student portal for exam routines.",
        "Make sure to maintain a minimum of 75% attendance to be eligible for university examinations."
    ],
    "courses streams btech bba mba pharmacy law subjects programs departments": [
        "JIS University offers programs in Engineering (B.Tech), Management (BBA/MBA), Pharmacy, Science, Law, and Hospitality management."
    ],
    "location address routing maps where is it located area route": [
        "JIS University is located at Agarpara, Kolkata, West Bengal (Near Kalyani Expressway)."
    ],
    "hi hello hey greetings good morning status": [
        "Hello! Welcome to CHATJIS. How can I help you regarding JIS University today?", 
        "Greetings from CHATJIS! Ask me anything about admissions, exams, or campus life."
    ],
    "bye goodbye exit thank you clear close": [
        "Thank you for using CHATJIS! Best of luck with your studies.", 
        "Goodbye! Have a great day at campus!"
    ]
}

def get_best_match(user_input):
    user_input = user_input.lower()
    best_ratio = 0.0
    best_match_key = None

    # Compare user phrase similarity against each keyword group
    for keyword_group in jis_knowledge:
        # Check if individual words exist, or calculate textual similarity ratio
        words = user_input.split()
        any_word_match = any(word in keyword_group for word in words if len(word) > 3)
        
        # Calculate matching score between 0.0 and 1.0
        ratio = SequenceMatcher(None, user_input, keyword_group).ratio()
        
        if any_word_match:
            ratio += 0.4  # Boost score if a specific core keyword matches

        if ratio > best_ratio:
            best_ratio = ratio
            best_match_key = keyword_group

    # If the match reliability is above a 30% confidence threshold, return response
    if best_ratio > 0.3 and best_match_key:
        return random.choice(jis_knowledge[best_match_key])
        
    return "I am still learning the various ways students ask questions about JIS University. Could you please rephrase your query or try words like 'admission', 'exams', or 'hostel'?"

# Route to serve our frontend UI webpage
@app.route('/')
def home():
    return render_template('index.html')

# API Endpoint for processing chat messages
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    bot_reply = get_best_match(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG', 'True') == 'True'
    app.run(debug=debug_mode, port=int(os.getenv('PORT', 5000)))