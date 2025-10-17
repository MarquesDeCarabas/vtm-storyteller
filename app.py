# VTM Storyteller - Enhanced with Hybrid Character System
# This version includes:
# - Demiplane character linking
# - Custom character creation and sheets
# - Advanced dice roller with Hunger mechanics
# - Character-aware Storyteller AI

from flask import Flask, render_template_string, request, jsonify, Response
from openai import OpenAI
import os
import sqlite3
import json
from datetime import datetime
import random
import re

app = Flask(__name__)

# OpenAI Configuration
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Database setup
def init_db():
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    # Existing tables
    c.execute('''CREATE TABLE IF NOT EXISTS characters
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  name TEXT,
                  clan TEXT,
                  generation INTEGER,
                  attributes TEXT,
                  skills TEXT,
                  disciplines TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS health_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  component TEXT,
                  status TEXT,
                  details TEXT)''')
    
    # New table for Demiplane character links
    c.execute('''CREATE TABLE IF NOT EXISTS demiplane_links
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT NOT NULL,
                  character_id TEXT NOT NULL,
                  demiplane_url TEXT NOT NULL,
                  character_name TEXT,
                  clan TEXT,
                  predator_type TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Enhanced characters table for custom sheets
    c.execute('''CREATE TABLE IF NOT EXISTS character_sheets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT NOT NULL,
                  name TEXT NOT NULL,
                  clan TEXT,
                  predator_type TEXT,
                  generation INTEGER DEFAULT 13,
                  sire TEXT,
                  concept TEXT,
                  chronicle TEXT,
                  ambition TEXT,
                  desire TEXT,
                  attributes JSON NOT NULL,
                  skills JSON NOT NULL,
                  disciplines JSON NOT NULL,
                  health INTEGER DEFAULT 3,
                  willpower INTEGER DEFAULT 3,
                  humanity INTEGER DEFAULT 7,
                  hunger INTEGER DEFAULT 1,
                  blood_potency INTEGER DEFAULT 0,
                  experience INTEGER DEFAULT 0,
                  merits JSON,
                  flaws JSON,
                  equipment JSON,
                  notes TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Dice roll history
    c.execute('''CREATE TABLE IF NOT EXISTS dice_rolls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  character_id INTEGER,
                  pool_size INTEGER,
                  hunger_dice INTEGER,
                  results JSON,
                  successes INTEGER,
                  critical BOOLEAN,
                  messy_critical BOOLEAN,
                  bestial_failure BOOLEAN,
                  context TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

init_db()

# Conversation history storage
conversation_histories = {}

# System prompt for VTM Storyteller
SYSTEM_PROMPT = """You are an expert Storyteller for Vampire: The Masquerade 5th Edition. You are knowledgeable about:
- All VTM 5e clans, disciplines, and mechanics
- The World of Darkness lore and setting
- Character creation and development
- Running engaging chronicles
- The Hunger system and dice mechanics

You should:
- Be immersive and atmospheric in your descriptions
- Use gothic and noir themes
- Reference VTM lore accurately
- Help players create compelling characters
- Guide gameplay with dramatic storytelling
- Explain mechanics when needed
- Be supportive and encouraging

When a player has a linked character, you can reference their stats, clan abilities, and current status to make the game more immersive."""

def get_conversation_history(user_id):
    """Get or create conversation history for a user"""
    if user_id not in conversation_histories:
        conversation_histories[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    return conversation_histories[user_id]

def get_character_context(user_id):
    """Get character information to provide context to the AI"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    # Check for Demiplane linked character
    c.execute('''SELECT character_name, clan, predator_type, demiplane_url 
                 FROM demiplane_links 
                 WHERE user_id = ? 
                 ORDER BY updated_at DESC LIMIT 1''', (user_id,))
    demiplane_char = c.fetchone()
    
    # Check for custom character
    c.execute('''SELECT name, clan, predator_type, attributes, skills, hunger, humanity 
                 FROM character_sheets 
                 WHERE user_id = ? 
                 ORDER BY updated_at DESC LIMIT 1''', (user_id,))
    custom_char = c.fetchone()
    
    conn.close()
    
    context = ""
    if demiplane_char:
        context += f"\n\n[Player's Character (Demiplane): {demiplane_char[0]}, {demiplane_char[1]} {demiplane_char[2]}]"
    elif custom_char:
        context += f"\n\n[Player's Character: {custom_char[0]}, {custom_char[1]} {custom_char[2]}, Hunger: {custom_char[5]}, Humanity: {custom_char[6]}]"
    
    return context

# Dice rolling mechanics
def roll_dice(pool_size, hunger=0):
    """
    Roll VTM 5e dice pool with Hunger mechanics
    Returns: {
        'normal_dice': [...],
        'hunger_dice': [...],
        'successes': int,
        'critical': bool,
        'messy_critical': bool,
        'bestial_failure': bool
    }
    """
    normal_count = pool_size - hunger
    normal_dice = [random.randint(1, 10) for _ in range(max(0, normal_count))]
    hunger_dice = [random.randint(1, 10) for _ in range(hunger)]
    
    all_dice = normal_dice + hunger_dice
    successes = sum(1 for d in all_dice if d >= 6)
    
    # Count 10s for criticals
    normal_tens = sum(1 for d in normal_dice if d == 10)
    hunger_tens = sum(1 for d in hunger_dice if d == 10)
    total_tens = normal_tens + hunger_tens
    
    # Critical win: pairs of 10s add 4 successes total
    pairs_of_tens = total_tens // 2
    critical = pairs_of_tens > 0
    
    # Messy critical: at least one hunger die shows 10 in a critical
    messy_critical = critical and hunger_tens > 0
    
    # Bestial failure: no successes and at least one hunger die shows 1
    hunger_ones = sum(1 for d in hunger_dice if d == 1)
    bestial_failure = successes == 0 and hunger_ones > 0
    
    return {
        'normal_dice': normal_dice,
        'hunger_dice': hunger_dice,
        'successes': successes,
        'critical': critical,
        'messy_critical': messy_critical,
        'bestial_failure': bestial_failure,
        'total_tens': total_tens,
        'pairs': pairs_of_tens
    }

# API Endpoints

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """System health check"""
    try:
        # Check database
        conn = sqlite3.connect('vtm_storyteller.db')
        conn.close()
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    # Check OpenAI API
    try:
        client.models.list()
        api_status = "healthy"
    except:
        api_status = "unhealthy"
    
    # Get recent error count
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM health_logs WHERE status='error' AND timestamp > datetime('now', '-1 hour')")
    recent_errors = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM health_logs")
    total_logs = c.fetchone()[0]
    conn.close()
    
    overall_status = "healthy" if db_status == "healthy" and api_status == "healthy" else "degraded"
    
    return jsonify({
        "status": overall_status,
        "components": {
            "database": db_status,
            "openai_api": api_status
        },
        "metrics": {
            "recent_errors_count": recent_errors,
            "total_logs": total_logs
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with character context"""
    data = request.json
    user_message = data.get('message', '')
    user_id = data.get('user_id', 'default')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        # Get conversation history
        history = get_conversation_history(user_id)
        
        # Add character context if available
        char_context = get_character_context(user_id)
        
        # Add user message with character context
        full_message = user_message + char_context
        history.append({"role": "user", "content": full_message})
        
        # Keep only last 20 messages to avoid token limits
        if len(history) > 21:  # 1 system + 20 messages
            history = [history[0]] + history[-20:]
        
        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=history,
            max_tokens=1000,
            temperature=0.8
        )
        
        assistant_message = response.choices[0].message.content
        history.append({"role": "assistant", "content": assistant_message})
        
        return jsonify({"response": assistant_message})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/roll', methods=['POST'])
def roll():
    """Handle dice rolls"""
    data = request.json
    pool_size = data.get('pool', 0)
    hunger = data.get('hunger', 0)
    user_id = data.get('user_id', 'default')
    character_id = data.get('character_id')
    context = data.get('context', '')
    
    if pool_size < 1:
        return jsonify({"error": "Pool size must be at least 1"}), 400
    
    if hunger > pool_size:
        return jsonify({"error": "Hunger dice cannot exceed pool size"}), 400
    
    # Roll the dice
    result = roll_dice(pool_size, hunger)
    
    # Store in database
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    c.execute('''INSERT INTO dice_rolls 
                 (user_id, character_id, pool_size, hunger_dice, results, successes, 
                  critical, messy_critical, bestial_failure, context)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, character_id, pool_size, hunger, json.dumps(result), 
               result['successes'], result['critical'], result['messy_critical'],
               result['bestial_failure'], context))
    conn.commit()
    conn.close()
    
    return jsonify(result)

