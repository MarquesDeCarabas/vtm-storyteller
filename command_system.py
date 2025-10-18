"""
Command System for VTM Storyteller
Handles parsing and execution of slash commands
"""

import re
from campaign_session_api import *
from campaign_recall import *

class CommandSystem:
    def __init__(self):
        self.commands = {
            'campaign': self.handle_campaign_command,
            'session': self.handle_session_command,
            'npc': self.handle_npc_command,
            'location': self.handle_location_command,
            'item': self.handle_item_command,
            'roll': self.handle_roll_command,
            'help': self.handle_help_command
        }
    
    def is_command(self, message):
        """Check if a message is a command"""
        return message.strip().startswith('/')
    
    def parse_command(self, message):
        """Parse a command message into command and arguments"""
        message = message.strip()
        if not message.startswith('/'):
            return None, None
        
        # Remove the leading slash
        message = message[1:]
        
        # Split into command and arguments
        parts = message.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ''
        
        return command, args
    
    def execute_command(self, message):
        """Execute a command and return the result"""
        command, args = self.parse_command(message)
        
        if not command:
            return {'error': 'Invalid command format'}
        
        if command not in self.commands:
            return {'error': f'Unknown command: /{command}. Type /help for available commands.'}
        
        try:
            return self.commands[command](args)
        except Exception as e:
            return {'error': f'Error executing command: {str(e)}'}
    
    # ==================== CAMPAIGN COMMANDS ====================
    
    def handle_campaign_command(self, args):
        """Handle /campaign commands"""
        if not args:
            return {'error': 'Usage: /campaign <new|load|list|info> [args]'}
        
        parts = args.split(maxsplit=1)
        subcommand = parts[0].lower()
        subargs = parts[1] if len(parts) > 1 else ''
        
        if subcommand == 'new':
            if not subargs:
                return {'error': 'Usage: /campaign new <name>'}
            return self.create_campaign_command(subargs)
        
        elif subcommand == 'load':
            if not subargs:
                return {'error': 'Usage: /campaign load <name>'}
            return self.load_campaign_command(subargs)
        
        elif subcommand == 'list':
            return self.list_campaigns_command()
        
        elif subcommand == 'info':
            return self.campaign_info_command()
        
        else:
            return {'error': f'Unknown campaign subcommand: {subcommand}'}
    
    def create_campaign_command(self, name):
        """Create a new campaign"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO campaigns (name, status, total_sessions, created_at, updated_at)
            VALUES (?, 'active', 0, ?, ?)
        ''', (name, datetime.now(), datetime.now()))
        
        campaign_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': f'✅ Campaign "{name}" created successfully!',
            'campaign_id': campaign_id
        }
    
    def load_campaign_command(self, name):
        """Load an existing campaign"""
        conn = get_db_connection()
        campaign = conn.execute('''
            SELECT * FROM campaigns WHERE name LIKE ?
        ''', (f'%{name}%',)).fetchone()
        conn.close()
        
        if not campaign:
            return {'error': f'Campaign "{name}" not found'}
        
        # Store in session
        session['active_campaign_id'] = campaign['id']
        
        return {
            'success': True,
            'message': f'✅ Campaign "{campaign["name"]}" loaded successfully!',
            'campaign': dict(campaign)
        }
    
    def list_campaigns_command(self):
        """List all campaigns"""
        conn = get_db_connection()
        campaigns = conn.execute('''
            SELECT id, name, city, faction, status, total_sessions
            FROM campaigns
            ORDER BY updated_at DESC
        ''').fetchall()
        conn.close()
        
        if not campaigns:
            return {'message': 'No campaigns found. Use /campaign new <name> to create one.'}
        
        campaign_list = []
        for c in campaigns:
            campaign_list.append(f"• {c['name']} ({c['city'] or 'Unknown City'}) - {c['total_sessions']} sessions - Status: {c['status']}")
        
        return {
            'success': True,
            'message': '📖 Available Campaigns:\n\n' + '\n'.join(campaign_list)
        }
    
    def campaign_info_command(self):
        """Show info about current campaign"""
        campaign_id = get_active_campaign_id()
        
        if not campaign_id:
            return {'error': 'No active campaign. Use /campaign load <name> or /campaign new <name>'}
        
        conn = get_db_connection()
        campaign = conn.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,)).fetchone()
        
        # Get stats
        npc_count = conn.execute('SELECT COUNT(*) as count FROM campaign_npcs WHERE campaign_id = ?', (campaign_id,)).fetchone()['count']
        location_count = conn.execute('SELECT COUNT(*) as count FROM campaign_locations WHERE campaign_id = ?', (campaign_id,)).fetchone()['count']
        item_count = conn.execute('SELECT COUNT(*) as count FROM campaign_items WHERE campaign_id = ?', (campaign_id,)).fetchone()['count']
        
        conn.close()
        
        info = f"""
