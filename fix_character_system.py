#!/usr/bin/env python3
"""
Fix Character System and Add VTM 5e Rules Database
"""

import sqlite3

def create_vtm5e_rules_database():
    """Create comprehensive VTM 5e rules database"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    # Character Creation Rules
    c.execute('''CREATE TABLE IF NOT EXISTS character_creation_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        rule_name TEXT NOT NULL,
        description TEXT NOT NULL,
        points_available INTEGER,
        minimum_value INTEGER,
        maximum_value INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Attributes Rules
    c.execute('''CREATE TABLE IF NOT EXISTS attributes_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attribute_name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        specializations TEXT
    )''')
    
    # Skills Rules
    c.execute('''CREATE TABLE IF NOT EXISTS skills_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        specializations TEXT
    )''')
    
    # Combat Rules
    c.execute('''CREATE TABLE IF NOT EXISTS combat_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_type TEXT NOT NULL,
        rule_name TEXT NOT NULL,
        description TEXT NOT NULL,
        mechanics TEXT,
        examples TEXT
    )''')
    
    # Hunger Rules
    c.execute('''CREATE TABLE IF NOT EXISTS hunger_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hunger_level INTEGER NOT NULL,
        description TEXT NOT NULL,
        effects TEXT NOT NULL,
        feeding_requirements TEXT
    )''')
    
    # Humanity Rules
    c.execute('''CREATE TABLE IF NOT EXISTS humanity_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        humanity_level INTEGER NOT NULL,
        description TEXT NOT NULL,
        stains_to_lose INTEGER,
        bane_severity TEXT,
        effects TEXT
    )''')
    
    # Damage and Healing Rules
    c.execute('''CREATE TABLE IF NOT EXISTS damage_healing_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_type TEXT NOT NULL,
        damage_type TEXT,
        description TEXT NOT NULL,
        mechanics TEXT NOT NULL,
        blood_cost INTEGER,
        time_required TEXT
    )''')
    
    # Experience Rules
    c.execute('''CREATE TABLE IF NOT EXISTS experience_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trait_type TEXT NOT NULL,
        current_rating INTEGER NOT NULL,
        xp_cost INTEGER NOT NULL,
        description TEXT
    )''')
    
    # Clans (already exists, but let's ensure it's complete)
    c.execute('''CREATE TABLE IF NOT EXISTS clans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        bane TEXT,
        compulsion TEXT,
        disciplines TEXT
    )''')
    
    conn.commit()
    conn.close()
    print("✅ VTM 5e rules database schema created")

def populate_character_creation_rules():
    """Populate character creation rules"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    rules = [
        ('Attributes', 'Physical Attributes', 'Distribute 7 dots among Strength, Dexterity, and Stamina', 7, 1, 5),
        ('Attributes', 'Social Attributes', 'Distribute 5 dots among Charisma, Manipulation, and Composure', 5, 1, 5),
        ('Attributes', 'Mental Attributes', 'Distribute 3 dots among Intelligence, Wits, and Resolve', 3, 1, 5),
        ('Skills', 'Primary Skills', 'Distribute 13 dots among your primary skills', 13, 0, 5),
        ('Skills', 'Secondary Skills', 'Distribute 9 dots among your secondary skills', 9, 0, 5),
        ('Skills', 'Tertiary Skills', 'Distribute 5 dots among your tertiary skills', 5, 0, 5),
        ('Disciplines', 'Clan Disciplines', 'Choose 2 dots in clan disciplines', 2, 0, 5),
        ('Disciplines', 'Additional Discipline', 'Choose 1 dot in any discipline', 1, 0, 5),
        ('Advantages', 'Backgrounds', 'Distribute 3 dots among backgrounds', 3, 0, 5),
        ('Advantages', 'Predator Type', 'Choose a predator type (grants dots and flaws)', 0, 0, 0),
        ('Touchstones', 'Convictions', 'Choose 1-3 convictions', 0, 1, 3),
        ('Touchstones', 'Touchstones', 'Choose touchstones equal to your convictions', 0, 1, 3),
        ('Final Touches', 'Humanity', 'Starting Humanity is 7', 0, 1, 10),
        ('Final Touches', 'Health', 'Health = Stamina + 3', 0, 3, 8),
        ('Final Touches', 'Willpower', 'Willpower = Composure + Resolve', 0, 2, 10)
    ]
    
    for rule in rules:
        c.execute('''INSERT OR IGNORE INTO character_creation_rules 
                    (category, rule_name, description, points_available, minimum_value, maximum_value)
                    VALUES (?, ?, ?, ?, ?, ?)''', rule)
    
    conn.commit()
    conn.close()
    print("✅ Character creation rules populated")

