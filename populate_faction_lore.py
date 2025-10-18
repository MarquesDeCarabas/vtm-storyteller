#!/usr/bin/env python3
"""
VTM Storyteller - Faction Lore Database Population Script
Adds Camarilla and Anarch faction knowledge to the database
"""

import sqlite3
import json

def init_faction_tables():
    """Create tables for faction lore and content"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    # Factions table
    c.execute('''CREATE TABLE IF NOT EXISTS factions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL UNIQUE,
                  description TEXT,
                  philosophy TEXT,
                  structure TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Faction roles/positions table
    c.execute('''CREATE TABLE IF NOT EXISTS faction_roles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  faction_id INTEGER,
                  role_name TEXT NOT NULL,
                  role_description TEXT,
                  responsibilities TEXT,
                  typical_clans TEXT,
                  FOREIGN KEY (faction_id) REFERENCES factions (id))''')
    
    # Faction cities table
    c.execute('''CREATE TABLE IF NOT EXISTS faction_cities
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  faction_id INTEGER,
                  city_name TEXT NOT NULL,
                  country TEXT,
                  description TEXT,
                  notable_features TEXT,
                  power_structure TEXT,
                  FOREIGN KEY (faction_id) REFERENCES factions (id))''')
    
    # Clan faction relationships
    c.execute('''CREATE TABLE IF NOT EXISTS clan_faction_relations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  clan_name TEXT NOT NULL,
                  faction_id INTEGER,
                  relationship_type TEXT,
                  description TEXT,
                  FOREIGN KEY (faction_id) REFERENCES factions (id))''')
    
    # Lore sheets table
    c.execute('''CREATE TABLE IF NOT EXISTS lore_sheets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  faction_id INTEGER,
                  category TEXT,
                  description TEXT,
                  benefits TEXT,
                  FOREIGN KEY (faction_id) REFERENCES factions (id))''')
    
    # Faction concepts/themes
    c.execute('''CREATE TABLE IF NOT EXISTS faction_themes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  faction_id INTEGER,
                  theme_name TEXT NOT NULL,
                  description TEXT,
                  examples TEXT,
                  FOREIGN KEY (faction_id) REFERENCES factions (id))''')
    
    conn.commit()
    conn.close()
    print("✅ Faction database tables created successfully")

def populate_camarilla_data():
    """Populate Camarilla faction data"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    # Insert Camarilla faction
    c.execute('''INSERT OR IGNORE INTO factions (name, description, philosophy, structure)
                 VALUES (?, ?, ?, ?)''',
              ('Camarilla',
               'The Camarilla is the largest sect of vampires, claiming to uphold the Traditions and maintain the Masquerade',
               'Order, tradition, and the preservation of vampire society through hierarchy and the Masquerade',
               'Feudal hierarchy with Princes ruling cities, supported by Primogen Councils and various court positions'))
    
    faction_id = c.lastrowid if c.lastrowid > 0 else c.execute("SELECT id FROM factions WHERE name='Camarilla'").fetchone()[0]
    
    # Camarilla Court Roles
    roles = [
        ('Prince', 'Ruler of a city domain', 'Maintains order, enforces Traditions, represents the Camarilla', 'Ventrue, Toreador, Tremere'),
        ('Seneschal', 'Second-in-command to the Prince', 'Acts as advisor and regent when Prince is absent', 'Any clan'),
        ('Sheriff', 'Enforcer of the Prince\'s will', 'Maintains order, punishes transgressors, protects the domain', 'Brujah, Nosferatu, Gangrel'),
        ('Scourge', 'Hunter of unauthorized vampires', 'Eliminates thin-bloods and unauthorized kindred', 'Nosferatu, Gangrel'),
        ('Keeper of Elysium', 'Maintains neutral ground', 'Ensures Elysium remains safe and neutral territory', 'Toreador, Ventrue'),
        ('Harpy', 'Social arbiter and gossip', 'Tracks status, spreads information, influences social dynamics', 'Toreador, Ventrue'),
        ('Primogen', 'Clan representative', 'Advises Prince, represents clan interests in the city', 'All clans'),
        ('Whip', 'Assistant to Primogen', 'Enforces clan unity, supports Primogen', 'All clans'),
    ]
    
    for role_name, desc, resp, clans in roles:
        c.execute('''INSERT OR IGNORE INTO faction_roles 
                     (faction_id, role_name, role_description, responsibilities, typical_clans)
                     VALUES (?, ?, ?, ?, ?)''',
                  (faction_id, role_name, desc, resp, clans))
    
    # Camarilla Themes
    themes = [
        ('Feudalism', 'Medieval power structures adapted to modern nights', 'Blood bonds, oaths of fealty, vassalage'),
        ('The Masquerade', 'Hiding vampire existence from mortals', 'Elaborate cover-ups, punishment for breaches'),
        ('Tradition', 'Ancient laws and customs', 'The Six Traditions, respect for elders'),
        ('Politics', 'Complex social maneuvering', 'Boons, status, favors, alliances'),
        ('Elitism', 'Belief in vampire superiority', 'Disdain for thin-bloods, mortal manipulation'),
    ]
    
    for theme_name, desc, examples in themes:
        c.execute('''INSERT OR IGNORE INTO faction_themes 
                     (faction_id, theme_name, description, examples)
                     VALUES (?, ?, ?, ?)''',
                  (faction_id, theme_name, desc, examples))
    
    # Clan relationships with Camarilla
    clan_relations = [
        ('Ventrue', 'Core', 'Founding clan, natural leaders, often hold Prince positions'),
        ('Toreador', 'Core', 'Founding clan, social manipulators, keepers of culture'),
        ('Tremere', 'Core', 'Blood sorcerers, valuable but distrusted, hierarchical'),
        ('Malkavian', 'Core', 'Seers and madmen, unpredictable but insightful'),
        ('Nosferatu', 'Core', 'Information brokers, spies, essential despite appearance'),
        ('Banu Haqim', 'Recent', 'Recently joined, former assassins, proving loyalty'),
        ('Brujah', 'Defected', 'Many left for Anarchs, some remain loyal'),
        ('Gangrel', 'Defected', 'Mostly abandoned Camarilla for independence'),
    ]
    
    for clan, rel_type, desc in clan_relations:
        c.execute('''INSERT OR IGNORE INTO clan_faction_relations 
                     (clan_name, faction_id, relationship_type, description)
                     VALUES (?, ?, ?, ?)''',
                  (clan, faction_id, rel_type, desc))
    
    conn.commit()
    conn.close()
    print("✅ Camarilla data populated successfully")

