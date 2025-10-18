#!/usr/bin/env python3
"""
Campaign Auto-Save System
Automatically detects and saves AI-generated NPCs, Locations, and Items
"""

import sqlite3
import json
import re
from datetime import datetime

class CampaignAutoSave:
    def __init__(self, db_path='campaign_data.db'):
        self.db_path = db_path
        
    def parse_npc_from_text(self, text, campaign_id=None):
        """Parse NPC information from AI-generated text"""
        npc_data = {
            'name': None,
            'real_name': None,
            'clan': None,
            'nature': None,
            'personality': None,
            'appearance': None,
            'quirks': None,
            'clothing_style': None,
            'information_specialty': None,
            'backstory': None,
            'skills': {},
            'disciplines': {},
            'attributes': {},
            'tags': [],
            'origin_campaign_id': campaign_id,
            'created_by': 'AI'
        }
        
        # Extract NAME
        name_match = re.search(r'NAME:\s*([^\n]+)', text, re.IGNORECASE)
        if name_match:
            npc_data['name'] = name_match.group(1).strip()
            
        # Extract real name from parentheses
        real_name_match = re.search(r'\(Real name:\s*([^)]+)\)', text, re.IGNORECASE)
        if real_name_match:
            npc_data['real_name'] = real_name_match.group(1).strip()
        
        # Extract CLAN
        clan_match = re.search(r'CLAN:\s*([^\n]+)', text, re.IGNORECASE)
        if clan_match:
            npc_data['clan'] = clan_match.group(1).strip()
            npc_data['tags'].append(npc_data['clan'])
        
        # Extract NATURE
        nature_match = re.search(r'NATURE:\s*([^\n]+)', text, re.IGNORECASE)
        if nature_match:
            npc_data['nature'] = nature_match.group(1).strip()
        
        # Extract ATTRIBUTES
        attr_section = re.search(r'ATTRIBUTES:(.*?)(?:SKILLS:|DISCIPLINES:|PERSONALITY:|$)', text, re.IGNORECASE | re.DOTALL)
        if attr_section:
            attr_text = attr_section.group(1)
            # Physical
            strength = re.search(r'Strength\s+(\d+)', attr_text, re.IGNORECASE)
            dexterity = re.search(r'Dexterity\s+(\d+)', attr_text, re.IGNORECASE)
            stamina = re.search(r'Stamina\s+(\d+)', attr_text, re.IGNORECASE)
            # Social
            charisma = re.search(r'Charisma\s+(\d+)', attr_text, re.IGNORECASE)
            manipulation = re.search(r'Manipulation\s+(\d+)', attr_text, re.IGNORECASE)
            composure = re.search(r'Composure\s+(\d+)', attr_text, re.IGNORECASE)
            # Mental
            intelligence = re.search(r'Intelligence\s+(\d+)', attr_text, re.IGNORECASE)
            wits = re.search(r'Wits\s+(\d+)', attr_text, re.IGNORECASE)
            resolve = re.search(r'Resolve\s+(\d+)', attr_text, re.IGNORECASE)
            
            if strength: npc_data['attributes']['strength'] = int(strength.group(1))
            if dexterity: npc_data['attributes']['dexterity'] = int(dexterity.group(1))
            if stamina: npc_data['attributes']['stamina'] = int(stamina.group(1))
            if charisma: npc_data['attributes']['charisma'] = int(charisma.group(1))
            if manipulation: npc_data['attributes']['manipulation'] = int(manipulation.group(1))
            if composure: npc_data['attributes']['composure'] = int(composure.group(1))
            if intelligence: npc_data['attributes']['intelligence'] = int(intelligence.group(1))
            if wits: npc_data['attributes']['wits'] = int(wits.group(1))
            if resolve: npc_data['attributes']['resolve'] = int(resolve.group(1))
        
        # Extract SKILLS
        skills_section = re.search(r'SKILLS:(.*?)(?:DISCIPLINES:|PERSONALITY:|APPEARANCE:|$)', text, re.IGNORECASE | re.DOTALL)
        if skills_section:
            skills_text = skills_section.group(1)
            # Find all skill: value pairs
            skill_matches = re.findall(r'([A-Za-z\s]+?)\s+(\d+)', skills_text)
            for skill_name, skill_value in skill_matches:
                npc_data['skills'][skill_name.strip()] = int(skill_value)
        
        # Extract DISCIPLINES
        disc_section = re.search(r'DISCIPLINES:(.*?)(?:PERSONALITY:|APPEARANCE:|QUIRKS:|$)', text, re.IGNORECASE | re.DOTALL)
        if disc_section:
            disc_text = disc_section.group(1)
            disc_matches = re.findall(r'([A-Za-z\s]+?)\s+(\d+)', disc_text)
            for disc_name, disc_value in disc_matches:
                npc_data['disciplines'][disc_name.strip()] = int(disc_value)
        
        # Extract PERSONALITY
        personality_section = re.search(r'PERSONALITY:(.*?)(?:APPEARANCE:|QUIRKS:|CLOTHING|INFORMATION|$)', text, re.IGNORECASE | re.DOTALL)
        if personality_section:
            npc_data['personality'] = personality_section.group(1).strip()
        
        # Extract APPEARANCE
        appearance_section = re.search(r'APPEARANCE:(.*?)(?:QUIRKS:|CLOTHING|INFORMATION|$)', text, re.IGNORECASE | re.DOTALL)
        if appearance_section:
            npc_data['appearance'] = appearance_section.group(1).strip()
        
        # Extract QUIRKS
        quirks_section = re.search(r'QUIRKS:(.*?)(?:CLOTHING|INFORMATION|$)', text, re.IGNORECASE | re.DOTALL)
        if quirks_section:
            npc_data['quirks'] = quirks_section.group(1).strip()
        
        # Extract CLOTHING STYLE
        clothing_section = re.search(r'CLOTHING STYLE:(.*?)(?:INFORMATION|$)', text, re.IGNORECASE | re.DOTALL)
        if clothing_section:
            npc_data['clothing_style'] = clothing_section.group(1).strip()
        
        # Extract INFORMATION SPECIALTY
        info_section = re.search(r'INFORMATION SPECIALTY:(.*?)$', text, re.IGNORECASE | re.DOTALL)
        if info_section:
            npc_data['information_specialty'] = info_section.group(1).strip()
        
        # Detect city from text
        cities = ['Vienna', 'Paris', 'London', 'Chicago', 'Los Angeles', 'Berlin', 'Barcelona', 'New York', 'Prague']
        for city in cities:
            if city.lower() in text.lower():
                npc_data['tags'].append(city)
                npc_data['primary_location'] = city
                break
        
        # Detect faction
        if 'camarilla' in text.lower():
            npc_data['faction'] = 'Camarilla'
            npc_data['tags'].append('Camarilla')
        elif 'anarch' in text.lower():
            npc_data['faction'] = 'Anarch'
            npc_data['tags'].append('Anarch')
        
        # Detect role
        if 'information broker' in text.lower():
            npc_data['tags'].append('Information Broker')
        
        return npc_data
    
    def parse_location_from_text(self, text, campaign_id=None):
        """Parse Location information from AI-generated text"""
        location_data = {
            'name': None,
            'type': None,
            'city': None,
            'architecture_style': None,
            'atmosphere': None,
            'rooms': [],
            'hidden_passages': None,
            'security_measures': [],
            'supernatural_elements': [],
            'history': None,
            'tags': [],
            'origin_campaign_id': campaign_id,
            'created_by': 'AI'
        }
        
        # Extract NAME
        name_match = re.search(r'NAME:\s*([^\n]+)', text, re.IGNORECASE)
        if name_match:
            location_data['name'] = name_match.group(1).strip()
        
        # Extract LOCATION (city)
        loc_match = re.search(r'LOCATION:\s*([^\n]+)', text, re.IGNORECASE)
        if loc_match:
            location_data['city'] = loc_match.group(1).strip()
            location_data['tags'].append(location_data['city'])
        
        # Extract ARCHITECTURE
        arch_section = re.search(r'ARCHITECTURE:(.*?)(?:ATMOSPHERE:|KEY ROOMS:|$)', text, re.IGNORECASE | re.DOTALL)
        if arch_section:
            location_data['architecture_style'] = arch_section.group(1).strip()
        
        # Extract ATMOSPHERE
        atm_section = re.search(r'ATMOSPHERE:(.*?)(?:KEY ROOMS:|HIDDEN|SECURITY|$)', text, re.IGNORECASE | re.DOTALL)
        if atm_section:
            location_data['atmosphere'] = atm_section.group(1).strip()
        
        # Extract KEY ROOMS
        rooms_section = re.search(r'KEY ROOMS:(.*?)(?:HIDDEN|SECURITY|SUPERNATURAL|$)', text, re.IGNORECASE | re.DOTALL)
        if rooms_section:
            rooms_text = rooms_section.group(1)
            # Find room names (usually preceded by "- " or "The ")
            room_matches = re.findall(r'-\s*([^:]+):(.*?)(?=\n-|\n\n|$)', rooms_text, re.DOTALL)
            for room_name, room_desc in room_matches:
                location_data['rooms'].append({
                    'name': room_name.strip(),
                    'description': room_desc.strip()
                })
        
        # Extract HIDDEN PASSAGES
        hidden_section = re.search(r'HIDDEN PASSAGES:(.*?)(?:SECURITY|SUPERNATURAL|$)', text, re.IGNORECASE | re.DOTALL)
        if hidden_section:
            location_data['hidden_passages'] = hidden_section.group(1).strip()
        
        # Extract SECURITY MEASURES
        security_section = re.search(r'SECURITY MEASURES:(.*?)(?:SUPERNATURAL|$)', text, re.IGNORECASE | re.DOTALL)
        if security_section:
            security_text = security_section.group(1).strip()
            location_data['security_measures'].append({'description': security_text})
        
        # Extract SUPERNATURAL ELEMENTS
        super_section = re.search(r'SUPERNATURAL ELEMENTS:(.*?)$', text, re.IGNORECASE | re.DOTALL)
        if super_section:
            super_text = super_section.group(1).strip()
            location_data['supernatural_elements'].append({'description': super_text})
        
        # Detect type
        if 'elysium' in text.lower():
            location_data['type'] = 'Elysium'
            location_data['tags'].append('Elysium')
        elif 'cathedral' in text.lower():
            location_data['type'] = 'Cathedral'
            location_data['tags'].append('Cathedral')
        elif 'haven' in text.lower():
            location_data['type'] = 'Haven'
            location_data['tags'].append('Haven')
        
        # Detect faction
        if 'camarilla' in text.lower():
            location_data['controlled_by'] = 'Camarilla'
            location_data['tags'].append('Camarilla')
        elif 'anarch' in text.lower():
            location_data['controlled_by'] = 'Anarch'
            location_data['tags'].append('Anarch')
        
        # Detect architecture style
        if 'gothic' in text.lower():
            location_data['tags'].append('Gothic')
        
        return location_data
    
    def parse_item_from_text(self, text, campaign_id=None):
        """Parse Item information from AI-generated text"""
        item_data = {
            'name': None,
            'type': None,
            'description': None,
            'stats': {},
            'features': [],
            'backstory': None,
            'game_mechanics': None,
            'tags': [],
            'origin_campaign_id': campaign_id,
            'created_by': 'AI'
        }
        
        # Extract NAME
        name_match = re.search(r'NAME:\s*([^\n]+)', text, re.IGNORECASE)
        if name_match:
            item_data['name'] = name_match.group(1).strip()
        
        # Extract BACKSTORY
        backstory_section = re.search(r'BACKSTORY:(.*?)(?:STATS|FEATURES|$)', text, re.IGNORECASE | re.DOTALL)
        if backstory_section:
            item_data['backstory'] = backstory_section.group(1).strip()
        
        # Extract STATS & FEATURES
        stats_section = re.search(r'STATS.*?FEATURES:(.*?)(?:SPECIAL FEATURES:|GAME MECHANICS:|$)', text, re.IGNORECASE | re.DOTALL)
        if stats_section:
            stats_text = stats_section.group(1)
            # Speed
            speed_match = re.search(r'Speed.*?(\d+)\s*mph', stats_text, re.IGNORECASE)
            if speed_match:
                item_data['stats']['speed_mph'] = int(speed_match.group(1))
            # Handling
            handling_match = re.search(r'Handling.*?\+(\d+)', stats_text, re.IGNORECASE)
            if handling_match:
                item_data['stats']['handling_bonus'] = int(handling_match.group(1))
            # Armor
            armor_match = re.search(r'Armor.*?(\d+)\s*health', stats_text, re.IGNORECASE)
            if armor_match:
                item_data['stats']['armor_health'] = int(armor_match.group(1))
        
        # Extract SPECIAL FEATURES
        features_section = re.search(r'SPECIAL FEATURES:(.*?)(?:GAME MECHANICS:|$)', text, re.IGNORECASE | re.DOTALL)
        if features_section:
            features_text = features_section.group(1)
            # Find feature names
            feature_matches = re.findall(r'-\s*([^:]+):(.*?)(?=\n-|\n\n|$)', features_text, re.DOTALL)
            for feature_name, feature_desc in feature_matches:
                item_data['features'].append({
                    'name': feature_name.strip(),
                    'description': feature_desc.strip()
                })
        
        # Extract GAME MECHANICS
        mechanics_section = re.search(r'GAME MECHANICS:(.*?)$', text, re.IGNORECASE | re.DOTALL)
        if mechanics_section:
            item_data['game_mechanics'] = mechanics_section.group(1).strip()
        
        # Detect type
        if 'motorcycle' in text.lower() or 'bike' in text.lower():
            item_data['type'] = 'Vehicle'
            item_data['subtype'] = 'Motorcycle'
            item_data['tags'].append('Motorcycle')
        elif 'weapon' in text.lower():
            item_data['type'] = 'Weapon'
            item_data['tags'].append('Weapon')
        
        # Detect clan association
        clans = ['Brujah', 'Gangrel', 'Malkavian', 'Nosferatu', 'Toreador', 'Tremere', 'Ventrue']
        for clan in clans:
            if clan.lower() in text.lower():
                item_data['tags'].append(clan)
                break
        
        return item_data
    
    def save_npc(self, npc_data):
        """Save NPC to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if NPC already exists
        c.execute('SELECT npc_id FROM campaign_npcs WHERE name = ?', (npc_data['name'],))
        existing = c.fetchone()
        
        if existing:
            print(f"⚠️  NPC '{npc_data['name']}' already exists in database")
            conn.close()
            return existing[0]
        
        # Insert new NPC
        c.execute('''INSERT INTO campaign_npcs (
            name, real_name, clan, nature, personality, appearance, quirks,
            clothing_style, information_specialty, skills, disciplines,
            strength, dexterity, stamina, charisma, manipulation, composure,
            intelligence, wits, resolve, primary_location, faction, tags,
            origin_campaign_id, created_by, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            npc_data['name'],
            npc_data.get('real_name'),
            npc_data.get('clan'),
            npc_data.get('nature'),
            npc_data.get('personality'),
            npc_data.get('appearance'),
            npc_data.get('quirks'),
            npc_data.get('clothing_style'),
            npc_data.get('information_specialty'),
            json.dumps(npc_data.get('skills', {})),
            json.dumps(npc_data.get('disciplines', {})),
            npc_data.get('attributes', {}).get('strength', 1),
            npc_data.get('attributes', {}).get('dexterity', 1),
            npc_data.get('attributes', {}).get('stamina', 1),
            npc_data.get('attributes', {}).get('charisma', 1),
            npc_data.get('attributes', {}).get('manipulation', 1),
            npc_data.get('attributes', {}).get('composure', 1),
            npc_data.get('attributes', {}).get('intelligence', 1),
            npc_data.get('attributes', {}).get('wits', 1),
            npc_data.get('attributes', {}).get('resolve', 1),
            npc_data.get('primary_location'),
            npc_data.get('faction'),
            json.dumps(npc_data.get('tags', [])),
            npc_data.get('origin_campaign_id'),
            npc_data.get('created_by', 'AI'),
            'alive'
        ))
        
        npc_id = c.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ NPC '{npc_data['name']}' saved to database (ID: {npc_id})")
        return npc_id
    
    def save_location(self, location_data):
        """Save Location to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if location already exists
        c.execute('SELECT location_id FROM campaign_locations WHERE name = ?', (location_data['name'],))
        existing = c.fetchone()
        
        if existing:
            print(f"⚠️  Location '{location_data['name']}' already exists in database")
            conn.close()
            return existing[0]
        
        # Insert new location
        c.execute('''INSERT INTO campaign_locations (
            name, type, city, architecture_style, atmosphere, rooms,
            hidden_passages, security_measures, supernatural_elements,
            controlled_by, tags, origin_campaign_id, created_by, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            location_data['name'],
            location_data.get('type'),
            location_data.get('city'),
            location_data.get('architecture_style'),
            location_data.get('atmosphere'),
            json.dumps(location_data.get('rooms', [])),
            location_data.get('hidden_passages'),
            json.dumps(location_data.get('security_measures', [])),
            json.dumps(location_data.get('supernatural_elements', [])),
            location_data.get('controlled_by'),
            json.dumps(location_data.get('tags', [])),
            location_data.get('origin_campaign_id'),
            location_data.get('created_by', 'AI'),
            'active'
        ))
        
        location_id = c.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Location '{location_data['name']}' saved to database (ID: {location_id})")
        return location_id
    
    def save_item(self, item_data):
        """Save Item to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if item already exists
        c.execute('SELECT item_id FROM campaign_items WHERE name = ?', (item_data['name'],))
        existing = c.fetchone()
        
        if existing:
            print(f"⚠️  Item '{item_data['name']}' already exists in database")
            conn.close()
            return existing[0]
        
        # Insert new item
        c.execute('''INSERT INTO campaign_items (
            name, type, subtype, backstory, stats, features,
            game_mechanics, tags, origin_campaign_id, created_by, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            item_data['name'],
            item_data.get('type'),
            item_data.get('subtype'),
            item_data.get('backstory'),
            json.dumps(item_data.get('stats', {})),
            json.dumps(item_data.get('features', [])),
            item_data.get('game_mechanics'),
            json.dumps(item_data.get('tags', [])),
            item_data.get('origin_campaign_id'),
            item_data.get('created_by', 'AI'),
            'intact'
        ))
        
        item_id = c.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Item '{item_data['name']}' saved to database (ID: {item_id})")
        return item_id
    
    def auto_detect_and_save(self, ai_response_text, campaign_id=None):
        """Automatically detect type of content and save to database"""
        saved_items = []
        
        # Detect if it's an NPC
        if re.search(r'(CLAN:|DISCIPLINES:|ATTRIBUTES:)', ai_response_text, re.IGNORECASE):
            npc_data = self.parse_npc_from_text(ai_response_text, campaign_id)
            if npc_data['name']:
                npc_id = self.save_npc(npc_data)
                saved_items.append(('NPC', npc_data['name'], npc_id))
        
        # Detect if it's a Location
        if re.search(r'(ARCHITECTURE:|KEY ROOMS:|ATMOSPHERE:)', ai_response_text, re.IGNORECASE):
            location_data = self.parse_location_from_text(ai_response_text, campaign_id)
            if location_data['name']:
                location_id = self.save_location(location_data)
                saved_items.append(('Location', location_data['name'], location_id))
        
        # Detect if it's an Item
        if re.search(r'(BACKSTORY:.*?(motorcycle|weapon|vehicle)|STATS.*?FEATURES:)', ai_response_text, re.IGNORECASE | re.DOTALL):
            item_data = self.parse_item_from_text(ai_response_text, campaign_id)
            if item_data['name']:
                item_id = self.save_item(item_data)
                saved_items.append(('Item', item_data['name'], item_id))
        
        return saved_items

