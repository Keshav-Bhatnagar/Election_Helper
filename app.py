import os
import requests
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_CIVIC_API_KEY = os.getenv("GOOGLE_CIVIC_API_KEY")

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/civic', methods=['GET'])
def civic_lookup():
    address = request.args.get('address')
    if not address:
        return jsonify({"error": "Address is required"}), 400

    if not GOOGLE_CIVIC_API_KEY or GOOGLE_CIVIC_API_KEY == 'your_google_civic_api_key_here':
        # Return mock data if no key is configured
        is_india = 'india' in address.lower()
        mock_address = { "locationName": "Delhi Public School (Mock)", "line1": "Mathura Road", "city": "New Delhi", "state": "DL", "zip": "110003" } if is_india else { "locationName": "Community Center (Mock)", "line1": "123 Main St", "city": "Anytown", "state": "ST", "zip": "12345" }
        
        return jsonify({
            "mock": True, 
            "message": "Google Civic API key is missing. Showing mock data. Note: The real Google Civic API only supports U.S. elections.",
            "election": { "name": "General Election (Mock)", "electionDay": "2026-11-03" },
            "pollingLocations": [{
                "address": mock_address,
                "pollingHours": "7:00 AM - 6:00 PM"
            }],
            "representatives": [
                {"office": "President (Mock)" if is_india else "Governor (Mock)", "official": "Jane Doe"}
            ]
        })

    # Fetch voter info (Polling locations, upcoming elections, contests)
    voter_url = f"https://www.googleapis.com/civicinfo/v2/voterinfo?address={address}&key={GOOGLE_CIVIC_API_KEY}"
    voter_response = requests.get(voter_url)
    
    # Fetch representatives
    rep_url = f"https://www.googleapis.com/civicinfo/v2/representatives?address={address}&key={GOOGLE_CIVIC_API_KEY}"
    rep_response = requests.get(rep_url)
    
    if voter_response.status_code != 200 and rep_response.status_code != 200:
        error_details = voter_response.json() if voter_response.status_code != 200 else rep_response.json()
        hint = " Note: Google Civic API only supports U.S. addresses." if voter_response.status_code == 400 else ""
        return jsonify({"error": f"Failed to fetch civic data.{hint}", "details": error_details}), 400

    voter_data = voter_response.json() if voter_response.status_code == 200 else {}
    rep_data = rep_response.json() if rep_response.status_code == 200 else {}

    # Extract representatives
    reps = []
    if 'offices' in rep_data and 'officials' in rep_data:
        for office in rep_data['offices']:
            for official_idx in office.get('officialIndices', []):
                official = rep_data['officials'][official_idx]
                reps.append({"office": office['name'], "official": official['name']})

    return jsonify({
        "election": voter_data.get('election', {}),
        "pollingLocations": voter_data.get('pollingLocations', []),
        "representatives": reps
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    
    if not messages:
        return jsonify({"error": "Messages are required"}), 400

    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == 'your_anthropic_api_key_here':
        # Return mock data if no key is configured
        import random
        mock_replies = [
            "Voter registration deadlines vary by state. Some allow same-day registration, while others require it up to 30 days before the election. Check your state's official election website.",
            "Risk-limiting audits are manual hand counts of a statistical sample of paper ballots to ensure the machine tally is correct. It's a key security measure.",
            "Provisional ballots are used when a voter's eligibility is uncertain at the polling place. They are kept separate and only counted once officials verify the voter is eligible."
        ]
        return jsonify({"reply": random.choice(mock_replies)})

    # Anthropic API format
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Prepend the system prompt to messages if needed, or pass it directly.
    # The client will send the full messages array. We assume the client handles the system prompt correctly.
    # Wait, the Anthropic Messages API expects 'system' as a top level parameter and 'messages' to be alternating user/assistant.
    
    # We'll extract the system message from the array if it exists.
    system_prompt = "You are a nonpartisan election education assistant. Answer questions about the US voting process, registration, and election security objectively. Keep answers under 100 words."
    user_messages = []
    
    for msg in messages:
        if msg['role'] == 'system':
            system_prompt = msg['content']
        else:
            user_messages.append(msg)

    payload = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": 300,
        "system": system_prompt,
        "messages": user_messages
    }

    response = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to communicate with AI", "details": response.json()}), response.status_code
        
    response_data = response.json()
    reply = response_data['content'][0]['text']
    
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