@app.route('/character/link', methods=['POST'])
def link_demiplane_character():
    """Link a Demiplane character"""
    data = request.json
    user_id = data.get('user_id', 'default')
    demiplane_url = data.get('demiplane_url', '')
    
    if not demiplane_url:
        return jsonify({"error": "No Demiplane URL provided"}), 400
    
    # Extract character ID from URL
    match = re.search(r'/character-sheet/([a-f0-9-]+)', demiplane_url)
    if not match:
        return jsonify({"error": "Invalid Demiplane URL"}), 400
    
    character_id = match.group(1)
    
    # Store in database
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    c.execute('''INSERT INTO demiplane_links 
                 (user_id, character_id, demiplane_url, character_name, clan, predator_type)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (user_id, character_id, demiplane_url, 
               data.get('name', 'Unknown'), data.get('clan', 'Unknown'), 
               data.get('predator_type', 'Unknown')))
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True,
        "character_id": character_id,
        "message": "Character linked successfully"
    })

@app.route('/character/create', methods=['POST'])
def create_character():
    """Create a custom character"""
    data = request.json
    user_id = data.get('user_id', 'default')
    
    required_fields = ['name', 'clan', 'attributes', 'skills', 'disciplines']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    c.execute('''INSERT INTO character_sheets 
                 (user_id, name, clan, predator_type, concept, attributes, skills, disciplines,
                  health, willpower, humanity, hunger, blood_potency)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, data['name'], data['clan'], data.get('predator_type', ''),
               data.get('concept', ''), json.dumps(data['attributes']), 
               json.dumps(data['skills']), json.dumps(data['disciplines']),
               data.get('health', 3), data.get('willpower', 3), 
               data.get('humanity', 7), data.get('hunger', 1),
               data.get('blood_potency', 0)))
    character_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True,
        "character_id": character_id,
        "message": "Character created successfully"
    })