📖 **Campaign: {campaign['name']}**

🏙️ City: {campaign['city'] or 'Not set'}
⚔️ Faction: {campaign['faction'] or 'Not set'}
📊 Status: {campaign['status']}
🎭 Total Sessions: {campaign['total_sessions']}

**Database:**
• NPCs: {npc_count}
• Locations: {location_count}
• Items: {item_count}

📝 Description: {campaign['description'] or 'No description'}
"""
        
        return {'success': True, 'message': info}
    
    # ==================== SESSION COMMANDS ====================
    
    def handle_session_command(self, args):
        """Handle /session commands"""
        if not args:
            return {'error': 'Usage: /session <start|end|summary>'}
        
        subcommand = args.strip().lower()
        
        if subcommand == 'start':
            return self.start_session_command()
        
        elif subcommand == 'end':
            return self.end_session_command()
        
        elif subcommand == 'summary':
            return self.session_summary_command()
        
        else:
            return {'error': f'Unknown session subcommand: {subcommand}'}
    
    def start_session_command(self):
        """Start a new session"""
        campaign_id = get_active_campaign_id()
        
        if not campaign_id:
            return {'error': 'No active campaign. Use /campaign load <name> first.'}
        
        # Check if there's already an active session
        active_session = get_active_session_id()
        if active_session:
            return {'error': 'A session is already active. Use /session end first.'}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current session count
        campaign = conn.execute('SELECT total_sessions, name FROM campaigns WHERE id = ?', (campaign_id,)).fetchone()
        session_number = campaign['total_sessions'] + 1
        
        # Create new session
        cursor.execute('''
            INSERT INTO campaign_sessions (campaign_id, session_number, start_time, status)
            VALUES (?, ?, ?, 'active')
        ''', (campaign_id, session_number, datetime.now()))
        
        session_id = cursor.lastrowid
        
        # Update campaign
        cursor.execute('''
            UPDATE campaigns
            SET total_sessions = ?, updated_at = ?
            WHERE id = ?
        ''', (session_number, datetime.now(), campaign_id))
        
        conn.commit()
        conn.close()
        
        # Store in session
        session['active_session_id'] = session_id
        
        return {
            'success': True,
            'message': f'🎬 Session {session_number} started for campaign "{campaign["name"]}"!\n\nLet the story begin...',
            'session_id': session_id,
            'session_number': session_number
        }
    
    def end_session_command(self):
        """End the current session"""
        session_id = get_active_session_id()
        
        if not session_id:
            return {'error': 'No active session to end.'}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get session info
        session_data = conn.execute('SELECT * FROM campaign_sessions WHERE id = ?', (session_id,)).fetchone()
        
        # Update session
        cursor.execute('''
            UPDATE campaign_sessions
            SET end_time = ?, status = 'completed'
            WHERE id = ?
        ''', (datetime.now(), session_id))
        
        conn.commit()
        conn.close()
        
        # Clear from session
        session.pop('active_session_id', None)
        
        return {
            'success': True,
            'message': f'🎬 Session {session_data["session_number"]} ended.\n\nUse /session summary to get a summary of what happened.',
            'session_id': session_id
        }
    
    def session_summary_command(self):
        """Get summary of the last session"""
        session_id = get_active_session_id()
        
        if not session_id:
            # Get the last completed session
            campaign_id = get_active_campaign_id()
            if not campaign_id:
                return {'error': 'No campaign or session active.'}
            
            conn = get_db_connection()
            last_session = conn.execute('''
                SELECT * FROM campaign_sessions
                WHERE campaign_id = ? AND status = 'completed'
                ORDER BY session_number DESC
                LIMIT 1
            ''', (campaign_id,)).fetchone()
            conn.close()
            
            if not last_session:
                return {'error': 'No completed sessions found.'}
            
            session_id = last_session['id']
        
        conn = get_db_connection()
        session_data = conn.execute('SELECT * FROM campaign_sessions WHERE id = ?', (session_id,)).fetchone()
        
        # Get events from this session
        events = conn.execute('''
            SELECT * FROM campaign_events
            WHERE campaign_id = ? AND created_at BETWEEN ? AND ?
            ORDER BY created_at
        ''', (session_data['campaign_id'], session_data['start_time'], session_data['end_time'] or datetime.now())).fetchall()
        
        # Get NPCs created
        npcs = conn.execute('''
            SELECT name, clan FROM campaign_npcs
            WHERE campaign_id = ? AND created_at BETWEEN ? AND ?
        ''', (session_data['campaign_id'], session_data['start_time'], session_data['end_time'] or datetime.now())).fetchall()
        
        # Get locations created
        locations = conn.execute('''
            SELECT name, type FROM campaign_locations
            WHERE campaign_id = ? AND created_at BETWEEN ? AND ?
        ''', (session_data['campaign_id'], session_data['start_time'], session_data['end_time'] or datetime.now())).fetchall()
        
        conn.close()
        
        summary = f"""
