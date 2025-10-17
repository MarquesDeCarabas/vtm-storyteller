from flask import Flask, request, render_template_string, jsonify, Response, stream_with_context
from openai import OpenAI
import os
import time
import json
import sqlite3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# OpenAI Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

client = OpenAI(api_key=API_KEY)

# Database initialization
def init_db():
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    # Character sheets table
    c.execute('''CREATE TABLE IF NOT EXISTS characters
                 (id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  clan TEXT,
                  generation INTEGER,
                  attributes TEXT,
                  disciplines TEXT,
                  backgrounds TEXT,
                  created_at TIMESTAMP,
                  updated_at TIMESTAMP)''')
    
    # System health logs table
    c.execute('''CREATE TABLE IF NOT EXISTS system_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TIMESTAMP,
                  level TEXT,
                  message TEXT,
                  details TEXT)''')
    
    # Campaigns table
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns
                 (id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  roll20_game_id TEXT,
                  discord_channel_id TEXT,
                  created_at TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

# Helper functions
def log_system_event(level, message, details=None):
    """Log system events to database"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    c.execute('''INSERT INTO system_logs (timestamp, level, message, details)
                 VALUES (?, ?, ?, ?)''',
              (datetime.now(), level, message, json.dumps(details) if details else None))
    conn.commit()
    conn.close()
    logger.info(f"{level}: {message}")

def get_or_create_thread(user_id="default"):
    """Get or create a conversation thread"""
    try:
        thread = client.beta.threads.create()
        log_system_event("INFO", f"Created new thread: {thread.id}")
        return thread.id
    except Exception as e:
        log_system_event("ERROR", "Failed to create thread", {"error": str(e)})
        raise

def wait_for_run_completion(thread_id, run_id, max_iterations=90):
    """Wait for the assistant run to complete with progress logging"""
    for i in range(max_iterations):
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            
            # Log progress every 10 seconds
            if i % 10 == 0 and i > 0:
                log_system_event("INFO", f"Waiting for response... {i} seconds elapsed", 
                               {"thread_id": thread_id, "run_id": run_id, "status": run.status})
            
            if run.status == "completed":
                log_system_event("INFO", "Assistant response completed", 
                               {"thread_id": thread_id, "elapsed_time": i})
                return run
            elif run.status in ["failed", "cancelled", "expired"]:
                log_system_event("ERROR", f"Run {run.status}", 
                               {"thread_id": thread_id, "run_id": run_id, "status": run.status})
                return None
            
            time.sleep(1)
        except Exception as e:
            log_system_event("ERROR", "Error checking run status", {"error": str(e)})
            raise
    
    log_system_event("WARNING", "Response timeout", {"thread_id": thread_id, "timeout": max_iterations})
    return None

# Routes

@app.route('/')
def home():
    """Main chat interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with SSE support"""
    try:
        user_message = request.json.get('message', '')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        log_system_event("INFO", "Received chat message", {"message": user_message[:100]})
        
        # Create thread and send message
        thread_id = get_or_create_thread()
        
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        
        # Wait for completion
        completed_run = wait_for_run_completion(thread_id, run.id)
        
        if not completed_run:
            log_system_event("ERROR", "Assistant run failed or timed out")
            return jsonify({
                "error": "The Storyteller is taking too long to respond. Please try again with a simpler question."
            }), 504
        
        # Get the response
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_message = messages.data[0].content[0].text.value
        
        log_system_event("INFO", "Chat response sent", {"response_length": len(assistant_message)})
        
        return jsonify({"response": assistant_message})
        
    except Exception as e:
        log_system_event("ERROR", "Chat error", {"error": str(e)})
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    """Stream chat responses using Server-Sent Events"""
    def generate():
        try:
            user_message = request.json.get('message', '')
            
            if not user_message:
                yield f"data: {json.dumps({'error': 'No message provided'})}\n\n"
                return
            
            # Send typing indicator
            yield f"data: {json.dumps({'type': 'typing', 'message': 'Storyteller is thinking...'})}\n\n"
            
            # Create thread and send message
            thread_id = get_or_create_thread()
            
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_message
            )
            
            # Run the assistant with streaming
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=ASSISTANT_ID
            )
            
            # Poll for completion and stream progress
            for i in range(90):
                run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
                
                if i % 5 == 0:
                    yield f"data: {json.dumps({'type': 'progress', 'seconds': i})}\n\n"
                
                if run_status.status == "completed":
                    messages = client.beta.threads.messages.list(thread_id=thread_id)
                    assistant_message = messages.data[0].content[0].text.value
                    
                    # Stream the response in chunks
                    words = assistant_message.split()
                    for j in range(0, len(words), 5):
                        chunk = ' '.join(words[j:j+5])
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk + ' '})}\n\n"
                        time.sleep(0.1)
                    
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return
                
                elif run_status.status in ["failed", "cancelled", "expired"]:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Assistant run failed'})}\n\n"
                    return
                
                time.sleep(1)
            
            yield f"data: {json.dumps({'type': 'error', 'message': 'Response timeout'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/character/<character_id>')
def view_character(character_id):
    """View character sheet"""
    try:
        conn = sqlite3.connect('vtm_storyteller.db')
        c = conn.cursor()
        c.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
        character = c.fetchone()
        conn.close()
        
        if not character:
            return jsonify({"error": "Character not found"}), 404
        
        character_data = {
            "id": character[0],
            "name": character[1],
            "clan": character[2],
            "generation": character[3],
            "attributes": json.loads(character[4]) if character[4] else {},
            "disciplines": json.loads(character[5]) if character[5] else {},
            "backgrounds": json.loads(character[6]) if character[6] else {},
            "created_at": character[7],
            "updated_at": character[8]
        }
        
        return render_template_string(CHARACTER_SHEET_TEMPLATE, character=character_data)
        
    except Exception as e:
        log_system_event("ERROR", "Error viewing character", {"character_id": character_id, "error": str(e)})
        return jsonify({"error": str(e)}), 500

@app.route('/character', methods=['POST'])
def create_character():
    """Create or update a character sheet"""
    try:
        data = request.json
        character_id = data.get('id', f"char_{int(time.time())}")
        
        conn = sqlite3.connect('vtm_storyteller.db')
        c = conn.cursor()
        
        c.execute('''INSERT OR REPLACE INTO characters 
                     (id, name, clan, generation, attributes, disciplines, backgrounds, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (character_id,
                   data.get('name'),
                   data.get('clan'),
                   data.get('generation'),
                   json.dumps(data.get('attributes', {})),
                   json.dumps(data.get('disciplines', {})),
                   json.dumps(data.get('backgrounds', {})),
                   datetime.now(),
                   datetime.now()))
        
        conn.commit()
        conn.close()
        
        log_system_event("INFO", "Character created/updated", {"character_id": character_id})
        
        return jsonify({"success": True, "character_id": character_id, "url": f"/character/{character_id}"})
        
    except Exception as e:
        log_system_event("ERROR", "Error creating character", {"error": str(e)})
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    """System health check endpoint"""
    try:
        # Check database connection
        conn = sqlite3.connect('vtm_storyteller.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM system_logs')
        log_count = c.fetchone()[0]
        
        # Get recent errors
        c.execute('''SELECT timestamp, message, details FROM system_logs 
                     WHERE level = "ERROR" 
                     ORDER BY timestamp DESC LIMIT 10''')
        recent_errors = [{"timestamp": row[0], "message": row[1], "details": row[2]} 
                        for row in c.fetchall()]
        
        conn.close()
        
        # Check OpenAI connection
        openai_status = "healthy"
        try:
            client.models.list()
        except:
            openai_status = "unhealthy"
        
        health_data = {
            "status": "healthy" if openai_status == "healthy" else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": "healthy",
                "openai_api": openai_status,
                "assistant": "configured" if ASSISTANT_ID else "not_configured"
            },
            "metrics": {
                "total_logs": log_count,
                "recent_errors_count": len(recent_errors)
            },
            "recent_errors": recent_errors
        }
        
        return jsonify(health_data)
        
    except Exception as e:
        log_system_event("ERROR", "Health check failed", {"error": str(e)})
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/roll20/webhook', methods=['POST'])
def roll20_webhook():
    """Webhook endpoint for Roll20 integration"""
    try:
        data = request.json
        log_system_event("INFO", "Roll20 webhook received", data)
        
        # Process Roll20 events (dice rolls, character updates, etc.)
        event_type = data.get('type')
        
        if event_type == 'dice_roll':
            # Handle dice roll events
            result = data.get('result')
            character = data.get('character')
            # Send to Discord or process in chat
            
        return jsonify({"success": True})
        
    except Exception as e:
        log_system_event("ERROR", "Roll20 webhook error", {"error": str(e)})
        return jsonify({"error": str(e)}), 500

# HTML Templates

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🧛 VTM Storyteller</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #1a0000 0%, #330000 100%);
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.8);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #8b0000;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
        }
        
        .header h1 {
            color: #cc0000;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        }
        
        .header p {
            color: #999;
            margin-top: 10px;
            font-style: italic;
        }
        
        .nav {
            background: rgba(0, 0, 0, 0.6);
            padding: 10px 20px;
            display: flex;
            gap: 20px;
            justify-content: center;
            border-bottom: 1px solid #8b0000;
        }
        
        .nav a {
            color: #cc0000;
            text-decoration: none;
            padding: 5px 15px;
            border-radius: 5px;
            transition: all 0.3s;
        }
        
        .nav a:hover {
            background: rgba(204, 0, 0, 0.2);
        }
        
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 900px;
            width: 100%;
            margin: 0 auto;
            padding: 20px;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            padding: 15px 20px;
            border-radius: 10px;
            max-width: 80%;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            background: rgba(139, 0, 0, 0.3);
            align-self: flex-end;
            border: 1px solid #8b0000;
        }
        
        .message.storyteller {
            background: rgba(0, 0, 0, 0.5);
            align-self: flex-start;
            border: 1px solid #444;
        }
        
        .message-header {
            font-weight: bold;
            margin-bottom: 8px;
            color: #cc0000;
        }
        
        .typing-indicator {
            display: none;
            padding: 15px 20px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            max-width: 200px;
            border: 1px solid #444;
        }
        
        .typing-indicator.active {
            display: block;
        }
        
        .typing-indicator span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #cc0000;
            margin: 0 2px;
            animation: typing 1.4s infinite;
        }
        
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
        
        .input-container {
            padding: 20px;
            background: rgba(0, 0, 0, 0.6);
            border-top: 2px solid #8b0000;
            display: flex;
            gap: 10px;
        }
        
        .input-container input {
            flex: 1;
            padding: 15px;
            border: 2px solid #8b0000;
            border-radius: 5px;
            background: rgba(0, 0, 0, 0.7);
            color: #e0e0e0;
            font-size: 16px;
        }
        
        .input-container input:focus {
            outline: none;
            border-color: #cc0000;
            box-shadow: 0 0 10px rgba(204, 0, 0, 0.3);
        }
        
        .input-container button {
            padding: 15px 30px;
            background: #8b0000;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .input-container button:hover {
            background: #cc0000;
            box-shadow: 0 0 15px rgba(204, 0, 0, 0.5);
        }
        
        .input-container button:disabled {
            background: #555;
            cursor: not-allowed;
        }
        
        .status-bar {
            padding: 5px 20px;
            background: rgba(0, 0, 0, 0.8);
            color: #666;
            font-size: 12px;
            text-align: center;
        }
        
        .status-bar.online {
            color: #0c0;
        }
        
        .status-bar.error {
            color: #c00;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧛 VTM Storyteller</h1>
        <p>Vampire: The Masquerade 5th Edition AI Game Master</p>
    </div>
    
    <div class="nav">
        <a href="/">Chat</a>
        <a href="/health">System Status</a>
        <a href="#" onclick="showCharacterForm()">Create Character</a>
    </div>
    
    <div class="status-bar" id="statusBar">System Online</div>
    
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message storyteller">
                <div class="message-header">Storyteller</div>
                <div>Welcome, Kindred. I am your Storyteller for tonight's chronicle. Tell me about your character, or ask me to begin a new story in the World of Darkness...</div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            <span></span><span></span><span></span>
        </div>
        
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Enter your message..." />
            <button id="sendButton" onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <script>
        const messagesContainer = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const typingIndicator = document.getElementById('typingIndicator');
        const statusBar = document.getElementById('statusBar');
        
        let useSSE = true; // Use Server-Sent Events for streaming
        
        // Check system health on load
        checkHealth();
        setInterval(checkHealth, 60000); // Check every minute
        
        async function checkHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                if (data.status === 'healthy') {
                    statusBar.textContent = 'System Online';
                    statusBar.className = 'status-bar online';
                } else {
                    statusBar.textContent = 'System Degraded';
                    statusBar.className = 'status-bar error';
                }
            } catch (error) {
                statusBar.textContent = 'System Offline';
                statusBar.className = 'status-bar error';
            }
        }
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addMessage('user', 'You', message);
            messageInput.value = '';
            
            // Disable input while processing
            sendButton.disabled = true;
            messageInput.disabled = true;
            typingIndicator.classList.add('active');
            
            if (useSSE) {
                await sendMessageSSE(message);
            } else {
                await sendMessageHTTP(message);
            }
            
            // Re-enable input
            sendButton.disabled = false;
            messageInput.disabled = false;
            typingIndicator.classList.remove('active');
            messageInput.focus();
        }
        
        async function sendMessageSSE(message) {
            const eventSource = new EventSource('/chat/stream');
            let responseText = '';
            let messageElement = null;
            
            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'typing') {
                    // Already showing typing indicator
                } else if (data.type === 'chunk') {
                    if (!messageElement) {
                        messageElement = addMessage('storyteller', 'Storyteller', '');
                    }
                    responseText += data.content;
                    messageElement.querySelector('div:last-child').textContent = responseText;
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                } else if (data.type === 'done') {
                    eventSource.close();
                } else if (data.type === 'error') {
                    eventSource.close();
                    addMessage('storyteller', 'Storyteller', 'Error: ' + data.message);
                }
            };
            
            eventSource.onerror = function() {
                eventSource.close();
                if (!messageElement) {
                    addMessage('storyteller', 'Storyteller', 'Error: Connection lost. Please try again.');
                }
            };
            
            // Send the message
            fetch('/chat/stream', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            });
        }
        
        async function sendMessageHTTP(message) {
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                
                const data = await response.json();
                
                if (data.error) {
                    addMessage('storyteller', 'Storyteller', 'Error: ' + data.error);
                } else {
                    addMessage('storyteller', 'Storyteller', data.response);
                }
            } catch (error) {
                addMessage('storyteller', 'Storyteller', 'Error: ' + error.message);
            }
        }
        
        function addMessage(type, sender, text) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = `
                <div class="message-header">${sender}</div>
                <div>${text}</div>
            `;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            return messageDiv;
        }
        
        function showCharacterForm() {
            alert('Character creation form coming soon!');
        }
        
        // Allow Enter key to send message
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
'''

CHARACTER_SHEET_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ character.name }} - Character Sheet</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #1a0000 0%, #330000 100%);
            color: #e0e0e0;
            padding: 20px;
        }
        
        .sheet-container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #8b0000;
            border-radius: 10px;
            padding: 30px;
        }
        
        h1 {
            color: #cc0000;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .section {
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(139, 0, 0, 0.1);
            border-radius: 5px;
        }
        
        .section h2 {
            color: #cc0000;
            border-bottom: 1px solid #8b0000;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        
        .field {
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
        }
        
        .field label {
            font-weight: bold;
            color: #999;
        }
        
        .field value {
            color: #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="sheet-container">
        <h1>{{ character.name }}</h1>
        
        <div class="section">
            <h2>Basic Information</h2>
            <div class="field">
                <label>Clan:</label>
                <value>{{ character.clan }}</value>
            </div>
            <div class="field">
                <label>Generation:</label>
                <value>{{ character.generation }}</value>
            </div>
        </div>
        
        <div class="section">
            <h2>Attributes</h2>
            {% for attr, value in character.attributes.items() %}
            <div class="field">
                <label>{{ attr }}:</label>
                <value>{{ value }}</value>
            </div>
            {% endfor %}
        </div>
        
        <div class="section">
            <h2>Disciplines</h2>
            {% for disc, level in character.disciplines.items() %}
            <div class="field">
                <label>{{ disc }}:</label>
                <value>{{ level }}</value>
            </div>
            {% endfor %}
        </div>
        
        <div class="section">
            <h2>Backgrounds</h2>
            {% for bg, value in character.backgrounds.items() %}
            <div class="field">
                <label>{{ bg }}:</label>
                <value>{{ value }}</value>
            </div>
            {% endfor %}
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/" style="color: #cc0000; text-decoration: none;">← Back to Chat</a>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