@app.route('/character/<int:character_id>', methods=['GET'])
def get_character(character_id):
    """Get character details"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    c.execute('SELECT * FROM character_sheets WHERE id = ?', (character_id,))
    char = c.fetchone()
    conn.close()
    
    if not char:
        return jsonify({"error": "Character not found"}), 404
    
    return jsonify({
        "id": char[0],
        "name": char[2],
        "clan": char[3],
        "predator_type": char[4],
        "attributes": json.loads(char[7]),
        "skills": json.loads(char[8]),
        "disciplines": json.loads(char[9]),
        "health": char[10],
        "willpower": char[11],
        "humanity": char[12],
        "hunger": char[13],
        "blood_potency": char[14]
    })

@app.route('/character/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    """Update character"""
    data = request.json
    
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    # Build update query dynamically
    updates = []
    values = []
    
    updatable_fields = ['name', 'health', 'willpower', 'humanity', 'hunger', 
                       'blood_potency', 'experience', 'notes']
    
    for field in updatable_fields:
        if field in data:
            updates.append(f"{field} = ?")
            values.append(data[field])
    
    if updates:
        values.append(character_id)
        query = f"UPDATE character_sheets SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        c.execute(query, values)
        conn.commit()
    
    conn.close()
    
    return jsonify({"success": True, "message": "Character updated"})

# HTML Template (will be very large, creating in separate file)
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧛 VTM Storyteller - Hybrid Character System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #1a0000 0%, #2d0a0a 50%, #1a0000 100%);
            color: #e0e0e0;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #8b0000;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 3em;
            color: #ff0000;
            text-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #999;
            font-style: italic;
            font-size: 1.1em;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .tab {
            padding: 15px 30px;
            background: #2a0505;
            border: 2px solid #8b0000;
            color: #e0e0e0;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 1.1em;
            border-radius: 5px;
        }
        
        .tab:hover {
            background: #3d0808;
            border-color: #ff0000;
        }
        
        .tab.active {
            background: #8b0000;
            border-color: #ff0000;
            color: #fff;
            box-shadow: 0 0 20px rgba(139, 0, 0, 0.5);
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.3s;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Chat Section */
        .chat-container {
            background: #1a0505;
            border: 2px solid #8b0000;
            border-radius: 10px;
            padding: 20px;
            height: 600px;
            display: flex;
            flex-direction: column;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 15px;
            background: #0d0202;
            border-radius: 5px;
        }
        
        .message {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 8px;
            line-height: 1.6;
        }
        
        .message.user {
            background: #2a0505;
            border-left: 4px solid #ff0000;
        }
        
        .message.assistant {
            background: #051a1a;
            border-left: 4px solid #00ff00;
        }
        
        .message-label {
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .user .message-label {
            color: #ff0000;
        }
        
        .assistant .message-label {
            color: #00ff00;
        }
        
        .input-area {
            display: flex;
            gap: 10px;
        }
        
        input[type="text"], textarea {
            flex: 1;
            padding: 15px;
            background: #0d0202;
            border: 2px solid #8b0000;
            color: #e0e0e0;
            border-radius: 5px;
            font-family: 'Georgia', serif;
            font-size: 1em;
        }
        
        input[type="text"]:focus, textarea:focus {
            outline: none;
            border-color: #ff0000;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.3);
        }
        
        button {
            padding: 15px 30px;
            background: #8b0000;
            border: 2px solid #ff0000;
            color: #fff;
            cursor: pointer;
            border-radius: 5px;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s;
            font-family: 'Georgia', serif;
        }
        
        button:hover:not(:disabled) {
            background: #a00000;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
            transform: translateY(-2px);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* Character System */
        .character-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .option-card {
            background: #1a0505;
            border: 2px solid #8b0000;
            border-radius: 10px;
            padding: 30px;
            transition: all 0.3s;
        }
        
        .option-card:hover {
            border-color: #ff0000;
            box-shadow: 0 0 30px rgba(139, 0, 0, 0.3);
        }
        
        .option-card h3 {
            color: #ff0000;
            margin-bottom: 15px;
            font-size: 1.8em;
        }
        
        .option-card p {
            color: #999;
            margin-bottom: 20px;
            line-height: 1.6;
        }
        
        /* Demiplane Link Section */
        .demiplane-link {
            background: #0a1a0a;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .demiplane-link h4 {
            color: #00ff00;
            margin-bottom: 15px;
        }
        
        .linked-character {
            background: #051a05;
            padding: 20px;
            border-radius: 5px;
            margin-top: 15px;
        }
        
        .linked-character p {
            margin: 10px 0;
        }
        
        .linked-character strong {
            color: #00ff00;
        }
        
        /* Character Creation Form */
        .creation-wizard {
            background: #1a0505;
            border: 2px solid #8b0000;
            border-radius: 10px;
            padding: 30px;
        }
        
        .wizard-step {
            display: none;
        }
        
        .wizard-step.active {
            display: block;
            animation: fadeIn 0.3s;
        }
        
        .wizard-step h3 {
            color: #ff0000;
            margin-bottom: 20px;
            font-size: 2em;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 10px;
            color: #ff0000;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px;
            background: #0d0202;
            border: 2px solid #8b0000;
            color: #e0e0e0;
            border-radius: 5px;
            font-size: 1em;
        }
        
        .clan-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .clan-option {
            padding: 20px;
            background: #2a0505;
            border: 2px solid #8b0000;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
        }
        
        .clan-option:hover {
            border-color: #ff0000;
            background: #3d0808;
        }
        
        .clan-option.selected {
            border-color: #ff0000;
            background: #8b0000;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
        }
        
        .attributes-grid, .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .attribute-category, .skill-category {
            background: #0d0202;
            padding: 20px;
            border-radius: 5px;
            border: 2px solid #8b0000;
        }
        
        .attribute-category h4, .skill-category h4 {
            color: #ff0000;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .attribute-item, .skill-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .dots {
            display: flex;
            gap: 5px;
        }
        
        .dot {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid #8b0000;
            background: #0d0202;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .dot:hover {
            border-color: #ff0000;
        }
        
        .dot.filled {
            background: #ff0000;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
        }
        
        .points-remaining {
            text-align: center;
            font-size: 1.2em;
            color: #ff0000;
            margin-bottom: 20px;
            padding: 10px;
            background: #0d0202;
            border-radius: 5px;
        }
        
        .wizard-nav {
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
        }
        
        /* Character Sheet */
        .character-sheet {
            background: #1a0505;
            border: 2px solid #8b0000;
            border-radius: 10px;
            padding: 30px;
        }
        
        .sheet-header {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #8b0000;
        }
        
        .sheet-header-item {
            text-align: center;
        }
        
        .sheet-header-item label {
            display: block;
            color: #999;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .sheet-header-item .value {
            color: #ff0000;
            font-size: 1.5em;
            font-weight: bold;
        }
        
        .trackers {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .tracker {
            background: #0d0202;
            padding: 20px;
            border-radius: 5px;
            border: 2px solid #8b0000;
            text-align: center;
        }
        
        .tracker h4 {
            color: #ff0000;
            margin-bottom: 15px;
        }
        
        .tracker-boxes {
            display: flex;
            justify-content: center;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .tracker-box {
            width: 30px;
            height: 30px;
            border: 2px solid #8b0000;
            background: #0d0202;
            cursor: pointer;
            transition: all 0.2s;
            border-radius: 3px;
        }
        
        .tracker-box:hover {
            border-color: #ff0000;
        }
        
        .tracker-box.filled {
            background: #ff0000;
        }
        
        .tracker-box.damage {
            background: #000;
            border-color: #ff0000;
        }
        
        /* Dice Roller */
        .dice-roller {
            background: #1a0505;
            border: 2px solid #8b0000;
            border-radius: 10px;
            padding: 30px;
        }
        
        .dice-controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .dice-input {
            background: #0d0202;
            padding: 20px;
            border-radius: 5px;
            border: 2px solid #8b0000;
        }
        
        .dice-input label {
            display: block;
            color: #ff0000;
            margin-bottom: 10px;
            font-weight: bold;
        }
        
        .dice-input input[type="number"] {
            width: 100%;
            padding: 12px;
            background: #1a0505;
            border: 2px solid #8b0000;
            color: #e0e0e0;
            border-radius: 5px;
            font-size: 1.2em;
            text-align: center;
        }
        
        .dice-result {
            background: #0d0202;
            padding: 30px;
            border-radius: 5px;
            border: 2px solid #8b0000;
            margin-top: 30px;
            display: none;
        }
        
        .dice-result.show {
            display: block;
            animation: fadeIn 0.5s;
        }
        
        .dice-display {
            display: flex;
            gap: 30px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .dice-group h4 {
            color: #ff0000;
            margin-bottom: 15px;
        }
        
        .dice-list {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .die {
            width: 50px;
            height: 50px;
            border: 3px solid #8b0000;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            font-weight: bold;
            background: #1a0505;
            color: #fff;
        }
        
        .die.hunger {
            border-color: #ff0000;
            background: #3d0000;
        }
        
        .die.success {
            background: #003d00;
            border-color: #00ff00;
            color: #00ff00;
        }
        
        .die.ten {
            background: #3d3d00;
            border-color: #ffff00;
            color: #ffff00;
        }
        
        .result-summary {
            text-align: center;
            padding: 20px;
            background: #1a0505;
            border-radius: 5px;
        }
        
        .result-summary h3 {
            font-size: 2em;
            margin-bottom: 15px;
        }
        
        .result-summary.critical {
            background: #3d3d00;
            border: 3px solid #ffff00;
        }
        
        .result-summary.critical h3 {
            color: #ffff00;
        }
        
        .result-summary.messy {
            background: #3d0000;
            border: 3px solid #ff0000;
        }
        
        .result-summary.messy h3 {
            color: #ff0000;
        }
        
        .result-summary.bestial {
            background: #000;
            border: 3px solid #ff0000;
        }
        
        .result-summary.bestial h3 {
            color: #ff0000;
        }
        
        .result-summary.success {
            background: #003d00;
            border: 3px solid #00ff00;
        }
        
        .result-summary.success h3 {
            color: #00ff00;
        }
        
        /* Status indicator */
        .status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 5px;
            font-weight: bold;
            z-index: 1000;
        }
        
        .status.online {
            background: #003d00;
            border: 2px solid #00ff00;
            color: #00ff00;
        }
        
        .status.degraded {
            background: #3d3d00;
            border: 2px solid #ffff00;
            color: #ffff00;
        }
        
        .typing-indicator {
            display: none;
            padding: 15px;
            color: #999;
            font-style: italic;
        }
        
        .typing-indicator.show {
            display: block;
        }
        
        .typing-dots {
            display: inline-block;
        }
        
        .typing-dots span {
            animation: blink 1.4s infinite;
            animation-fill-mode: both;
        }
        
        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes blink {
            0%, 80%, 100% {
                opacity: 0;
            }
            40% {
                opacity: 1;
            }
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0d0202;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #8b0000;
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #a00000;
        }
    </style>
</head>
<body>
    <div class="status online" id="status">System Online</div>
    
    <div class="container">
        <header>
            <h1>🧛 VTM Storyteller</h1>
            <p class="subtitle">Vampire: The Masquerade 5th Edition AI Game Master</p>
            <p class="subtitle">Hybrid Character System</p>
        </header>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('chat')">Chat</div>
            <div class="tab" onclick="switchTab('character')">Character</div>
            <div class="tab" onclick="switchTab('sheet')">Character Sheet</div>
            <div class="tab" onclick="switchTab('dice')">Dice Roller</div>
        </div>
        
        <!-- Chat Tab -->
        <div id="chat-tab" class="tab-content active">
            <div class="chat-container">
                <div class="messages" id="messages">
                    <div class="message assistant">
                        <div class="message-label">Storyteller</div>
                        <div>Welcome, Kindred. I am your Storyteller for tonight's chronicle. Whether you seek to create a new character, explore the World of Darkness, or begin your journey into the night, I am here to guide you. What brings you to my domain?</div>
                    </div>
                </div>
                <div class="typing-indicator" id="typing">
                    <span class="typing-dots">
                        <span>.</span><span>.</span><span>.</span>
                    </span>
                    Storyteller is writing...
                </div>
                <div class="input-area">
                    <input type="text" id="message-input" placeholder="Speak to the Storyteller..." onkeypress="handleKeyPress(event)">
                    <button onclick="sendMessage()" id="send-btn">Send</button>
                </div>
            </div>
        </div>
        
        <!-- Character Tab -->
        <div id="character-tab" class="tab-content">
            <div class="character-options">
                <div class="option-card">
                    <h3>🔗 Link Demiplane Character</h3>
                    <p>Already have a character on Demiplane? Link it here to use with the Storyteller AI. Your character stats will be accessible during gameplay.</p>
                    <button onclick="showDemiplaneLink()">Link Character</button>
                    
                    <div class="demiplane-link" id="demiplane-link-section" style="display: none;">
                        <h4>Enter Your Demiplane Character URL</h4>
                        <input type="text" id="demiplane-url" placeholder="https://app.demiplane.com/nexus/vampire/character-sheet/...">
                        <div style="margin-top: 15px;">
                            <input type="text" id="demiplane-name" placeholder="Character Name" style="margin-bottom: 10px;">
                            <input type="text" id="demiplane-clan" placeholder="Clan" style="margin-bottom: 10px;">
                            <input type="text" id="demiplane-predator" placeholder="Predator Type">
                        </div>
                        <button onclick="linkDemiplaneCharacter()" style="margin-top: 15px;">Save Link</button>
                        
                        <div class="linked-character" id="linked-character" style="display: none;">
                            <h4 style="color: #00ff00;">✓ Character Linked</h4>
                            <p><strong>Name:</strong> <span id="linked-name"></span></p>
                            <p><strong>Clan:</strong> <span id="linked-clan"></span></p>
                            <p><strong>Predator:</strong> <span id="linked-predator"></span></p>
                            <a href="#" id="view-sheet-link" target="_blank" style="color: #00ff00;">View Full Sheet on Demiplane →</a>
                        </div>
                    </div>
                </div>
                
                <div class="option-card">
                    <h3>✨ Create Custom Character</h3>
                    <p>Create a new character using our built-in character creation wizard. Perfect for quick games or if you don't have a Demiplane account.</p>
                    <button onclick="startCharacterCreation()">Create Character</button>
                </div>
            </div>
            
            <!-- Character Creation Wizard -->
            <div class="creation-wizard" id="creation-wizard" style="display: none;">
                <!-- Step 1: Basic Info -->
                <div class="wizard-step active" id="step-1">
                    <h3>Step 1: Basic Information</h3>
                    <div class="form-group">
                        <label>Character Name</label>
                        <input type="text" id="char-name" placeholder="Enter character name">
                    </div>
                    <div class="form-group">
                        <label>Concept</label>
                        <input type="text" id="char-concept" placeholder="e.g., Street Artist, Corporate Lawyer, Underground DJ">
                    </div>
                    <div class="form-group">
                        <label>Chronicle</label>
                        <input type="text" id="char-chronicle" placeholder="Name of your chronicle">
                    </div>
                    <div class="wizard-nav">
                        <button onclick="cancelCreation()">Cancel</button>
                        <button onclick="nextStep(2)">Next →</button>
                    </div>
                </div>
                
                <!-- Step 2: Clan Selection -->
                <div class="wizard-step" id="step-2">
                    <h3>Step 2: Choose Your Clan</h3>
                    <div class="clan-grid" id="clan-grid">
                        <!-- Clans will be populated by JavaScript -->
                    </div>
                    <div class="wizard-nav">
                        <button onclick="prevStep(1)">← Back</button>
                        <button onclick="nextStep(3)">Next →</button>
                    </div>
                </div>
                
                <!-- Step 3: Attributes -->
                <div class="wizard-step" id="step-3">
                    <h3>Step 3: Distribute Attributes</h3>
                    <p class="points-remaining" id="attr-points">Points Remaining: Physical (7), Social (7), Mental (7)</p>
                    <div class="attributes-grid" id="attributes-grid">
                        <!-- Attributes will be populated by JavaScript -->
                    </div>
                    <div class="wizard-nav">
                        <button onclick="prevStep(2)">← Back</button>
                        <button onclick="nextStep(4)">Next →</button>
                    </div>
                </div>
                
                <!-- Step 4: Skills -->
                <div class="wizard-step" id="step-4">
                    <h3>Step 4: Distribute Skills</h3>
                    <p class="points-remaining" id="skill-points">Points Remaining: 13</p>
                    <div class="skills-grid" id="skills-grid">
                        <!-- Skills will be populated by JavaScript -->
                    </div>
                    <div class="wizard-nav">
                        <button onclick="prevStep(3)">← Back</button>
                        <button onclick="nextStep(5)">Next →</button>
                    </div>
                </div>
                
                <!-- Step 5: Disciplines & Final -->
                <div class="wizard-step" id="step-5">
                    <h3>Step 5: Choose Disciplines</h3>
                    <p style="color: #999; margin-bottom: 20px;">Select 2 dots of Disciplines from your clan's options</p>
                    <div id="disciplines-grid">
                        <!-- Disciplines will be populated based on clan -->
                    </div>
                    <div class="wizard-nav">
                        <button onclick="prevStep(4)">← Back</button>
                        <button onclick="finishCreation()">Create Character</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Character Sheet Tab -->
        <div id="sheet-tab" class="tab-content">
            <div class="character-sheet" id="character-sheet">
                <p style="text-align: center; color: #999; padding: 50px;">No character loaded. Create or link a character first.</p>
            </div>
        </div>
        
        <!-- Dice Roller Tab -->
        <div id="dice-tab" class="tab-content">
            <div class="dice-roller">
                <h2 style="color: #ff0000; margin-bottom: 30px; text-align: center;">🎲 VTM 5e Dice Roller</h2>
                <div class="dice-controls">
                    <div class="dice-input">
                        <label>Pool Size</label>
                        <input type="number" id="pool-size" min="1" max="20" value="5">
                    </div>
                    <div class="dice-input">
                        <label>Hunger Dice</label>
                        <input type="number" id="hunger-dice" min="0" max="5" value="1">
                    </div>
                    <div class="dice-input">
                        <label>Difficulty</label>
                        <input type="number" id="difficulty" min="1" max="10" value="2">
                    </div>
                </div>
                <div style="text-align: center; margin-bottom: 30px;">
                    <button onclick="rollDice()" style="font-size: 1.2em; padding: 20px 50px;">🎲 ROLL</button>
                </div>
                <div class="dice-result" id="dice-result">
                    <!-- Results will be displayed here -->
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Global state
        let currentCharacter = null;
        let userId = 'user_' + Math.random().toString(36).substr(2, 9);
        
        // VTM 5e Data
        const clans = [
            { name: 'Brujah', disciplines: ['Celerity', 'Potence', 'Presence'] },
            { name: 'Gangrel', disciplines: ['Animalism', 'Fortitude', 'Protean'] },
            { name: 'Malkavian', disciplines: ['Auspex', 'Dominate', 'Obfuscate'] },
            { name: 'Nosferatu', disciplines: ['Animalism', 'Obfuscate', 'Potence'] },
            { name: 'Toreador', disciplines: ['Auspex', 'Celerity', 'Presence'] },
            { name: 'Tremere', disciplines: ['Auspex', 'Blood Sorcery', 'Dominate'] },
            { name: 'Ventrue', disciplines: ['Dominate', 'Fortitude', 'Presence'] },
            { name: 'Caitiff', disciplines: ['Choose any 3'] },
            { name: 'Thin-Blood', disciplines: ['Thin-Blood Alchemy'] }
        ];
        
        const attributes = {
            physical: ['Strength', 'Dexterity', 'Stamina'],
            social: ['Charisma', 'Manipulation', 'Composure'],
            mental: ['Intelligence', 'Wits', 'Resolve']
        };
        
        const skills = {
            physical: ['Athletics', 'Brawl', 'Craft', 'Drive', 'Firearms', 'Larceny', 'Melee', 'Stealth', 'Survival'],
            social: ['Animal Ken', 'Etiquette', 'Insight', 'Intimidation', 'Leadership', 'Performance', 'Persuasion', 'Streetwise', 'Subterfuge'],
            mental: ['Academics', 'Awareness', 'Finance', 'Investigation', 'Medicine', 'Occult', 'Politics', 'Science', 'Technology']
        };
        
        // Character creation state
        let characterData = {
            attributes: {},
            skills: {},
            disciplines: {}
        };
        
        // Tab switching
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
        }
        
        // Chat functionality
        async function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addMessage('user', message);
            input.value = '';
            
            // Disable send button and show typing indicator
            const sendBtn = document.getElementById('send-btn');
            sendBtn.disabled = true;
            document.getElementById('typing').classList.add('show');
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, user_id: userId })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    addMessage('assistant', 'Error: ' + data.error);
                } else {
                    addMessage('assistant', data.response);
                }
            } catch (error) {
                addMessage('assistant', 'Error: Connection lost. Please try again.');
            } finally {
                sendBtn.disabled = false;
                document.getElementById('typing').classList.remove('show');
            }
        }
        
        function addMessage(role, content) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            messageDiv.innerHTML = `
                <div class="message-label">${role === 'user' ? 'You' : 'Storyteller'}</div>
                <div>${content}</div>
            `;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        // Demiplane linking
        function showDemiplaneLink() {
            document.getElementById('demiplane-link-section').style.display = 'block';
        }
        
        async function linkDemiplaneCharacter() {
            const url = document.getElementById('demiplane-url').value;
            const name = document.getElementById('demiplane-name').value;
            const clan = document.getElementById('demiplane-clan').value;
            const predator = document.getElementById('demiplane-predator').value;
            
            if (!url || !name || !clan) {
                alert('Please fill in all required fields');
                return;
            }
            
            try {
                const response = await fetch('/character/link', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        demiplane_url: url,
                        name,
                        clan,
                        predator_type: predator
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('linked-name').textContent = name;
                    document.getElementById('linked-clan').textContent = clan;
                    document.getElementById('linked-predator').textContent = predator;
                    document.getElementById('view-sheet-link').href = url;
                    document.getElementById('linked-character').style.display = 'block';
                    alert('Character linked successfully!');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error linking character: ' + error.message);
            }
        }
        
        // Character creation
        function startCharacterCreation() {
            document.getElementById('creation-wizard').style.display = 'block';
            initializeClans();
            initializeAttributes();
            initializeSkills();
        }
        
        function cancelCreation() {
            if (confirm('Are you sure you want to cancel character creation?')) {
                document.getElementById('creation-wizard').style.display = 'none';
                resetWizard();
            }
        }
        
        function nextStep(stepNum) {
            document.querySelectorAll('.wizard-step').forEach(step => step.classList.remove('active'));
            document.getElementById(`step-${stepNum}`).classList.add('active');
        }
        
        function prevStep(stepNum) {
            document.querySelectorAll('.wizard-step').forEach(step => step.classList.remove('active'));
            document.getElementById(`step-${stepNum}`).classList.add('active');
        }
        
        function initializeClans() {
            const grid = document.getElementById('clan-grid');
            grid.innerHTML = '';
            
            clans.forEach(clan => {
                const div = document.createElement('div');
                div.className = 'clan-option';
                div.innerHTML = `
                    <h4>${clan.name}</h4>
                    <p style="font-size: 0.9em; margin-top: 10px;">${clan.disciplines.join(', ')}</p>
                `;
                div.onclick = () => selectClan(clan.name, div);
                grid.appendChild(div);
            });
        }
        
        function selectClan(clanName, element) {
            document.querySelectorAll('.clan-option').forEach(opt => opt.classList.remove('selected'));
            element.classList.add('selected');
            characterData.clan = clanName;
            
            // Update disciplines for step 5
            const selectedClan = clans.find(c => c.name === clanName);
            updateDisciplines(selectedClan.disciplines);
        }
        
        function initializeAttributes() {
            const grid = document.getElementById('attributes-grid');
            grid.innerHTML = '';
            
            Object.entries(attributes).forEach(([category, attrs]) => {
                const div = document.createElement('div');
                div.className = 'attribute-category';
                div.innerHTML = `<h4>${category.toUpperCase()}</h4>`;
                
                attrs.forEach(attr => {
                    characterData.attributes[attr] = 1; // Start at 1
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'attribute-item';
                    itemDiv.innerHTML = `
                        <span>${attr}</span>
                        <div class="dots" id="attr-${attr}">
                            ${[1,2,3,4,5].map(i => `<div class="dot ${i === 1 ? 'filled' : ''}" onclick="setAttributeDot('${attr}', ${i})"></div>`).join('')}
                        </div>
                    `;
                    div.appendChild(itemDiv);
                });
                
                grid.appendChild(div);
            });
        }
        
        function setAttributeDot(attr, value) {
            characterData.attributes[attr] = value;
            const dotsContainer = document.getElementById(`attr-${attr}`);
            const dots = dotsContainer.querySelectorAll('.dot');
            dots.forEach((dot, index) => {
                if (index < value) {
                    dot.classList.add('filled');
                } else {
                    dot.classList.remove('filled');
                }
            });
        }
        
        function initializeSkills() {
            const grid = document.getElementById('skills-grid');
            grid.innerHTML = '';
            
            Object.entries(skills).forEach(([category, skillList]) => {
                const div = document.createElement('div');
                div.className = 'skill-category';
                div.innerHTML = `<h4>${category.toUpperCase()}</h4>`;
                
                skillList.forEach(skill => {
                    characterData.skills[skill] = 0;
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'skill-item';
                    itemDiv.innerHTML = `
                        <span>${skill}</span>
                        <div class="dots" id="skill-${skill}">
                            ${[1,2,3,4,5].map(i => `<div class="dot" onclick="setSkillDot('${skill}', ${i})"></div>`).join('')}
                        </div>
                    `;
                    div.appendChild(itemDiv);
                });
                
                grid.appendChild(div);
            });
        }
        
        function setSkillDot(skill, value) {
            characterData.skills[skill] = value;
            const dotsContainer = document.getElementById(`skill-${skill}`);
            const dots = dotsContainer.querySelectorAll('.dot');
            dots.forEach((dot, index) => {
                if (index < value) {
                    dot.classList.add('filled');
                } else {
                    dot.classList.remove('filled');
                }
            });
        }
        
        function updateDisciplines(disciplineList) {
            const grid = document.getElementById('disciplines-grid');
            grid.innerHTML = '';
            
            disciplineList.forEach(disc => {
                characterData.disciplines[disc] = 0;
                const div = document.createElement('div');
                div.className = 'attribute-item';
                div.innerHTML = `
                    <span>${disc}</span>
                    <div class="dots" id="disc-${disc}">
                        ${[1,2].map(i => `<div class="dot" onclick="setDisciplineDot('${disc}', ${i})"></div>`).join('')}
                    </div>
                `;
                grid.appendChild(div);
            });
        }
        
        function setDisciplineDot(disc, value) {
            characterData.disciplines[disc] = value;
            const dotsContainer = document.getElementById(`disc-${disc}`);
            const dots = dotsContainer.querySelectorAll('.dot');
            dots.forEach((dot, index) => {
                if (index < value) {
                    dot.classList.add('filled');
                } else {
                    dot.classList.remove('filled');
                }
            });
        }
        
        async function finishCreation() {
            const name = document.getElementById('char-name').value;
            const concept = document.getElementById('char-concept').value;
            
            if (!name || !characterData.clan) {
                alert('Please complete all required fields');
                return;
            }
            
            try {
                const response = await fetch('/character/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        name,
                        clan: characterData.clan,
                        concept,
                        attributes: characterData.attributes,
                        skills: characterData.skills,
                        disciplines: characterData.disciplines
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('Character created successfully!');
                    currentCharacter = data.character_id;
                    loadCharacterSheet(data.character_id);
                    document.getElementById('creation-wizard').style.display = 'none';
                    switchTab('sheet');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                alert('Error creating character: ' + error.message);
            }
        }
        
        async function loadCharacterSheet(characterId) {
            try {
                const response = await fetch(`/character/${characterId}`);
                const char = await response.json();
                
                if (char.error) {
                    alert('Error loading character');
                    return;
                }
                
                // Display character sheet
                const sheetDiv = document.getElementById('character-sheet');
                sheetDiv.innerHTML = `
                    <div class="sheet-header">
                        <div class="sheet-header-item">
                            <label>Name</label>
                            <div class="value">${char.name}</div>
                        </div>
                        <div class="sheet-header-item">
                            <label>Clan</label>
                            <div class="value">${char.clan}</div>
                        </div>
                        <div class="sheet-header-item">
                            <label>Predator Type</label>
                            <div class="value">${char.predator_type || 'None'}</div>
                        </div>
                    </div>
                    
                    <div class="trackers">
                        <div class="tracker">
                            <h4>Health</h4>
                            <div class="tracker-boxes">
                                ${Array(char.health + 3).fill(0).map((_, i) => `<div class="tracker-box"></div>`).join('')}
                            </div>
                        </div>
                        <div class="tracker">
                            <h4>Willpower</h4>
                            <div class="tracker-boxes">
                                ${Array(char.willpower + 3).fill(0).map((_, i) => `<div class="tracker-box"></div>`).join('')}
                            </div>
                        </div>
                        <div class="tracker">
                            <h4>Humanity</h4>
                            <div class="tracker-boxes">
                                ${Array(10).fill(0).map((_, i) => `<div class="tracker-box ${i < char.humanity ? 'filled' : ''}"></div>`).join('')}
                            </div>
                        </div>
                        <div class="tracker">
                            <h4>Hunger</h4>
                            <div class="tracker-boxes">
                                ${Array(5).fill(0).map((_, i) => `<div class="tracker-box ${i < char.hunger ? 'filled' : ''}"></div>`).join('')}
                            </div>
                        </div>
                    </div>
                    
                    <h3 style="color: #ff0000; margin: 30px 0 20px;">Attributes</h3>
                    <div class="attributes-grid">
                        ${Object.entries(attributes).map(([category, attrs]) => `
                            <div class="attribute-category">
                                <h4>${category.toUpperCase()}</h4>
                                ${attrs.map(attr => `
                                    <div class="attribute-item">
                                        <span>${attr}</span>
                                        <div class="dots">
                                            ${[1,2,3,4,5].map(i => `<div class="dot ${i <= char.attributes[attr] ? 'filled' : ''}"></div>`).join('')}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        `).join('')}
                    </div>
                    
                    <h3 style="color: #ff0000; margin: 30px 0 20px;">Skills</h3>
                    <div class="skills-grid">
                        ${Object.entries(skills).map(([category, skillList]) => `
                            <div class="skill-category">
                                <h4>${category.toUpperCase()}</h4>
                                ${skillList.map(skill => `
                                    <div class="skill-item">
                                        <span>${skill}</span>
                                        <div class="dots">
                                            ${[1,2,3,4,5].map(i => `<div class="dot ${i <= (char.skills[skill] || 0) ? 'filled' : ''}"></div>`).join('')}
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        `).join('')}
                    </div>
                    
                    <h3 style="color: #ff0000; margin: 30px 0 20px;">Disciplines</h3>
                    <div class="attributes-grid">
                        ${Object.entries(char.disciplines).map(([disc, level]) => `
                            <div class="attribute-item">
                                <span>${disc}</span>
                                <div class="dots">
                                    ${[1,2,3,4,5].map(i => `<div class="dot ${i <= level ? 'filled' : ''}"></div>`).join('')}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } catch (error) {
                alert('Error loading character sheet: ' + error.message);
            }
        }
        
        // Dice roller
        async function rollDice() {
            const poolSize = parseInt(document.getElementById('pool-size').value);
            const hungerDice = parseInt(document.getElementById('hunger-dice').value);
            const difficulty = parseInt(document.getElementById('difficulty').value);
            
            if (hungerDice > poolSize) {
                alert('Hunger dice cannot exceed pool size');
                return;
            }
            
            try {
                const response = await fetch('/roll', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pool: poolSize,
                        hunger: hungerDice,
                        user_id: userId,
                        character_id: currentCharacter
                    })
                });
                
                const result = await response.json();
                displayDiceResult(result, difficulty);
            } catch (error) {
                alert('Error rolling dice: ' + error.message);
            }
        }
        
        function displayDiceResult(result, difficulty) {
            const resultDiv = document.getElementById('dice-result');
            
            let summaryClass = '';
            let summaryText = '';
            
            if (result.bestial_failure) {
                summaryClass = 'bestial';
                summaryText = '🐺 BESTIAL FAILURE';
            } else if (result.messy_critical) {
                summaryClass = 'messy';
                summaryText = '💀 MESSY CRITICAL';
            } else if (result.critical) {
                summaryClass = 'critical';
                summaryText = '⭐ CRITICAL WIN';
            } else if (result.successes >= difficulty) {
                summaryClass = 'success';
                summaryText = '✓ SUCCESS';
            } else {
                summaryClass = '';
                summaryText = '✗ FAILURE';
            }
            
            resultDiv.innerHTML = `
                <div class="dice-display">
                    <div class="dice-group">
                        <h4>Normal Dice</h4>
                        <div class="dice-list">
                            ${result.normal_dice.map(d => `
                                <div class="die ${d >= 6 ? 'success' : ''} ${d === 10 ? 'ten' : ''}">${d}</div>
                            `).join('')}
                        </div>
                    </div>
                    ${result.hunger_dice.length > 0 ? `
                        <div class="dice-group">
                            <h4>Hunger Dice</h4>
                            <div class="dice-list">
                                ${result.hunger_dice.map(d => `
                                    <div class="die hunger ${d >= 6 ? 'success' : ''} ${d === 10 ? 'ten' : ''}">${d}</div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                
                <div class="result-summary ${summaryClass}">
                    <h3>${summaryText}</h3>
                    <p style="font-size: 1.5em; margin: 15px 0;">
                        <strong>${result.successes}</strong> successes
                        ${result.pairs > 0 ? `<br><strong>${result.pairs}</strong> critical pair(s)` : ''}
                    </p>
                    <p style="color: #999;">Difficulty: ${difficulty}</p>
                </div>
            `;
            
            resultDiv.classList.add('show');
        }
        
        function resetWizard() {
            characterData = {
                attributes: {},
                skills: {},
                disciplines: {}
            };
            document.querySelectorAll('.wizard-step').forEach((step, index) => {
                step.classList.remove('active');
                if (index === 0) step.classList.add('active');
            });
        }
        
        // Check system health on load
        async function checkHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                const statusDiv = document.getElementById('status');
                
                if (data.status === 'healthy') {
                    statusDiv.className = 'status online';
                    statusDiv.textContent = 'System Online';
                } else {
                    statusDiv.className = 'status degraded';
                    statusDiv.textContent = 'System Degraded';
                }
            } catch (error) {
                const statusDiv = document.getElementById('status');
                statusDiv.className = 'status degraded';
                statusDiv.textContent = 'System Offline';
            }
        }
        
        // Initialize
        checkHealth();
        setInterval(checkHealth, 60000); // Check every minute
    </script>
</body>
</html>

"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