def populate_anarch_data():
    """Populate Anarch faction data"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    # Insert Anarch faction
    c.execute('''INSERT OR IGNORE INTO factions (name, description, philosophy, structure)
                 VALUES (?, ?, ?, ?)''',
              ('Anarch Movement',
               'The Anarch Movement rejects the tyranny of elders and seeks freedom from oppressive hierarchies',
               'Freedom, equality, and self-determination for all Kindred regardless of generation',
               'Loose confederations with elected Barons, councils, and democratic decision-making'))
    
    faction_id = c.lastrowid if c.lastrowid > 0 else c.execute("SELECT id FROM factions WHERE name='Anarch Movement'").fetchone()[0]
    
    # Anarch Roles
    roles = [
        ('Baron', 'Leader of Anarch territory', 'Maintains order, represents the domain, elected by peers', 'Brujah, Gangrel, any clan'),
        ('Emissary', 'Diplomat and negotiator', 'Handles external relations, negotiates with other factions', 'Any clan'),
        ('Constable', 'Enforcer and protector', 'Maintains security, deals with threats', 'Brujah, Gangrel'),
        ('Sweeper', 'Cleaner and fixer', 'Handles Masquerade breaches, cleans up messes', 'Nosferatu, Gangrel'),
    ]
    
    for role_name, desc, resp, clans in roles:
        c.execute('''INSERT OR IGNORE INTO faction_roles 
                     (faction_id, role_name, role_description, responsibilities, typical_clans)
                     VALUES (?, ?, ?, ?, ?)''',
                  (faction_id, role_name, desc, resp, clans))
    
    # Anarch Themes
    themes = [
        ('Freedom', 'Liberation from elder tyranny', 'Self-governance, rejection of blood bonds'),
        ('Equality', 'All Kindred deserve respect', 'Meritocracy over age, thin-blood acceptance'),
        ('Revolution', 'Overthrowing oppressive systems', 'Direct action, challenging authority'),
        ('Community', 'Collective strength and support', 'Coteries, mutual aid, shared resources'),
        ('Pragmatism', 'Survival over ideology', 'Flexible morality, adaptability'),
    ]
    
    for theme_name, desc, examples in themes:
        c.execute('''INSERT OR IGNORE INTO faction_themes 
                     (faction_id, theme_name, description, examples)
                     VALUES (?, ?, ?, ?)''',
                  (faction_id, theme_name, desc, examples))
    
    # Clan relationships with Anarchs
    clan_relations = [
        ('Brujah', 'Core', 'Founding clan of the movement, passionate revolutionaries'),
        ('Gangrel', 'Core', 'Independent survivors, value freedom above all'),
        ('Caitiff', 'Core', 'Clanless vampires finding acceptance and purpose'),
        ('Thin-Blooded', 'Core', 'Weak-blooded vampires seeking equality and protection'),
        ('Ministry', 'Allied', 'Former Followers of Set, offer temptation and liberation'),
        ('Malkavian', 'Split', 'Some embrace chaos and freedom of the movement'),
        ('Nosferatu', 'Split', 'Information brokers serving both sides'),
        ('Toreador', 'Split', 'Some rebel against Camarilla stuffiness'),
        ('Tremere', 'Split', 'Rare, usually outcasts from the Pyramid'),
        ('Ventrue', 'Rare', 'Uncommon, usually idealists or exiles'),
    ]
    
    for clan, rel_type, desc in clan_relations:
        c.execute('''INSERT OR IGNORE INTO clan_faction_relations 
                     (clan_name, faction_id, relationship_type, description)
                     VALUES (?, ?, ?, ?)''',
                  (clan, faction_id, rel_type, desc))
    
    conn.commit()
    conn.close()
    print("✅ Anarch data populated successfully")

def populate_important_cities():
    """Add important cities from both books"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    camarilla_id = c.execute("SELECT id FROM factions WHERE name='Camarilla'").fetchone()[0]
    anarch_id = c.execute("SELECT id FROM factions WHERE name='Anarch Movement'").fetchone()[0]
    
    # Camarilla cities
    camarilla_cities = [
        ('Vienna', 'Austria', 'Ancient Camarilla stronghold, seat of power', 'Tremere Chantry, Inner Circle presence', 'Prince with strong Primogen Council'),
        ('London', 'United Kingdom', 'Traditional Camarilla city', 'Mithras legacy, complex politics', 'Prince Anne Bowesley'),
        ('Paris', 'France', 'Cultural center of Camarilla', 'Toreador influence, artistic scene', 'Prince Villon'),
        ('Berlin', 'Germany', 'Divided city with complex history', 'East/West tensions, modern politics', 'Prince Wilhelm Waldburg'),
        ('Prague', 'Czech Republic', 'Ancient city with deep history', 'Tremere presence, mystical atmosphere', 'Prince Ecaterina the Wise'),
    ]
    
    for city, country, desc, features, structure in camarilla_cities:
        c.execute('''INSERT OR IGNORE INTO faction_cities 
                     (faction_id, city_name, country, description, notable_features, power_structure)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (camarilla_id, city, country, desc, features, structure))
    
    # Anarch cities
    anarch_cities = [
        ('Los Angeles', 'USA', 'Anarch Free State, major Anarch stronghold', 'Hollywood, diverse population, Baron system', 'Council of Barons'),
        ('San Francisco', 'USA', 'Tech-savvy Anarch domain', 'Silicon Valley influence, progressive politics', 'Baron Jeremy MacNeil'),
        ('Barcelona', 'Spain', 'European Anarch stronghold', 'Mediterranean culture, artistic freedom', 'Rotating Baron system'),
        ('Berlin (Anarch zones)', 'Germany', 'Contested territory with Anarch presence', 'Underground culture, punk aesthetic', 'Multiple Barons'),
    ]
    
    for city, country, desc, features, structure in anarch_cities:
        c.execute('''INSERT OR IGNORE INTO faction_cities 
                     (faction_id, city_name, country, description, notable_features, power_structure)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (anarch_id, city, country, desc, features, structure))
    
    conn.commit()
    conn.close()
    print("✅ City data populated successfully")