if __name__ == "__main__":
    # Test with The Archivist
    test_npc_text = """
    NAME: The Archivist (Real name: René Dubois)
    CLAN: Nosferatu
    NATURE: Plotter
    ATTRIBUTES:
    - Physical: Strength 2, Dexterity 3, Stamina 3
    - Social: Charisma 2, Manipulation 4, Composure 3
    - Mental: Intelligence 4, Wits 3, Resolve 4
    SKILLS:
    - Talents: Insight 3, Persuasion 3, Subterfuge 3
    - Skills: Technology 4, Investigation 3, Stealth 3
    - Knowledges: Academics (History) 4, Politics 2, Occult 2
    DISCIPLINES: Obfuscate 3, Potence 2, Animalism 1
    PERSONALITY: The Archivist is introverted and meticulous, with an insatiable curiosity.
    APPEARANCE: Standing at a mere 5'4", he possesses an emaciated frame and elongated limbs.
    QUIRKS: The Archivist has an uncanny habit of remembering every single piece of information.
    CLOTHING STYLE: He is often seen in a tattered, centuries-old monk's robe.
    INFORMATION SPECIALTY: The Archivist specializes in historical records, ancient treaties, old bloodline genealogies.
    """
    
    auto_save = CampaignAutoSave()
    saved = auto_save.auto_detect_and_save(test_npc_text)
    print(f"\n📊 Auto-saved {len(saved)} items:")
    for item_type, item_name, item_id in saved:
        print(f"   - {item_type}: {item_name} (ID: {item_id})")

