from flask import Flask, render_template_string, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:5000",
    "X-Title": "GameBrain AI"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GameBrain AI - Gaming Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .chat-wrapper {
            width: 100%;
            max-width: 900px;
            height: 85vh;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 28px 24px;
            text-align: center;
        }

        .chat-header h1 {
            font-size: 32px;
            font-weight: 700;
            color: white;
            margin-bottom: 8px;
        }

        .chat-header p {
            font-size: 18px;
            color: rgba(255, 255, 255, 0.9);
            font-weight: 500;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            background: #f7f9fc;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .message {
            display: flex;
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .user-message {
            justify-content: flex-end;
        }

        .bot-message {
            justify-content: flex-start;
        }

        .message-content {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            line-height: 1.5;
            word-wrap: break-word;
            font-size: 15px;
        }

        .user-message .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .bot-message .message-content {
            background: white;
            color: #2d3748;
            border: 1px solid #e2e8f0;
            border-bottom-left-radius: 4px;
        }

        .chat-input-container {
            padding: 20px 24px;
            background: white;
            border-top: 1px solid #e2e8f0;
        }

        .input-wrapper {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .chat-input {
            flex: 1;
            padding: 12px 20px;
            border: 2px solid #e2e8f0;
            border-radius: 30px;
            outline: none;
            font-size: 15px;
            transition: all 0.3s;
        }

        .chat-input:focus {
            border-color: #764ba2;
            box-shadow: 0 0 0 3px rgba(118, 75, 162, 0.1);
        }

        .send-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 28px;
            border-radius: 30px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .send-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .typing-indicator {
            display: none;
            padding: 10px 18px;
            background: white;
            border-radius: 18px;
            border: 1px solid #e2e8f0;
            width: fit-content;
            color: #718096;
            font-size: 14px;
        }

        .suggestions {
            padding: 12px 24px;
            background: #f7f9fc;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .suggestion-chip {
            background: white;
            border: 1px solid #e2e8f0;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
            color: #4a5568;
        }

        .suggestion-chip:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        @media (max-width: 640px) {
            .message-content {
                max-width: 85%;
            }

            .chat-header h1 {
                font-size: 24px;
            }
        }
    </style>
</head>
<body>
    <div class="chat-wrapper">
        <div class="chat-header">
            <h1>🎮 GameBrain AI</h1>
            <p>How can I help?</p>
        </div>

        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="message-content">
                    👋 Hey! I'm GameBrain AI. Ask me anything about Minecraft, Fortnite, or any other game!
                </div>
            </div>
        </div>

        <div class="suggestions">
            <div class="suggestion-chip" onclick="sendSuggestion('How to find diamonds in Minecraft?')">💎 How to find diamonds in Minecraft?</div>
            <div class="suggestion-chip" onclick="sendSuggestion('Best Fortnite building tips?')">🏗️ Best Fortnite building tips?</div>
            <div class="suggestion-chip" onclick="sendSuggestion('How to beat the Ender Dragon?')">🐉 How to beat the Ender Dragon?</div>
            <div class="suggestion-chip" onclick="sendSuggestion('What are good beginner games?')">🎯 What are good beginner games?</div>
        </div>

        <div class="chat-input-container">
            <div class="input-wrapper">
                <input type="text" id="userInput" class="chat-input" placeholder="Ask me anything about gaming..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()" class="send-button">Send →</button>
            </div>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const userInput = document.getElementById('userInput');

        function addMessage(content, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function showTyping() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message';
            typingDiv.id = 'typingIndicator';
            const contentDiv = document.createElement('div');
            contentDiv.className = 'typing-indicator';
            contentDiv.innerHTML = 'GameBrain is thinking...';
            contentDiv.style.display = 'block';
            typingDiv.appendChild(contentDiv);
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function hideTyping() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) indicator.remove();
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            addMessage(message, true);
            userInput.value = '';
            userInput.disabled = true;
            showTyping();

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });

                const data = await response.json();
                hideTyping();
                userInput.disabled = false;
                userInput.focus();

                if (data.success) {
                    addMessage(data.response, false);
                } else {
                    addMessage('Sorry, I encountered an error: ' + data.error, false);
                }
            } catch (error) {
                hideTyping();
                userInput.disabled = false;
                addMessage('Network error. Please check your connection.', false);
            }
        }

        function sendSuggestion(text) {
            userInput.value = text;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') sendMessage();
        }

        userInput.focus();
    </script>
</body>
</html>
"""


@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)


@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        print(f"📝 Question: {user_message}")

        response = requests.post(
            OPENROUTER_URL,
            headers=HEADERS,
            json={
                "model": "deepseek/deepseek-r1:free",  # ✅ Free model that actually works
                "messages": [
                    {
                        "role": "system",
                        "content": "You are GameBrain AI, a friendly and knowledgeable gaming assistant. Help gamers with strategies, tips, mechanics, and guides for games like Minecraft, Fortnite, League of Legends, CS:GO, Valorant, and others. Answer in a helpful, concise, and friendly manner. Keep responses clear and easy to understand."
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
        )

        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            print(f"✅ Response sent")
            return jsonify({'success': True, 'response': answer})
        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            print(f"❌ {error_msg}")
            return jsonify({'success': False, 'error': error_msg})

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    print("🚀 GameBrain AI is starting with OpenRouter API!")
    print("📍 Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)