def add_lore_sheet_categories():
    """Add lore sheet categories (without reproducing copyrighted content)"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    camarilla_id = c.execute("SELECT id FROM factions WHERE name='Camarilla'").fetchone()[0]
    anarch_id = c.execute("SELECT id FROM factions WHERE name='Anarch Movement'").fetchone()[0]
    
    # Camarilla lore sheet categories (general descriptions only)
    camarilla_lore = [
        ('Descendant of...', 'Lineage', 'Connection to famous sire or bloodline', 'Status benefits, special abilities'),
        ('Court Position', 'Political', 'Holding an official position in Camarilla court', 'Authority, resources, influence'),
        ('Sect Loyalty', 'Ideological', 'Deep commitment to Camarilla ideals', 'Faction benefits, reputation'),
    ]
    
    for name, category, desc, benefits in camarilla_lore:
        c.execute('''INSERT OR IGNORE INTO lore_sheets 
                     (name, faction_id, category, description, benefits)
                     VALUES (?, ?, ?, ?, ?)''',
                  (name, camarilla_id, category, desc, benefits))
    
    # Anarch lore sheet categories
    anarch_lore = [
        ('Revolutionary', 'Ideological', 'Committed to the Anarch cause', 'Respect, resources, connections'),
        ('Baron', 'Political', 'Leadership of Anarch territory', 'Authority, domain control'),
        ('Free Spirit', 'Personal', 'Independent operator within the movement', 'Flexibility, unique abilities'),
    ]
    
    for name, category, desc, benefits in anarch_lore:
        c.execute('''INSERT OR IGNORE INTO lore_sheets 
                     (name, faction_id, category, description, benefits)
                     VALUES (?, ?, ?, ?, ?)''',
                  (name, anarch_id, category, desc, benefits))
    
    conn.commit()
    conn.close()
    print("✅ Lore sheet categories added successfully")

if __name__ == '__main__':
    print("🧛 VTM Storyteller - Populating Faction Lore Database")
    print("=" * 60)
    
    init_faction_tables()
    populate_camarilla_data()
    populate_anarch_data()
    populate_important_cities()
    add_lore_sheet_categories()
    
    print("=" * 60)
    print("✅ All faction data populated successfully!")
    print("\nThe AI Storyteller now has access to:")
    print("  • Camarilla structure, roles, and philosophy")
    print("  • Anarch Movement structure, roles, and philosophy")
    print("  • Important cities in both factions")
    print("  • Clan relationships with each faction")
    print("  • Thematic elements for narrative enhancement")
    print("  • Lore sheet categories for character backgrounds")