def populate_attributes():
    """Populate attributes with descriptions"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    attributes = [
        # Physical
        ('Strength', 'Physical', 'Physical power and muscle', 'Grip, Lifting, Punching'),
        ('Dexterity', 'Physical', 'Agility, speed, and precision', 'Acrobatics, Sleight of Hand, Stealth'),
        ('Stamina', 'Physical', 'Endurance and resilience', 'Endurance, Resistance, Toughness'),
        # Social
        ('Charisma', 'Social', 'Charm, magnetism, and likability', 'Leadership, Seduction, Performance'),
        ('Manipulation', 'Social', 'Influence, persuasion, and deception', 'Lying, Negotiation, Subterfuge'),
        ('Composure', 'Social', 'Poise, self-control, and grace under pressure', 'Calm, Restraint, Poker Face'),
        # Mental
        ('Intelligence', 'Mental', 'Memory, reasoning, and analytical ability', 'Research, Analysis, Memory'),
        ('Wits', 'Mental', 'Quick thinking, perception, and reaction', 'Awareness, Initiative, Cunning'),
        ('Resolve', 'Mental', 'Determination, focus, and willpower', 'Concentration, Determination, Courage')
    ]
    
    for attr in attributes:
        c.execute('''INSERT OR IGNORE INTO attributes_rules 
                    (attribute_name, category, description, specializations)
                    VALUES (?, ?, ?, ?)''', attr)
    
    conn.commit()
    conn.close()
    print("✅ Attributes populated")

def populate_skills():
    """Populate skills with descriptions"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    skills = [
        # Physical Skills
        ('Athletics', 'Physical', 'Running, jumping, climbing, swimming', 'Acrobatics, Climbing, Parkour, Swimming'),
        ('Brawl', 'Physical', 'Unarmed combat and wrestling', 'Dirty Fighting, Grappling, Throws, Biting'),
        ('Craft', 'Physical', 'Creating and repairing objects', 'Carpentry, Mechanics, Sculpting, Painting'),
        ('Drive', 'Physical', 'Operating vehicles', 'Motorcycles, Pursuit, Stunts, Off-road'),
        ('Firearms', 'Physical', 'Using guns and ranged weapons', 'Pistols, Rifles, Shotguns, Archery'),
        ('Melee', 'Physical', 'Armed combat with melee weapons', 'Swords, Clubs, Stakes, Improvised'),
        ('Larceny', 'Physical', 'Theft, lockpicking, and security', 'Lockpicking, Pickpocketing, Hotwiring, Security'),
        ('Stealth', 'Physical', 'Moving unseen and unheard', 'Hiding, Shadowing, Silent Movement, Camouflage'),
        ('Survival', 'Physical', 'Wilderness skills and tracking', 'Tracking, Foraging, Navigation, Weather'),
        # Social Skills
        ('Animal Ken', 'Social', 'Understanding and influencing animals', 'Dogs, Horses, Wild Animals, Training'),
        ('Etiquette', 'Social', 'Social grace and protocol', 'High Society, Street, Elysium, Business'),
        ('Insight', 'Social', 'Reading people and detecting lies', 'Motives, Lies, Desires, Vices'),
        ('Intimidation', 'Social', 'Coercion and threats', 'Physical, Veiled, Torture, Staredown'),
        ('Leadership', 'Social', 'Inspiring and commanding others', 'Command, Inspiration, Military, Praxis'),
        ('Performance', 'Social', 'Entertaining and artistic expression', 'Acting, Music, Dance, Oratory'),
        ('Persuasion', 'Social', 'Convincing and negotiating', 'Negotiation, Seduction, Sales, Fast Talk'),
        ('Streetwise', 'Social', 'Urban survival and criminal knowledge', 'Black Market, Gangs, Rumors, Drugs'),
        ('Subterfuge', 'Social', 'Deception and misdirection', 'Lying, Disguise, Impersonation, Misdirection'),
        # Mental Skills
        ('Academics', 'Mental', 'Scholarly knowledge and research', 'History, Literature, Research, Teaching'),
        ('Awareness', 'Mental', 'Perception and alertness', 'Ambushes, Searching, Sensing Danger, Traps'),
        ('Finance', 'Mental', 'Money management and economics', 'Accounting, Investment, Appraisal, Embezzlement'),
        ('Investigation', 'Mental', 'Gathering clues and solving mysteries', 'Forensics, Profiling, Searching, Deduction'),
        ('Medicine', 'Mental', 'Healing and medical knowledge', 'First Aid, Surgery, Pathology, Pharmaceuticals'),
        ('Occult', 'Mental', 'Supernatural lore and mysticism', 'Kindred Lore, Rituals, Ghosts, Magic'),
        ('Politics', 'Mental', 'Political systems and manipulation', 'Bureaucracy, Diplomacy, Camarilla, Anarchs'),
        ('Science', 'Mental', 'Scientific knowledge and method', 'Biology, Chemistry, Physics, Computers'),
        ('Technology', 'Mental', 'Modern technology and computers', 'Hacking, Programming, Electronics, Surveillance')
    ]
    
    for skill in skills:
        c.execute('''INSERT OR IGNORE INTO skills_rules 
                    (skill_name, category, description, specializations)
                    VALUES (?, ?, ?, ?)''', skill)
    
    conn.commit()
    conn.close()
    print("✅ Skills populated")

