#!/usr/bin/env python3
"""
Campaign Recall System
Search and retrieve NPCs, Locations, and Items from the campaign database
"""

import sqlite3
import json
from typing import List, Dict, Optional

class CampaignRecall:
    def __init__(self, db_path='campaign_data.db'):
        self.db_path = db_path
    
    def search_npcs(self, query: str = None, clan: str = None, faction: str = None, 
                    city: str = None, status: str = 'alive', tags: List[str] = None) -> List[Dict]:
        """Search for NPCs with various filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        sql = 'SELECT * FROM campaign_npcs WHERE 1=1'
        params = []
        
        if query:
            sql += ' AND (name LIKE ? OR real_name LIKE ? OR personality LIKE ?)'
            params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
        
        if clan:
            sql += ' AND clan = ?'
            params.append(clan)
        
        if faction:
            sql += ' AND faction = ?'
            params.append(faction)
        
        if city:
            sql += ' AND primary_location = ?'
            params.append(city)
        
        if status:
            sql += ' AND status = ?'
            params.append(status)
        
        if tags:
            for tag in tags:
                sql += ' AND tags LIKE ?'
                params.append(f'%{tag}%')
        
        c.execute(sql, params)
        results = c.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_npc_by_id(self, npc_id: int) -> Optional[Dict]:
        """Get NPC by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM campaign_npcs WHERE npc_id = ?', (npc_id,))
        result = c.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def get_npc_by_name(self, name: str) -> Optional[Dict]:
        """Get NPC by exact name"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM campaign_npcs WHERE name = ? OR real_name = ?', (name, name))
        result = c.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def format_npc_for_ai(self, npc_data: Dict) -> str:
        """Format NPC data for AI context"""
        if not npc_data:
            return "NPC not found."
        
        # Parse JSON fields
        skills = json.loads(npc_data.get('skills', '{}'))
        disciplines = json.loads(npc_data.get('disciplines', '{}'))
        tags = json.loads(npc_data.get('tags', '[]'))
        
        output = f"""
=== NPC: {npc_data['name']} ===

**Basic Info:**
- Real Name: {npc_data.get('real_name', 'Unknown')}
- Clan: {npc_data.get('clan', 'Unknown')}
- Nature: {npc_data.get('nature', 'Unknown')}
- Faction: {npc_data.get('faction', 'Independent')}
- Position: {npc_data.get('position', 'None')}
- Location: {npc_data.get('primary_location', 'Unknown')}
- Status: {npc_data.get('status', 'alive')}

**Attributes:**
- Physical: Strength {npc_data.get('strength', 1)}, Dexterity {npc_data.get('dexterity', 1)}, Stamina {npc_data.get('stamina', 1)}
- Social: Charisma {npc_data.get('charisma', 1)}, Manipulation {npc_data.get('manipulation', 1)}, Composure {npc_data.get('composure', 1)}
- Mental: Intelligence {npc_data.get('intelligence', 1)}, Wits {npc_data.get('wits', 1)}, Resolve {npc_data.get('resolve', 1)}

**Skills:** {', '.join([f"{k} {v}" for k, v in skills.items()]) if skills else 'None listed'}

**Disciplines:** {', '.join([f"{k} {v}" for k, v in disciplines.items()]) if disciplines else 'None listed'}

**Personality:** {npc_data.get('personality', 'Not described')}

**Appearance:** {npc_data.get('appearance', 'Not described')}

**Quirks:** {npc_data.get('quirks', 'None noted')}

**Clothing Style:** {npc_data.get('clothing_style', 'Not described')}

**Information Specialty:** {npc_data.get('information_specialty', 'None')}

**Backstory:** {npc_data.get('backstory', 'Unknown')}

**Current Activity:** {npc_data.get('current_activity', 'Unknown')}

**Tags:** {', '.join(tags) if tags else 'None'}

