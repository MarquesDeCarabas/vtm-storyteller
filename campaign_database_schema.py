#!/usr/bin/env python3
"""
Campaign Database Schema for VTM Storyteller
Persistent storage of NPCs, Locations, Items across multiple campaigns
"""

import sqlite3
import json
from datetime import datetime

def create_campaign_database(db_path='campaign_data.db'):
    """Create comprehensive campaign database with all tables"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # ==================== CAMPAIGNS TABLE ====================
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT,
        chronicle_name TEXT,
        start_date TEXT,
        last_played TEXT,
        status TEXT DEFAULT 'active',
        description TEXT,
        storyteller_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # ==================== NPCS TABLE ====================
    c.execute('''CREATE TABLE IF NOT EXISTS campaign_npcs (
        npc_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        real_name TEXT,
        clan TEXT,
        generation INTEGER,
        sire TEXT,
        
        -- Attributes
        strength INTEGER DEFAULT 1,
        dexterity INTEGER DEFAULT 1,
        stamina INTEGER DEFAULT 1,
        charisma INTEGER DEFAULT 1,
        manipulation INTEGER DEFAULT 1,
        composure INTEGER DEFAULT 1,
        intelligence INTEGER DEFAULT 1,
        wits INTEGER DEFAULT 1,
        resolve INTEGER DEFAULT 1,
        
        -- Core Stats
        health INTEGER DEFAULT 3,
        willpower INTEGER DEFAULT 3,
        humanity INTEGER DEFAULT 7,
        blood_potency INTEGER DEFAULT 0,
        hunger INTEGER DEFAULT 1,
        
        -- Character Details
        nature TEXT,
        demeanor TEXT,
        predator_type TEXT,
        concept TEXT,
        ambition TEXT,
        desire TEXT,
        
        -- Physical Description
        appearance TEXT,
        apparent_age TEXT,
        true_age TEXT,
        height TEXT,
        build TEXT,
        distinguishing_features TEXT,
        
        -- Personality & Behavior
        personality TEXT,
        quirks TEXT,
        speech_pattern TEXT,
        mannerisms TEXT,
        
        -- Skills (JSON)
        skills TEXT,  -- JSON: {"Academics": 3, "Investigation": 4, ...}
        
        -- Disciplines (JSON)
        disciplines TEXT,  -- JSON: {"Obfuscate": 3, "Potence": 2, ...}
        
        -- Advantages & Flaws (JSON)
        advantages TEXT,  -- JSON: ["Resources 3", "Allies 2", ...]
        flaws TEXT,  -- JSON: ["Enemy 2", "Dark Secret", ...]
        
        -- Background & Lore
        backstory TEXT,
        secrets TEXT,
        goals TEXT,
        fears TEXT,
        
        -- Information Specialty (for information brokers)
        information_specialty TEXT,
        
        -- Clothing & Style
        clothing_style TEXT,
        typical_outfit TEXT,
        
        -- Location & Affiliations
        primary_location TEXT,
        territory TEXT,
        coterie TEXT,
        faction TEXT,  -- Camarilla, Anarch, Independent, Sabbat
        position TEXT,  -- Prince, Baron, Primogen, etc.
        
        -- Relationships (JSON)
        allies TEXT,  -- JSON: ["NPC_ID_1", "NPC_ID_2", ...]
        enemies TEXT,
        contacts TEXT,
        
        -- Status & Availability
        status TEXT DEFAULT 'alive',  -- alive, torpor, final_death, missing
        last_seen TEXT,
        current_activity TEXT,
        
        -- Campaign Association
        origin_campaign_id INTEGER,
        available_campaigns TEXT,  -- JSON: [1, 2, 3, ...] (campaign IDs where this NPC is available)
        
        -- Tags for Organization
        tags TEXT,  -- JSON: ["Chicago", "Information Broker", "Nosferatu", ...]
        
        -- Metadata
        created_by TEXT DEFAULT 'AI',  -- 'AI' or 'Player' or 'Storyteller'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Version Control
        version INTEGER DEFAULT 1,
        change_log TEXT,  -- JSON: [{"date": "...", "change": "...", "reason": "..."}]
        
        FOREIGN KEY (origin_campaign_id) REFERENCES campaigns(campaign_id)
    )''')
    
    # ==================== LOCATIONS TABLE ====================
    c.execute('''CREATE TABLE IF NOT EXISTS campaign_locations (
        location_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT,  -- Elysium, Haven, Nightclub, Warehouse, etc.
        city TEXT,
        district TEXT,
        address TEXT,
        
        -- Architecture & Design
        architecture_style TEXT,
        exterior_description TEXT,
        interior_description TEXT,
        
        -- Atmosphere
        atmosphere TEXT,
        scents TEXT,
        sounds TEXT,
        lighting TEXT,
        temperature TEXT,
        
        -- Key Rooms (JSON)
        rooms TEXT,  -- JSON: [{"name": "The Nave", "description": "...", "purpose": "..."}, ...]
        
        -- Features
        hidden_passages TEXT,  -- JSON: [{"location": "...", "leads_to": "...", "difficulty": 3}, ...]
        security_measures TEXT,  -- JSON: [{"type": "Ghouls", "description": "..."}, {"type": "Tremere Wards", ...}]
        supernatural_elements TEXT,  -- JSON: [{"type": "Moving Gargoyles", "description": "..."}, ...]
        
        -- Access & Control
        owner TEXT,  -- NPC name or faction
        controlled_by TEXT,  -- Faction
        access_restrictions TEXT,
        entry_requirements TEXT,
        
        -- Historical Context
        history TEXT,
        original_purpose TEXT,
        conversion_date TEXT,
        significant_events TEXT,  -- JSON: [{"date": "...", "event": "...", "impact": "..."}, ...]
        
        -- NPCs Present (JSON)
        regular_npcs TEXT,  -- JSON: ["NPC_ID_1", "NPC_ID_2", ...] (NPCs commonly found here)
        
        -- Campaign Association
        origin_campaign_id INTEGER,
        available_campaigns TEXT,  -- JSON: [1, 2, 3, ...]
        
        -- Status
        status TEXT DEFAULT 'active',  -- active, destroyed, abandoned, renovated
        last_visited TEXT,
        current_condition TEXT,
        
        -- Tags
        tags TEXT,  -- JSON: ["Vienna", "Camarilla", "Elysium", "Gothic", ...]
        
        -- Metadata
        created_by TEXT DEFAULT 'AI',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Version Control
        version INTEGER DEFAULT 1,
        change_log TEXT,
        
        FOREIGN KEY (origin_campaign_id) REFERENCES campaigns(campaign_id)
    )''')
    
    # ==================== ITEMS TABLE ====================
    c.execute('''CREATE TABLE IF NOT EXISTS campaign_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT,  -- Weapon, Vehicle, Artifact, Equipment, etc.
        subtype TEXT,  -- Motorcycle, Sword, Amulet, etc.
        
        -- Description
        description TEXT,
        appearance TEXT,
        materials TEXT,
        
        -- Stats (JSON - flexible for different item types)
        stats TEXT,  -- JSON: {"speed": 220, "handling": "+2", "armor": 3, ...}
        
        -- Features (JSON)
        features TEXT,  -- JSON: [{"name": "Lurk Mode", "description": "...", "mechanics": "..."}, ...]
        
        -- Game Mechanics
        game_mechanics TEXT,  -- Detailed explanation of how to use in game
        bonuses TEXT,  -- JSON: {"Drive": 3, "Stealth": 2, ...}
        
        -- Backstory & Lore
        backstory TEXT,
        creator TEXT,
        creation_date TEXT,
        significance TEXT,
        
        -- Ownership & Location
        current_owner TEXT,  -- NPC name or Player Character name
        current_location TEXT,  -- Location name or "Carried"
        ownership_history TEXT,  -- JSON: [{"owner": "...", "from": "...", "to": "...", "how": "..."}, ...]
        
        -- Availability
        rarity TEXT,  -- Common, Uncommon, Rare, Legendary, Unique
        value TEXT,  -- Resources equivalent or description
        
        -- Campaign Association
        origin_campaign_id INTEGER,
        available_campaigns TEXT,  -- JSON: [1, 2, 3, ...]
        
        -- Status
        status TEXT DEFAULT 'intact',  -- intact, damaged, destroyed, lost, stolen
        condition TEXT,
        
        -- Tags
        tags TEXT,  -- JSON: ["Brujah", "Motorcycle", "High-Performance", "UV-Protected", ...]
        
        -- Metadata
        created_by TEXT DEFAULT 'AI',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Version Control
        version INTEGER DEFAULT 1,
        change_log TEXT,
        
        FOREIGN KEY (origin_campaign_id) REFERENCES campaigns(campaign_id)
    )''')
    
    # ==================== EVENTS TABLE ====================
    c.execute('''CREATE TABLE IF NOT EXISTS campaign_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        session_number INTEGER,
        event_date TEXT,  -- In-game date
        real_date TEXT,  -- Real-world date
        
        -- Event Details
        title TEXT,
        description TEXT,
        location_id INTEGER,
        
        -- Participants (JSON)
        npcs_involved TEXT,  -- JSON: ["NPC_ID_1", "NPC_ID_2", ...]
        pcs_involved TEXT,  -- JSON: ["PC_ID_1", "PC_ID_2", ...]
        
        -- Outcomes
        outcome TEXT,
        consequences TEXT,
        
        -- Impact
        faction_impact TEXT,  -- JSON: {"Camarilla": "+1 reputation", "Anarchs": "-2 standing"}
        npc_changes TEXT,  -- JSON: [{"npc_id": 1, "change": "Became ally", ...}]
        location_changes TEXT,  -- JSON: [{"location_id": 1, "change": "Now hostile territory", ...}]
        
        -- Tags
        tags TEXT,  -- JSON: ["Combat", "Intrigue", "Investigation", ...]
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
        FOREIGN KEY (location_id) REFERENCES campaign_locations(location_id)
    )''')
    
    # ==================== RELATIONSHIPS TABLE ====================
    c.execute('''CREATE TABLE IF NOT EXISTS npc_relationships (
        relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
        npc_id_1 INTEGER,
        npc_id_2 INTEGER,
        relationship_type TEXT,  -- Ally, Enemy, Sire, Childe, Rival, Lover, etc.
        strength INTEGER DEFAULT 0,  -- -5 (bitter enemies) to +5 (close allies)
        description TEXT,
        history TEXT,
        status TEXT DEFAULT 'active',  -- active, broken, complicated
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (npc_id_1) REFERENCES campaign_npcs(npc_id),
        FOREIGN KEY (npc_id_2) REFERENCES campaign_npcs(npc_id)
    )''')
    
    # ==================== INDEXES FOR PERFORMANCE ====================
    c.execute('CREATE INDEX IF NOT EXISTS idx_npcs_name ON campaign_npcs(name)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_npcs_clan ON campaign_npcs(clan)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_npcs_faction ON campaign_npcs(faction)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_npcs_status ON campaign_npcs(status)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_npcs_city ON campaign_npcs(primary_location)')
    
    c.execute('CREATE INDEX IF NOT EXISTS idx_locations_name ON campaign_locations(name)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_locations_city ON campaign_locations(city)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_locations_type ON campaign_locations(type)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_locations_status ON campaign_locations(status)')
    
    c.execute('CREATE INDEX IF NOT EXISTS idx_items_name ON campaign_items(name)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_items_type ON campaign_items(type)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_items_owner ON campaign_items(current_owner)')
    
    c.execute('CREATE INDEX IF NOT EXISTS idx_events_campaign ON campaign_events(campaign_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_events_date ON campaign_events(event_date)')
    
    conn.commit()
    conn.close()
    
    print("✅ Campaign Database schema created successfully!")
    print(f"📊 Tables created:")
    print("   - campaigns")
    print("   - campaign_npcs")
    print("   - campaign_locations")
    print("   - campaign_items")
    print("   - campaign_events")
    print("   - npc_relationships")
    print(f"🔍 Indexes created for optimal search performance")
    
    return True

if __name__ == "__main__":
    create_campaign_database()