📊 **Session {session_data['session_number']} Summary**

⏱️ Duration: {session_data['start_time']} - {session_data['end_time'] or 'Ongoing'}

**Content Created:**
• NPCs: {len(npcs)} ({', '.join([n['name'] for n in npcs]) if npcs else 'None'})
• Locations: {len(locations)} ({', '.join([l['name'] for l in locations]) if locations else 'None'})
• Events: {len(events)}
"""
        
        return {'success': True, 'message': summary}
    
    # ==================== DATABASE COMMANDS ====================
    
    def handle_npc_command(self, args):
        """Handle /npc commands"""
        campaign_id = get_active_campaign_id()
        if not campaign_id:
            return {'error': 'No active campaign.'}
        
        if not args or args.strip() == 'list':
            return self.list_npcs_command(campaign_id)
        
        parts = args.split(maxsplit=1)
        subcommand = parts[0].lower()
        
        if subcommand == 'search' and len(parts) > 1:
            return self.search_npcs_command(campaign_id, parts[1])
        
        return {'error': 'Usage: /npc list or /npc search <name>'}
    
    def list_npcs_command(self, campaign_id):
        """List all NPCs"""
        npcs = search_npcs(campaign_id)
        
        if not npcs:
            return {'message': 'No NPCs found in this campaign.'}
        
        npc_list = []
        for npc in npcs:
            npc_list.append(f"• {npc['name']} ({npc['clan']}) - {npc['faction'] or 'Independent'} - Status: {npc['status']}")
        
        return {
            'success': True,
            'message': f'👥 NPCs in Campaign ({len(npcs)} total):\n\n' + '\n'.join(npc_list)
        }
    
    def search_npcs_command(self, campaign_id, search_term):
        """Search for NPCs"""
        npcs = search_npcs(campaign_id, name=search_term)
        
        if not npcs:
            return {'message': f'No NPCs found matching "{search_term}".'}
        
        # Format detailed info for found NPCs
        npc_info = []
        for npc in npcs:
            info = f"""