**Last Seen:** {npc_data.get('last_seen', 'Unknown')}
"""
        return output.strip()
    
    def search_locations(self, query: str = None, city: str = None, type: str = None,
                        controlled_by: str = None, status: str = 'active', 
                        tags: List[str] = None) -> List[Dict]:
        """Search for locations with various filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        sql = 'SELECT * FROM campaign_locations WHERE 1=1'
        params = []
        
        if query:
            sql += ' AND (name LIKE ? OR description LIKE ? OR atmosphere LIKE ?)'
            params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
        
        if city:
            sql += ' AND city = ?'
            params.append(city)
        
        if type:
            sql += ' AND type = ?'
            params.append(type)
        
        if controlled_by:
            sql += ' AND controlled_by = ?'
            params.append(controlled_by)
        
        if status:
            sql += ' AND status = ?'
            params.append(status)
        
        if tags:
            for tag in tags:
                sql += ' AND tags LIKE ?'
                params.append(f'%{tag}%')
        
        c.execute(sql, params)
        results = c.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_location_by_name(self, name: str) -> Optional[Dict]:
        """Get location by exact name"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM campaign_locations WHERE name = ?', (name,))
        result = c.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def format_location_for_ai(self, location_data: Dict) -> str:
        """Format location data for AI context"""
        if not location_data:
            return "Location not found."
        
        # Parse JSON fields
        rooms = json.loads(location_data.get('rooms', '[]'))
        security = json.loads(location_data.get('security_measures', '[]'))
        supernatural = json.loads(location_data.get('supernatural_elements', '[]'))
        tags = json.loads(location_data.get('tags', '[]'))
        
        output = f"""
=== LOCATION: {location_data['name']} ===

**Basic Info:**
- Type: {location_data.get('type', 'Unknown')}
- City: {location_data.get('city', 'Unknown')}
- District: {location_data.get('district', 'Unknown')}
- Controlled By: {location_data.get('controlled_by', 'Unknown')}
- Status: {location_data.get('status', 'active')}

**Architecture:**
{location_data.get('architecture_style', 'Not described')}

**Atmosphere:**
{location_data.get('atmosphere', 'Not described')}

**Key Rooms:**
"""
        for room in rooms:
            output += f"\n- {room.get('name', 'Unnamed Room')}: {room.get('description', 'No description')}"
        
        if not rooms:
            output += "\nNo rooms listed."
        
        output += f"\n\n**Hidden Passages:**\n{location_data.get('hidden_passages', 'None known')}"
        
        output += "\n\n**Security Measures:**"
        for sec in security:
            output += f"\n- {sec.get('description', 'Unknown security')}"
        if not security:
            output += "\nNo security measures listed."
        
        output += "\n\n**Supernatural Elements:**"
        for sup in supernatural:
            output += f"\n- {sup.get('description', 'Unknown element')}"
        if not supernatural:
            output += "\nNo supernatural elements noted."
        
        output += f"\n\n**History:**\n{location_data.get('history', 'Unknown')}"
        
        output += f"\n\n**Current Condition:**\n{location_data.get('current_condition', 'Unknown')}"
        
        output += f"\n\n**Tags:** {', '.join(tags) if tags else 'None'}"
        
        output += f"\n\n**Last Visited:** {location_data.get('last_visited', 'Never')}"
        
        return output.strip()
    
    def search_items(self, query: str = None, type: str = None, owner: str = None,
                    status: str = 'intact', tags: List[str] = None) -> List[Dict]:
        """Search for items with various filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        sql = 'SELECT * FROM campaign_items WHERE 1=1'
        params = []
        
        if query:
            sql += ' AND (name LIKE ? OR description LIKE ? OR backstory LIKE ?)'
            params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
        
        if type:
            sql += ' AND type = ?'
            params.append(type)
        
        if owner:
            sql += ' AND current_owner = ?'
            params.append(owner)
        
        if status:
            sql += ' AND status = ?'
            params.append(status)
        
        if tags:
            for tag in tags:
                sql += ' AND tags LIKE ?'
                params.append(f'%{tag}%')
        
        c.execute(sql, params)
        results = c.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_item_by_name(self, name: str) -> Optional[Dict]:
        """Get item by exact name"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM campaign_items WHERE name = ?', (name,))
        result = c.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def format_item_for_ai(self, item_data: Dict) -> str:
        """Format item data for AI context"""
        if not item_data:
            return "Item not found."
        
        # Parse JSON fields
        stats = json.loads(item_data.get('stats', '{}'))
        features = json.loads(item_data.get('features', '[]'))
        tags = json.loads(item_data.get('tags', '[]'))
        
        output = f"""
=== ITEM: {item_data['name']} ===

**Basic Info:**
- Type: {item_data.get('type', 'Unknown')}
- Subtype: {item_data.get('subtype', 'Unknown')}
- Rarity: {item_data.get('rarity', 'Unknown')}
- Status: {item_data.get('status', 'intact')}
- Current Owner: {item_data.get('current_owner', 'None')}
- Current Location: {item_data.get('current_location', 'Unknown')}

