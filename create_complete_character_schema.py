#!/usr/bin/env python3
"""
Complete V5 Character Database Schema
Following official Vampire: The Masquerade 5th Edition rules
"""

import sqlite3
import os

def create_complete_character_schema():
    """Create comprehensive character database schema following V5 rules"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'vtm_storyteller.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing characters table if it exists
    cursor.execute('DROP TABLE IF EXISTS characters')
    
    # Create comprehensive characters table
    cursor.execute('''
    CREATE TABLE characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        
        -- Basic Information
        name TEXT NOT NULL,
        concept TEXT,
        chronicle TEXT,
        ambition TEXT,
        desire TEXT,
        predator_type TEXT,
        clan TEXT,
        generation INTEGER DEFAULT 13,
        sire TEXT,
        
        -- Attributes (Physical)
        strength INTEGER DEFAULT 1,
        dexterity INTEGER DEFAULT 1,
        stamina INTEGER DEFAULT 1,
        
        -- Attributes (Social)
        charisma INTEGER DEFAULT 1,
        manipulation INTEGER DEFAULT 1,
        composure INTEGER DEFAULT 1,
        
        -- Attributes (Mental)
        intelligence INTEGER DEFAULT 1,
        wits INTEGER DEFAULT 1,
        resolve INTEGER DEFAULT 1,
        
        -- Skills (Physical)
        athletics INTEGER DEFAULT 0,
        brawl INTEGER DEFAULT 0,
        craft INTEGER DEFAULT 0,
        drive INTEGER DEFAULT 0,
        firearms INTEGER DEFAULT 0,
        larceny INTEGER DEFAULT 0,
        melee INTEGER DEFAULT 0,
        stealth INTEGER DEFAULT 0,
        survival INTEGER DEFAULT 0,
        
        -- Skills (Social)
        animal_ken INTEGER DEFAULT 0,
        etiquette INTEGER DEFAULT 0,
        insight INTEGER DEFAULT 0,
        intimidation INTEGER DEFAULT 0,
        leadership INTEGER DEFAULT 0,
        performance INTEGER DEFAULT 0,
        persuasion INTEGER DEFAULT 0,
        streetwise INTEGER DEFAULT 0,
        subterfuge INTEGER DEFAULT 0,
        
        -- Skills (Mental)
        academics INTEGER DEFAULT 0,
        awareness INTEGER DEFAULT 0,
        finance INTEGER DEFAULT 0,
        investigation INTEGER DEFAULT 0,
        medicine INTEGER DEFAULT 0,
        occult INTEGER DEFAULT 0,
        politics INTEGER DEFAULT 0,
        science INTEGER DEFAULT 0,
        technology INTEGER DEFAULT 0,
        
        -- Skill Specialties (JSON format)
        skill_specialties TEXT DEFAULT '{}',
        
        -- Core Stats
        health INTEGER DEFAULT 3,
        health_damage INTEGER DEFAULT 0,
        willpower INTEGER DEFAULT 3,
        willpower_damage INTEGER DEFAULT 0,
        humanity INTEGER DEFAULT 7,
        humanity_stains INTEGER DEFAULT 0,
        hunger INTEGER DEFAULT 1,
        blood_potency INTEGER DEFAULT 0,
        
        -- Blood Potency Benefits
        blood_surge INTEGER DEFAULT 1,
        mend_amount INTEGER DEFAULT 1,
        power_bonus INTEGER DEFAULT 0,
        rouse_reroll INTEGER DEFAULT 0,
        feeding_penalty INTEGER DEFAULT 0,
        bane_severity INTEGER DEFAULT 0,
        
        -- Resonance & Dyscrasia
        resonance TEXT,
        dyscrasia TEXT,
        
        -- Disciplines (JSON format: {discipline_name: level})
        disciplines TEXT DEFAULT '{}',
        
        -- Powers (JSON format: list of power names)
        powers TEXT DEFAULT '[]',
        
        -- Advantages
        advantages TEXT DEFAULT '[]',
        
        -- Flaws
        flaws TEXT DEFAULT '[]',
        
        -- Backgrounds (JSON format)
        backgrounds TEXT DEFAULT '{}',
        
        -- Clan Bane
        clan_bane TEXT,
        clan_bane_description TEXT,
        
        -- Compulsion
        current_compulsion TEXT,
        
        -- Touchstones & Convictions
        touchstones TEXT DEFAULT '[]',
        convictions TEXT DEFAULT '[]',
        
        -- Chronicle Tenets
        chronicle_tenets TEXT DEFAULT '[]',
        
        -- True Age & Apparent Age
        true_age INTEGER,
        apparent_age INTEGER,
        date_of_birth TEXT,
        date_of_embrace TEXT,
        
        -- Physical Description
        appearance TEXT,
        distinguishing_features TEXT,
        
        -- Equipment & Resources
        equipment TEXT DEFAULT '[]',
        resources INTEGER DEFAULT 0,
        haven TEXT,
        
        -- Experience
        total_experience INTEGER DEFAULT 0,
        spent_experience INTEGER DEFAULT 0,
        
        -- Coterie
        coterie_name TEXT,
        coterie_type TEXT,
        
        -- Relationships (JSON format)
        relationships TEXT DEFAULT '[]',
        
        -- Notes
        notes TEXT,
        backstory TEXT,
        
        -- Demiplane Integration
        demiplane_url TEXT,
        demiplane_character_id TEXT,
        
        -- Metadata
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_played TIMESTAMP,
        
        -- Portrait
        portrait_url TEXT
    )
    ''')
    
    # Create skill_specialties table for detailed tracking
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skill_specialties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER,
        skill_name TEXT NOT NULL,
        specialty TEXT NOT NULL,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
    )
    ''')
    
    # Create character_disciplines table for detailed discipline tracking
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_disciplines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER,
        discipline_name TEXT NOT NULL,
        level INTEGER DEFAULT 1,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
    )
    ''')
    
    # Create character_powers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_powers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER,
        power_name TEXT NOT NULL,
        discipline TEXT NOT NULL,
        level INTEGER NOT NULL,
        cost TEXT,
        dice_pool TEXT,
        description TEXT,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
    )
    ''')
    
    # Create character_advantages table (Merits)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_advantages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER,
        advantage_name TEXT NOT NULL,
        dots INTEGER DEFAULT 1,
        description TEXT,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
    )
    ''')
    
    # Create character_flaws table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_flaws (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER,
        flaw_name TEXT NOT NULL,
        dots INTEGER DEFAULT 1,
        description TEXT,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
    )
    ''')
    
    # Create character_backgrounds table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_backgrounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER,
        background_name TEXT NOT NULL,
        dots INTEGER DEFAULT 1,
        description TEXT,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
    )
    ''')
    
    # Create character_touchstones table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_touchstones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER,
        touchstone_name TEXT NOT NULL,
        conviction TEXT NOT NULL,
        relationship TEXT,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
    )
    ''')
    
    # Create character_equipment table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER,
        item_name TEXT NOT NULL,
        item_type TEXT,
        description TEXT,
        quantity INTEGER DEFAULT 1,
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
    )
    ''')
    
    # Create character_relationships table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS character_relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER,
        npc_name TEXT NOT NULL,
        relationship_type TEXT,
        description TEXT,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Complete V5 character database schema created successfully!")
    print("\n📊 Tables created:")
    print("  - characters (main table with all core stats)")
    print("  - skill_specialties")
    print("  - character_disciplines")
    print("  - character_powers")
    print("  - character_advantages (Merits)")
    print("  - character_flaws")
    print("  - character_backgrounds")
    print("  - character_touchstones")
    print("  - character_equipment")
    print("  - character_relationships")

if __name__ == '__main__':
    create_complete_character_schema()