def populate_combat_rules():
    """Populate combat mechanics"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    combat_rules = [
        ('Initiative', 'Determining Turn Order', 'All combatants roll Wits + Awareness. Highest goes first.', 'Roll: Wits + Awareness. Ties go to higher Wits, then higher Dexterity.', 'A vampire with Wits 3 and Awareness 2 rolls 5 dice.'),
        ('Attack', 'Melee Attack', 'Roll Strength + Brawl or Melee vs target\'s Defense.', 'Roll: Attribute + Skill. Difficulty = target\'s Defense (Dexterity + Athletics). Each success over difficulty = 1 damage.', 'Attacker rolls 6 dice vs Defense 3. Rolls 5 successes = 2 damage.'),
        ('Attack', 'Ranged Attack', 'Roll Composure + Firearms vs difficulty based on range.', 'Close range (0-5m): Difficulty 2. Medium (6-30m): Difficulty 3. Long (31-50m): Difficulty 4.', 'Shooting at 20m requires 3 successes.'),
        ('Defense', 'Dodging', 'Use Dexterity + Athletics as passive defense.', 'Defense = Dexterity + Athletics. Attacker must exceed this to hit.', 'Vampire with Dex 3 + Athletics 2 has Defense 5.'),
        ('Damage', 'Superficial Damage', 'Minor injuries. Halved (round down) when applied to Health.', 'Mortals take full damage. Vampires halve it. Heals quickly with blood.', '4 Superficial damage = 2 actual damage to vampire.'),
        ('Damage', 'Aggravated Damage', 'Serious wounds. Fire, sunlight, werewolf claws. Hard to heal.', 'Taken in full. Cannot be healed during combat. Requires time and blood.', 'Fire does 3 Aggravated = 3 damage, no halving.'),
        ('Healing', 'Mending Superficial Damage', 'Spend 1 Rouse check to heal 1 Superficial damage.', 'Can heal during combat. Roll Hunger die. Success = heal 1 damage.', 'Vampire at 5 Health spends blood to heal to 6.'),
        ('Healing', 'Mending Aggravated Damage', 'Requires one night of rest per point + Rouse check.', 'Cannot heal in combat. 1 night + 1 blood per Aggravated damage.', 'Healing 3 Aggravated takes 3 nights and 3 Rouse checks.'),
        ('Frenzy', 'Fury Frenzy', 'Provoked by anger or humiliation. Attack nearest threat.', 'Roll Humanity vs 2-4 difficulty. Failure = attack nearest enemy/threat.', 'Insulted vampire rolls Humanity 6 vs Difficulty 3.'),
        ('Frenzy', 'Hunger Frenzy', 'Provoked by blood or starvation. Feed on nearest mortal.', 'Roll Humanity vs Hunger. Failure = attack nearest source of blood.', 'Vampire at Hunger 4 sees bleeding mortal. Rolls Humanity vs 4.'),
        ('Frenzy', 'Terror Frenzy', 'Provoked by fire, sunlight, or fear. Flee in panic.', 'Roll Humanity + Composure vs 2-4. Failure = flee in terror.', 'Facing fire, vampire rolls Humanity 6 + Composure 3 vs 4.')
    ]
    
    for rule in combat_rules:
        c.execute('''INSERT OR IGNORE INTO combat_rules 
                    (rule_type, rule_name, description, mechanics, examples)
                    VALUES (?, ?, ?, ?, ?)''', rule)
    
    conn.commit()
    conn.close()
    print("✅ Combat rules populated")

def populate_hunger_rules():
    """Populate Hunger mechanics"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    hunger_rules = [
        (0, 'Sated', 'No Hunger dice. Recently fed.', 'Feed on a full mortal or drink 3+ Blood Potency worth'),
        (1, 'Satisfied', '1 Hunger die. Comfortable but aware of the Beast.', 'Feed on a mortal or drink 2 Blood Potency worth'),
        (2, 'Hungry', '2 Hunger dice. The Beast stirs. Fangs may show.', 'Feed on a mortal or drink 1 Blood Potency worth'),
        (3, 'Starving', '3 Hunger dice. Constant craving. Veins show. Eyes red.', 'Must feed soon. Difficulty 3 to resist feeding'),
        (4, 'Ravenous', '4 Hunger dice. Desperate. Will attack if provoked.', 'Must feed immediately. Difficulty 4 to resist'),
        (5, 'Feral', '5 Hunger dice. The Beast is in control. Will frenzy.', 'Cannot use Disciplines. Automatic frenzy near blood')
    ]
    
    for rule in hunger_rules:
        c.execute('''INSERT OR IGNORE INTO hunger_rules 
                    (hunger_level, description, effects, feeding_requirements)
                    VALUES (?, ?, ?, ?)''', rule)
    
    conn.commit()
    conn.close()
    print("✅ Hunger rules populated")

