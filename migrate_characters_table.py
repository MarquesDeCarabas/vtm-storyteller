#!/usr/bin/env python3
"""
Migrate characters table to include all necessary columns
"""

import sqlite3
import json

def migrate_characters_table():
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    # Get existing data
    try:
        c.execute('SELECT * FROM characters')
        existing_data = c.fetchall()
        c.execute("PRAGMA table_info(characters)")
        old_columns = [col[1] for col in c.fetchall()]
        print(f"📊 Found {len(existing_data)} existing characters")
        print(f"📋 Old columns: {old_columns}")
    except:
        existing_data = []
        old_columns = []
    
    # Drop old table
    c.execute('DROP TABLE IF EXISTS characters')
    
    # Create new table with all columns
    c.execute('''CREATE TABLE characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        clan TEXT NOT NULL,
        concept TEXT,
        chronicle_id INTEGER,
        generation INTEGER DEFAULT 13,
        sire TEXT,
        predator_type TEXT,
        ambition TEXT,
        desire TEXT,
        attributes TEXT DEFAULT '{}',
        skills TEXT DEFAULT '{}',
        disciplines TEXT DEFAULT '{}',
        backgrounds TEXT DEFAULT '{}',
        health INTEGER DEFAULT 3,
        willpower INTEGER DEFAULT 2,
        humanity INTEGER DEFAULT 7,
        hunger INTEGER DEFAULT 1,
        experience INTEGER DEFAULT 0,
        demiplane_url TEXT,
        portrait BLOB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chronicle_id) REFERENCES chronicles(id)
    )''')
    
    print("✅ New characters table created with all columns")
    
    # Migrate existing data if any
    if existing_data:
        for row in existing_data:
            try:
                # Map old data to new schema
                old_data = dict(zip(old_columns, row))
                
                c.execute('''INSERT INTO characters 
                            (name, clan, generation, attributes, disciplines, backgrounds)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (old_data.get('name', 'Unknown'),
                          old_data.get('clan', 'Unknown'),
                          old_data.get('generation', 13),
                          old_data.get('attributes', '{}'),
                          old_data.get('disciplines', '{}'),
                          old_data.get('backgrounds', '{}')))
                print(f"  ✅ Migrated: {old_data.get('name')}")
            except Exception as e:
                print(f"  ⚠️ Could not migrate row: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Migration complete!")

if __name__ == '__main__':
    print("🔧 Migrating characters table...")
    migrate_characters_table()

