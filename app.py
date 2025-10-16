#!/usr/bin/env python3
"""
VTM Storyteller - Flask Web Application (Improved for Better Response Handling)
"""

from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI
import os
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)

# OpenAI Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
client = OpenAI(api_key=API_KEY)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>VTM Storyteller</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #1a0000 0%, #2d0a0a 100%);
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            background: rgba(0,0,0,0.8);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #8b0000;
        }
        h1 {
            color: #dc143c;
            font-size: 2.5em;
            text-shadow: 0 0 10px rgba(220, 20, 60, 0.5);
        }
        .subtitle {
            color: #999;
            font-style: italic;
            margin-top: 5px;
        }
        #chat-container {
            flex: 1;
            max-width: 900px;
            width: 100%;
            margin: 20px auto;
            padding: 20px;
            overflow-y: auto;
        }
        .message {
            margin: 15px 0;
            padding: 15px;
            border-radius: 10px;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user-message {
            background: rgba(139, 0, 0, 0.3);
            border-left: 4px solid #dc143c;
            margin-left: 50px;
        }
        .assistant-message {
            background: rgba(0, 0, 0, 0.5);
            border-left: 4px solid #666;
            margin-right: 50px;
        }
        .message-label {
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 0.9em;
        }
        .user-message .message-label { color: #dc143c; }
        .assistant-message .message-label { color: #999; }
        #input-container {
            background: rgba(0,0,0,0.8);
            padding: 20px;
            border-top: 2px solid #8b0000;
        }
        #input-form {
            max-width: 900px;
            margin: 0 auto;
            display: flex;
            gap: 10px;
        }
        #message-input {
            flex: 1;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border: 1px solid #666;
            border-radius: 5px;
            color: #e0e0e0;
            font-size: 16px;
        }
        #message-input:focus {
            outline: none;
            border-color: #dc143c;
            box-shadow: 0 0 10px rgba(220, 20, 60, 0.3);
        }
        button {
            padding: 15px 30px;
            background: #8b0000;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        button:hover {
            background: #dc143c;
            box-shadow: 0 0 15px rgba(220, 20, 60, 0.5);
        }
        button:disabled {
            background: #444;
            cursor: not-allowed;
        }
        .loading {
            text-align: center;
            color: #999;
            font-style: italic;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-left: 4px solid #666;
            margin: 15px 50px 15px 0;
            border-radius: 10px;
        }
        .loading-icon {
            font-size: 24px;
            margin-bottom: 10px;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .loading-text {
            font-size: 14px;
            margin-top: 10px;
        }
        .loading-subtext {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <header>
        <h1>🧛 VTM Storyteller</h1>
        <div class="subtitle">Vampire: The Masquerade 5th Edition AI Game Master</div>
    </header>
    
    <div id="chat-container"></div>
    
    <div id="input-container">
        <form id="input-form">
            <input type="text" id="message-input" placeholder="Enter your message..." autocomplete="off" required>
            <button type="submit" id="send-button">Send</button>
        </form>
    </div>

    <script>
        let threadId = null;
        const chatContainer = document.getElementById('chat-container');
        const inputForm = document.getElementById('input-form');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');

        function addMessage(content, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
            messageDiv.innerHTML = `
                <div class="message-label">${isUser ? 'You' : 'Storyteller'}</div>
                <div>${content.replace(/\\n/g, '<br>')}</div>
            `;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showLoading() {
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'loading';
            loadingDiv.id = 'loading';
            loadingDiv.innerHTML = `
                <div class="loading-icon">⏳</div>
                <div class="loading-text">The Storyteller is consulting the ancient texts...</div>
                <div class="loading-subtext">This may take up to 90 seconds for complex queries</div>
            `;
            chatContainer.appendChild(loadingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function hideLoading() {
            const loadingDiv = document.getElementById('loading');
            if (loadingDiv) loadingDiv.remove();
        }

        inputForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = messageInput.value.trim();
            if (!message) return;

            addMessage(message, true);
            messageInput.value = '';
            sendButton.disabled = true;
            showLoading();

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, thread_id: threadId })
                });

                const data = await response.json();
                hideLoading();

                if (data.error) {
                    addMessage(`Error: ${data.error}`, false);
                } else {
                    threadId = data.thread_id;
                    addMessage(data.response, false);
                }
            } catch (error) {
                hideLoading();
                addMessage(`Error: ${error.message}`, false);
            } finally {
                sendButton.disabled = false;
                messageInput.focus();
            }
        });

        // Initial message
        addMessage("Welcome, Kindred. I am your Storyteller for tonight's chronicle. Tell me about your character, or ask me to begin a new story in the World of Darkness...", false);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    thread_id = data.get('thread_id')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        # Create thread if needed
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id
            print(f"[INFO] Created new thread: {thread_id}")
        
        # Add user message
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
        print(f"[INFO] Added user message to thread {thread_id}")
        
        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        print(f"[INFO] Started run {run.id} with status: {run.status}")
        
        # Wait for completion (increased timeout to 90 seconds)
        max_iterations = 90
        iteration = 0
        
        while run.status != "completed" and iteration < max_iterations:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            iteration += 1
            
            # Log progress every 10 seconds
            if iteration % 10 == 0:
                print(f"[INFO] Run {run.id} status: {run.status} (iteration {iteration}/{max_iterations})")
            
            if run.status == "failed":
                print(f"[ERROR] Run {run.id} failed")
                return jsonify({"error": "Assistant run failed"}), 500
        
        if run.status != "completed":
            print(f"[WARNING] Run {run.id} did not complete within {max_iterations} seconds. Final status: {run.status}")
            return jsonify({"error": f"Request timeout. The Storyteller is taking longer than expected. Please try again."}), 504
        
        # Get response
        messages = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
        response_text = messages.data[0].content[0].text.value
        print(f"[INFO] Response generated successfully (length: {len(response_text)} chars)")
        
        return jsonify({
            "response": response_text,
            "thread_id": thread_id
        })
    
    except Exception as e:
        print(f"[ERROR] Exception in chat endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