**Description:**
{item_data.get('description', 'Not described')}

**Stats:**
"""
        for stat_name, stat_value in stats.items():
            output += f"\n- {stat_name}: {stat_value}"
        if not stats:
            output += "\nNo stats listed."
        
        output += "\n\n**Features:**"
        for feature in features:
            output += f"\n- {feature.get('name', 'Unnamed Feature')}: {feature.get('description', 'No description')}"
        if not features:
            output += "\nNo special features."
        
        output += f"\n\n**Backstory:**\n{item_data.get('backstory', 'Unknown')}"
        
        output += f"\n\n**Game Mechanics:**\n{item_data.get('game_mechanics', 'Not specified')}"
        
        output += f"\n\n**Tags:** {', '.join(tags) if tags else 'None'}"
        
        return output.strip()
    
    def recall_for_ai_context(self, query: str, context_type: str = 'all') -> str:
        """
        Comprehensive recall function for AI context
        Returns formatted text ready to be injected into AI prompt
        """
        output = []
        
        if context_type in ['all', 'npc']:
            npcs = self.search_npcs(query=query)
            if npcs:
                output.append("=== RECALLED NPCs ===")
                for npc in npcs[:3]:  # Limit to top 3 results
                    output.append(self.format_npc_for_ai(npc))
                    output.append("\n" + "="*50 + "\n")
        
        if context_type in ['all', 'location']:
            locations = self.search_locations(query=query)
            if locations:
                output.append("=== RECALLED LOCATIONS ===")
                for location in locations[:3]:
                    output.append(self.format_location_for_ai(location))
                    output.append("\n" + "="*50 + "\n")
        
        if context_type in ['all', 'item']:
            items = self.search_items(query=query)
            if items:
                output.append("=== RECALLED ITEMS ===")
                for item in items[:3]:
                    output.append(self.format_item_for_ai(item))
                    output.append("\n" + "="*50 + "\n")
        
        if not output:
            return f"No results found for query: '{query}'"
        
        return "\n".join(output)
    
    def get_all_for_city(self, city: str) -> Dict:
        """Get all NPCs, Locations, and Items for a specific city"""
        return {
            'npcs': self.search_npcs(city=city),
            'locations': self.search_locations(city=city),
            'items': self.search_items(tags=[city])
        }
    
    def get_campaign_summary(self, campaign_id: int) -> Dict:
        """Get summary of all content for a campaign"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Get campaign info
        c.execute('SELECT * FROM campaigns WHERE campaign_id = ?', (campaign_id,))
        campaign = c.fetchone()
        
        # Get counts
        c.execute('SELECT COUNT(*) as count FROM campaign_npcs WHERE origin_campaign_id = ?', (campaign_id,))
        npc_count = c.fetchone()['count']
        
        c.execute('SELECT COUNT(*) as count FROM campaign_locations WHERE origin_campaign_id = ?', (campaign_id,))
        location_count = c.fetchone()['count']
        
        c.execute('SELECT COUNT(*) as count FROM campaign_items WHERE origin_campaign_id = ?', (campaign_id,))
        item_count = c.fetchone()['count']
        
        c.execute('SELECT COUNT(*) as count FROM campaign_events WHERE campaign_id = ?', (campaign_id,))
        event_count = c.fetchone()['count']
        
        conn.close()
        
        return {
            'campaign': dict(campaign) if campaign else None,
            'npc_count': npc_count,
            'location_count': location_count,
            'item_count': item_count,
            'event_count': event_count
        }

if __name__ == "__main__":
    # Test recall system
    recall = CampaignRecall()
    
    print("🔍 Testing Recall System\n")
    
    # Test NPC recall
    print("=== Test 1: Recall The Archivist ===")
    archivist = recall.get_npc_by_name("The Archivist (Real name: René Dubois)")
    if archivist:
        print(recall.format_npc_for_ai(archivist))
    
    print("\n\n=== Test 2: Search Nosferatu NPCs ===")
    nosferatu = recall.search_npcs(clan='Nosferatu')
    print(f"Found {len(nosferatu)} Nosferatu NPCs")
    
    print("\n\n=== Test 3: Comprehensive Recall ===")
    context = recall.recall_for_ai_context("Archivist", context_type='npc')
    print(context)