def populate_humanity_rules():
    """Populate Humanity mechanics"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    humanity_rules = [
        (10, 'Saint', 3, 'None', 'Immune to frenzy. Inspire mortals. Walk in daylight briefly.'),
        (9, 'Heroic', 3, 'Mild', 'Resist frenzy easily. Strong moral compass.'),
        (8, 'Moral', 3, 'Mild', 'Normal human morality. Resist most temptations.'),
        (7, 'Normal', 2, 'Moderate', 'Average mortal. Some moral flexibility.'),
        (6, 'Conflicted', 2, 'Moderate', 'Occasional moral lapses. Rationalize bad acts.'),
        (5, 'Hardened', 2, 'Severe', 'Casual violence. Detached from humanity.'),
        (4, 'Callous', 1, 'Severe', 'Frequent cruelty. Little empathy.'),
        (3, 'Monstrous', 1, 'Terrible', 'Sadistic. Enjoy causing pain.'),
        (2, 'Inhuman', 1, 'Terrible', 'Alien mindset. No human connection.'),
        (1, 'Beast', 1, 'Catastrophic', 'Barely sentient. Constant frenzy risk.'),
        (0, 'Wassail', 0, 'Total', 'Lost to the Beast. NPC. Unplayable.')
    ]
    
    for rule in humanity_rules:
        c.execute('''INSERT OR IGNORE INTO humanity_rules 
                    (humanity_level, description, stains_to_lose, bane_severity, effects)
                    VALUES (?, ?, ?, ?, ?)''', rule)
    
    conn.commit()
    conn.close()
    print("✅ Humanity rules populated")

def populate_experience_rules():
    """Populate XP costs"""
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    xp_rules = [
        ('Attribute', 0, 5, 'Increase Attribute from 0 to 1'),
        ('Attribute', 1, 10, 'Increase Attribute from 1 to 2'),
        ('Attribute', 2, 15, 'Increase Attribute from 2 to 3'),
        ('Attribute', 3, 20, 'Increase Attribute from 3 to 4'),
        ('Attribute', 4, 25, 'Increase Attribute from 4 to 5'),
        ('Skill', 0, 3, 'Increase Skill from 0 to 1'),
        ('Skill', 1, 6, 'Increase Skill from 1 to 2'),
        ('Skill', 2, 9, 'Increase Skill from 2 to 3'),
        ('Skill', 3, 12, 'Increase Skill from 3 to 4'),
        ('Skill', 4, 15, 'Increase Skill from 4 to 5'),
        ('Discipline', 0, 5, 'Learn new Discipline at level 1 (in-clan)'),
        ('Discipline', 0, 7, 'Learn new Discipline at level 1 (out-of-clan)'),
        ('Discipline', 1, 10, 'Increase Discipline from 1 to 2 (in-clan)'),
        ('Discipline', 1, 14, 'Increase Discipline from 1 to 2 (out-of-clan)'),
        ('Discipline', 2, 15, 'Increase Discipline from 2 to 3 (in-clan)'),
        ('Discipline', 2, 21, 'Increase Discipline from 2 to 3 (out-of-clan)'),
        ('Discipline', 3, 20, 'Increase Discipline from 3 to 4 (in-clan)'),
        ('Discipline', 3, 28, 'Increase Discipline from 3 to 4 (out-of-clan)'),
        ('Discipline', 4, 25, 'Increase Discipline from 4 to 5 (in-clan)'),
        ('Discipline', 4, 35, 'Increase Discipline from 4 to 5 (out-of-clan)'),
        ('Background', 0, 3, 'Gain new Background dot'),
        ('Humanity', 0, 10, 'Increase Humanity by 1 (requires Remorse and story)'),
        ('Willpower', 0, 8, 'Increase Willpower by 1 (max 10)')
    ]
    
    for rule in xp_rules:
        c.execute('''INSERT OR IGNORE INTO experience_rules 
                    (trait_type, current_rating, xp_cost, description)
                    VALUES (?, ?, ?, ?)''', rule)
    
    conn.commit()
    conn.close()
    print("✅ Experience rules populated")

if __name__ == '__main__':
    print("🔧 Fixing Character System and Adding VTM 5e Rules...")
    print()
    
    create_vtm5e_rules_database()
    populate_character_creation_rules()
    populate_attributes()
    populate_skills()
    populate_combat_rules()
    populate_hunger_rules()
    populate_humanity_rules()
    populate_experience_rules()
    
    print()
    print("✅ All VTM 5e rules populated successfully!")
    print("📊 Database now includes:")
    print("   - Character creation rules")
    print("   - Attributes (9)")
    print("   - Skills (27)")
    print("   - Combat mechanics")
    print("   - Hunger system (6 levels)")
    print("   - Humanity system (11 levels)")
    print("   - Experience costs")