**{npc['name']}** ({npc['real_name'] or 'Unknown'})
• Clan: {npc['clan']}
• Faction: {npc['faction'] or 'Independent'}
• Status: {npc['status']}
• Personality: {npc['personality'][:100] if npc['personality'] else 'Unknown'}...
"""
            npc_info.append(info)
        
        return {
            'success': True,
            'message': f'🔍 Found {len(npcs)} NPC(s):\n' + '\n'.join(npc_info)
        }
    
    def handle_location_command(self, args):
        """Handle /location commands"""
        campaign_id = get_active_campaign_id()
        if not campaign_id:
            return {'error': 'No active campaign.'}
        
        if not args or args.strip() == 'list':
            return self.list_locations_command(campaign_id)
        
        parts = args.split(maxsplit=1)
        subcommand = parts[0].lower()
        
        if subcommand == 'search' and len(parts) > 1:
            return self.search_locations_command(campaign_id, parts[1])
        
        return {'error': 'Usage: /location list or /location search <name>'}
    
    def list_locations_command(self, campaign_id):
        """List all locations"""
        locations = search_locations(campaign_id)
        
        if not locations:
            return {'message': 'No locations found in this campaign.'}
        
        location_list = []
        for loc in locations:
            location_list.append(f"• {loc['name']} ({loc['type']}) - {loc['city'] or 'Unknown City'} - Status: {loc['status']}")
        
        return {
            'success': True,
            'message': f'🏛️ Locations in Campaign ({len(locations)} total):\n\n' + '\n'.join(location_list)
        }
    
    def search_locations_command(self, campaign_id, search_term):
        """Search for locations"""
        locations = search_locations(campaign_id, name=search_term)
        
        if not locations:
            return {'message': f'No locations found matching "{search_term}".'}
        
        location_info = []
        for loc in locations:
            info = f"""
**{loc['name']}** ({loc['type']})
• City: {loc['city'] or 'Unknown'}
• Status: {loc['status']}
• Description: {loc['description'][:100] if loc['description'] else 'Unknown'}...
"""
            location_info.append(info)
        
        return {
            'success': True,
            'message': f'🔍 Found {len(locations)} location(s):\n' + '\n'.join(location_info)
        }
    
    def handle_item_command(self, args):
        """Handle /item commands"""
        campaign_id = get_active_campaign_id()
        if not campaign_id:
            return {'error': 'No active campaign.'}
        
        if not args or args.strip() == 'list':
            return self.list_items_command(campaign_id)
        
        parts = args.split(maxsplit=1)
        subcommand = parts[0].lower()
        
        if subcommand == 'search' and len(parts) > 1:
            return self.search_items_command(campaign_id, parts[1])
        
        return {'error': 'Usage: /item list or /item search <name>'}
    
    def list_items_command(self, campaign_id):
        """List all items"""
        items = search_items(campaign_id)
        
        if not items:
            return {'message': 'No items found in this campaign.'}
        
        item_list = []
        for item in items:
            item_list.append(f"• {item['name']} ({item['type']}) - Status: {item['status']}")
        
        return {
            'success': True,
            'message': f'⚔️ Items in Campaign ({len(items)} total):\n\n' + '\n'.join(item_list)
        }
    
    def search_items_command(self, campaign_id, search_term):
        """Search for items"""
        items = search_items(campaign_id, name=search_term)
        
        if not items:
            return {'message': f'No items found matching "{search_term}".'}
        
        item_info = []
        for item in items:
            info = f"""
**{item['name']}** ({item['type']})
• Status: {item['status']}
• Stats: {item['stats'] if item['stats'] else 'None'}
• Description: {item['backstory'][:100] if item['backstory'] else 'Unknown'}...
"""
            item_info.append(info)
        
        return {
            'success': True,
            'message': f'🔍 Found {len(items)} item(s):\n' + '\n'.join(item_info)
        }
    
    # ==================== DICE COMMANDS ====================
    
    def handle_roll_command(self, args):
        """Handle /roll commands with intelligent context awareness"""
        # Get session ID for tracking
        session_id = get_active_session_id() or 'default'
        
        # Parse the roll command
        roll_params = intelligent_dice.parse_roll_command(f'/roll {args}')
        
        # Get character data
        character_id = session.get('active_character_id')
        if not character_id:
            return {'error': 'No active character. Please create or link a character first.'}
        
        conn = get_db_connection()
        character = conn.execute('SELECT * FROM characters WHERE id = ?', (character_id,)).fetchone()
        conn.close()
        
        if not character:
            return {'error': 'Character not found.'}
        
        character_data = dict(character)
        
        # Determine what to roll
        if roll_params['use_last_suggested']:
            # Use last suggested roll
            last_roll = intelligent_dice.get_last_suggested_roll(session_id)
            if not last_roll:
                return {'error': 'No previous roll suggestion found. Please specify what to roll (e.g., /roll Intelligence + Auspex)'}
            
            # Merge blood surge if specified
            if roll_params['blood_surge']:
                last_roll['blood_surge'] = True
            
            roll_data = last_roll
        else:
            # Use specified roll
            roll_data = roll_params
        
        # Calculate dice pool
        pool_size, description = intelligent_dice.calculate_dice_pool(character_data, roll_data)
        
        if pool_size == 0:
            return {'error': f'Cannot roll {description}. Dice pool is 0.'}
        
        # Get hunger from character
        hunger = character_data.get('hunger', 0)
        
        # Roll the dice
        result = intelligent_dice.roll_dice(pool_size, hunger, difficulty=0)
        
        # Format response
        response = f"🎲 **Rolling {description}**\n"
        response += f"Pool: {pool_size} dice | Hunger: {hunger}\n\n"
        response += result['message']
        
        return {
            'success': True,
            'message': response,
            'roll_result': result
        }
    
    # ==================== HELP COMMAND ====================
    
    def handle_help_command(self, args):
        """Handle /help command"""
        if not args:
            return {
                'success': True,
                'message': '''
📋 **Available Commands**

Type /help <command> for detailed information.

**Campaign Management:**
• /campaign new <name> - Create a new campaign
• /campaign load <name> - Load an existing campaign
• /campaign list - List all campaigns
• /campaign info - Show current campaign info

**Session Management:**
• /session start - Start a new session
• /session end - End the current session
• /session summary - Get session summary

**Database Queries:**
• /npc list - List all NPCs
• /npc search <name> - Search for NPCs
• /location list - List all locations
• /location search <name> - Search for locations
• /item list - List all items
• /item search <name> - Search for items

**Dice Rolling:**
• /roll <pool> <hunger> - Roll dice
• /roll <attribute>+<skill> - Roll attribute + skill

**Help:**
• /help - Show this help message
• /help <command> - Get detailed help for a command
'''
            }
        
        # Detailed help for specific commands
        command = args.strip().lower()
        help_texts = {
            'campaign': 'Campaign management commands. Use: /campaign <new|load|list|info> [args]',
            'session': 'Session management commands. Use: /session <start|end|summary>',
            'npc': 'NPC database commands. Use: /npc <list|search> [name]',
            'location': 'Location database commands. Use: /location <list|search> [name]',
            'item': 'Item database commands. Use: /item <list|search> [name]',
            'roll': 'Dice rolling commands. Use: /roll <pool> <hunger> or /roll <attribute>+<skill>'
        }
        
        if command in help_texts:
            return {'success': True, 'message': f'📋 Help for /{command}:\n\n{help_texts[command]}'}
        
        return {'error': f'No help available for command: {command}'}

# Global command system instance
command_system = CommandSystem()

