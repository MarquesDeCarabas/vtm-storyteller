#!/usr/bin/env python3
"""
Enhanced Character System for VTM Storyteller
- Complete character creation with power levels
- Demiplane import via JSON/manual entry
- Wiki integration for AI knowledge
- Character sheet context for AI narration
"""

import sqlite3
import json
import os
from datetime import datetime

# V5 Character Creation Rules with Power Levels
CHARACTER_POWER_LEVELS = {
    'neonate': {
        'name': 'Neonate (Standard)',
        'description': 'Newly embraced vampire, following standard V5 creation rules',
        'bonus_xp': 0,
        'bonus_attributes': 0,
        'bonus_skills': 0,
        'bonus_disciplines': 0,
        'bonus_advantages': 0,
        'blood_potency': 0,
        'generation': 13
    },
    'ancilla': {
        'name': 'Ancilla (Experienced)',
        'description': 'Vampire with 50-200 years of unlife',
        'bonus_xp': 150,
        'bonus_attributes': 3,
        'bonus_skills': 10,
        'bonus_disciplines': 2,
        'bonus_advantages': 5,
        'blood_potency': 1,
        'generation': 12
    },
    'elder': {
        'name': 'Elder (Ancient)',
        'description': 'Vampire with 300+ years of unlife',
        'bonus_xp': 300,
        'bonus_attributes': 6,
        'bonus_skills': 20,
        'bonus_disciplines': 4,
        'bonus_advantages': 10,
        'blood_potency': 2,
        'generation': 10
    },
    'custom': {
        'name': 'Custom Power Level',
        'description': 'Fully customizable character power',
        'bonus_xp': 0,  # User defined
        'bonus_attributes': 0,  # User defined
        'bonus_skills': 0,  # User defined
        'bonus_disciplines': 0,  # User defined
        'bonus_advantages': 0,  # User defined
        'blood_potency': 0,  # User defined
        'generation': 13  # User defined
    }
}

# Standard V5 Creation Rules (Neonate)
STANDARD_CREATION_RULES = {
    'attributes': {
        'base': 1,  # All attributes start at 1
        'primary': 7,
        'secondary': 5,
        'tertiary': 3
    },
    'skills': {
        'primary': 13,
        'secondary': 9,
        'tertiary': 5,
        'specialties': 3
    },
    'disciplines': {
        'clan': 2,  # 2 dots in clan disciplines
        'caitiff': 2  # Caitiff gets 2 in any
    },
    'advantages': {
        'total': 7  # Backgrounds + Merits
    },
    'humanity': 7,
    'health_base': 3,  # Stamina + 3
    'willpower_base': 3  # Composure + Resolve
}

def calculate_derived_stats(character_data):
    """Calculate Health, Willpower, and other derived stats"""
    
    # Health = Stamina + 3
    stamina = character_data.get('stamina', 1)
    health = stamina + 3
    
    # Willpower = Composure + Resolve
    composure = character_data.get('composure', 1)
    resolve = character_data.get('resolve', 1)
    willpower = composure + resolve
    
    # Blood Potency determines various mechanics
    blood_potency = character_data.get('blood_potency', 0)
    
    blood_potency_table = {
        0: {'surge': 1, 'mend': 1, 'power_bonus': 0, 'rouse_reroll': 0, 'feeding_penalty': 0, 'bane_severity': 0},
        1: {'surge': 2, 'mend': 1, 'power_bonus': 0, 'rouse_reroll': 0, 'feeding_penalty': 0, 'bane_severity': 1},
        2: {'surge': 2, 'mend': 2, 'power_bonus': 1, 'rouse_reroll': 1, 'feeding_penalty': 0, 'bane_severity': 1},
        3: {'surge': 3, 'mend': 2, 'power_bonus': 1, 'rouse_reroll': 1, 'feeding_penalty': 1, 'bane_severity': 2},
        4: {'surge': 3, 'mend': 3, 'power_bonus': 2, 'rouse_reroll': 2, 'feeding_penalty': 1, 'bane_severity': 2},
        5: {'surge': 4, 'mend': 3, 'power_bonus': 2, 'rouse_reroll': 2, 'feeding_penalty': 2, 'bane_severity': 3},
        6: {'surge': 4, 'mend': 3, 'power_bonus': 3, 'rouse_reroll': 3, 'feeding_penalty': 2, 'bane_severity': 3},
        7: {'surge': 5, 'mend': 3, 'power_bonus': 3, 'rouse_reroll': 3, 'feeding_penalty': 3, 'bane_severity': 3},
        8: {'surge': 5, 'mend': 4, 'power_bonus': 4, 'rouse_reroll': 4, 'feeding_penalty': 3, 'bane_severity': 4},
        9: {'surge': 6, 'mend': 4, 'power_bonus': 4, 'rouse_reroll': 4, 'feeding_penalty': 4, 'bane_severity': 4},
        10: {'surge': 6, 'mend': 5, 'power_bonus': 5, 'rouse_reroll': 5, 'feeding_penalty': 4, 'bane_severity': 5}
    }
    
    bp_benefits = blood_potency_table.get(blood_potency, blood_potency_table[0])
    
    return {
        'health': health,
        'willpower': willpower,
        'blood_surge': bp_benefits['surge'],
        'mend_amount': bp_benefits['mend'],
        'power_bonus': bp_benefits['power_bonus'],
        'rouse_reroll': bp_benefits['rouse_reroll'],
        'feeding_penalty': bp_benefits['feeding_penalty'],
        'bane_severity': bp_benefits['bane_severity']
    }

def create_character_with_power_level(character_data, power_level='neonate', custom_bonuses=None):
    """
    Create a character with specified power level
    
    Args:
        character_data: Dict with character information
        power_level: 'neonate', 'ancilla', 'elder', or 'custom'
        custom_bonuses: Dict with custom bonus values (for 'custom' power level)
    """
    
    db_path = os.path.join(os.path.dirname(__file__), 'vtm_storyteller.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get power level bonuses
    if power_level == 'custom' and custom_bonuses:
        bonuses = custom_bonuses
    else:
        bonuses = CHARACTER_POWER_LEVELS.get(power_level, CHARACTER_POWER_LEVELS['neonate'])
    
    # Calculate derived stats
    derived = calculate_derived_stats(character_data)
    
    # Merge bonuses into character data
    character_data['blood_potency'] = bonuses.get('blood_potency', 0)
    character_data['generation'] = bonuses.get('generation', 13)
    character_data['total_experience'] = bonuses.get('bonus_xp', 0)
    character_data['health'] = derived['health']
    character_data['willpower'] = derived['willpower']
    character_data['blood_surge'] = derived['blood_surge']
    character_data['mend_amount'] = derived['mend_amount']
    character_data['power_bonus'] = derived['power_bonus']
    character_data['rouse_reroll'] = derived['rouse_reroll']
    character_data['feeding_penalty'] = derived['feeding_penalty']
    character_data['bane_severity'] = derived['bane_severity']
    
    # Insert character into database
    cursor.execute('''
    INSERT INTO characters (
        user_id, name, concept, chronicle, ambition, desire,
        predator_type, clan, generation, sire,
        strength, dexterity, stamina,
        charisma, manipulation, composure,
        intelligence, wits, resolve,
        health, willpower, humanity, hunger, blood_potency,
        blood_surge, mend_amount, power_bonus, rouse_reroll,
        feeding_penalty, bane_severity,
        total_experience, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        character_data.get('user_id'),
        character_data.get('name'),
        character_data.get('concept'),
        character_data.get('chronicle'),
        character_data.get('ambition'),
        character_data.get('desire'),
        character_data.get('predator_type'),
        character_data.get('clan'),
        character_data.get('generation'),
        character_data.get('sire'),
        character_data.get('strength', 1),
        character_data.get('dexterity', 1),
        character_data.get('stamina', 1),
        character_data.get('charisma', 1),
        character_data.get('manipulation', 1),
        character_data.get('composure', 1),
        character_data.get('intelligence', 1),
        character_data.get('wits', 1),
        character_data.get('resolve', 1),
        character_data.get('health'),
        character_data.get('willpower'),
        character_data.get('humanity', 7),
        character_data.get('hunger', 1),
        character_data.get('blood_potency'),
        character_data.get('blood_surge'),
        character_data.get('mend_amount'),
        character_data.get('power_bonus'),
        character_data.get('rouse_reroll'),
        character_data.get('feeding_penalty'),
        character_data.get('bane_severity'),
        character_data.get('total_experience'),
        datetime.now()
    ))
    
    character_id = cursor.lastrowid
    
    # Add skills if provided
    if 'skills' in character_data:
        for skill_name, skill_value in character_data['skills'].items():
            if skill_value > 0:
                # Update the character record with skill value
                cursor.execute(f'''
                UPDATE characters SET {skill_name} = ? WHERE id = ?
                ''', (skill_value, character_id))
    
    # Add disciplines if provided
    if 'disciplines' in character_data:
        for discipline_name, level in character_data['disciplines'].items():
            cursor.execute('''
            INSERT INTO character_disciplines (character_id, discipline_name, level)
            VALUES (?, ?, ?)
            ''', (character_id, discipline_name, level))
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'character_id': character_id,
        'power_level': power_level,
        'bonuses_applied': bonuses,
        'message': f'Character created successfully as {bonuses["name"]}'
    }

def import_demiplane_character(demiplane_data, user_id):
    """
    Import character from Demiplane JSON data
    
    Expected format:
    {
        "name": "Character Name",
        "clan": "Toreador",
        "attributes": {...},
        "skills": {...},
        "disciplines": {...},
        ...
    }
    """
    
    # Map Demiplane data to our schema
    character_data = {
        'user_id': user_id,
        'name': demiplane_data.get('name'),
        'clan': demiplane_data.get('clan'),
        'predator_type': demiplane_data.get('predator_type'),
        'concept': demiplane_data.get('concept'),
        'chronicle': demiplane_data.get('chronicle'),
        'demiplane_url': demiplane_data.get('url'),
        'demiplane_character_id': demiplane_data.get('id')
    }
    
    # Map attributes
    if 'attributes' in demiplane_data:
        attrs = demiplane_data['attributes']
        character_data.update({
            'strength': attrs.get('strength', 1),
            'dexterity': attrs.get('dexterity', 1),
            'stamina': attrs.get('stamina', 1),
            'charisma': attrs.get('charisma', 1),
            'manipulation': attrs.get('manipulation', 1),
            'composure': attrs.get('composure', 1),
            'intelligence': attrs.get('intelligence', 1),
            'wits': attrs.get('wits', 1),
            'resolve': attrs.get('resolve', 1)
        })
    
    # Map skills
    if 'skills' in demiplane_data:
        character_data['skills'] = demiplane_data['skills']
    
    # Map disciplines
    if 'disciplines' in demiplane_data:
        character_data['disciplines'] = demiplane_data['disciplines']
    
    # Map core stats
    character_data.update({
        'health': demiplane_data.get('health', 3),
        'willpower': demiplane_data.get('willpower', 3),
        'humanity': demiplane_data.get('humanity', 7),
        'hunger': demiplane_data.get('hunger', 1),
        'blood_potency': demiplane_data.get('blood_potency', 0)
    })
    
    # Determine power level based on stats
    total_xp = demiplane_data.get('experience', 0)
    if total_xp >= 300:
        power_level = 'elder'
    elif total_xp >= 150:
        power_level = 'ancilla'
    else:
        power_level = 'neonate'
    
    return create_character_with_power_level(character_data, power_level)

def get_character_sheet_for_ai(character_id):
    """
    Get complete character sheet formatted for AI context
    Returns a comprehensive text description of the character
    """
    
    db_path = os.path.join(os.path.dirname(__file__), 'vtm_storyteller.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get character data
    cursor.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
    char = cursor.fetchone()
    
    if not char:
        return None
    
    # Get disciplines
    cursor.execute('SELECT discipline_name, level FROM character_disciplines WHERE character_id = ?', (character_id,))
    disciplines = cursor.fetchall()
    
    # Get powers
    cursor.execute('SELECT power_name, discipline, level FROM character_powers WHERE character_id = ?', (character_id,))
    powers = cursor.fetchall()
    
    # Format for AI
    character_context = f"""
CHARACTER SHEET: {char['name']}

BASIC INFORMATION:
- Concept: {char['concept']}
- Clan: {char['clan']}
- Generation: {char['generation']}
- Predator Type: {char['predator_type']}
- Chronicle: {char['chronicle']}

ATTRIBUTES:
Physical: Strength {char['strength']}, Dexterity {char['dexterity']}, Stamina {char['stamina']}
Social: Charisma {char['charisma']}, Manipulation {char['manipulation']}, Composure {char['composure']}
Mental: Intelligence {char['intelligence']}, Wits {char['wits']}, Resolve {char['resolve']}

SKILLS:
Physical: Athletics {char['athletics']}, Brawl {char['brawl']}, Craft {char['craft']}, Drive {char['drive']}, 
          Firearms {char['firearms']}, Larceny {char['larceny']}, Melee {char['melee']}, 
          Stealth {char['stealth']}, Survival {char['survival']}
Social: Animal Ken {char['animal_ken']}, Etiquette {char['etiquette']}, Insight {char['insight']}, 
        Intimidation {char['intimidation']}, Leadership {char['leadership']}, Performance {char['performance']}, 
        Persuasion {char['persuasion']}, Streetwise {char['streetwise']}, Subterfuge {char['subterfuge']}
Mental: Academics {char['academics']}, Awareness {char['awareness']}, Finance {char['finance']}, 
        Investigation {char['investigation']}, Medicine {char['medicine']}, Occult {char['occult']}, 
        Politics {char['politics']}, Science {char['science']}, Technology {char['technology']}

CORE STATS:
- Health: {char['health']} (Damage: {char['health_damage']})
- Willpower: {char['willpower']} (Damage: {char['willpower_damage']})
- Humanity: {char['humanity']} (Stains: {char['humanity_stains']})
- Hunger: {char['hunger']}
- Blood Potency: {char['blood_potency']}

BLOOD POTENCY BENEFITS:
- Blood Surge: {char['blood_surge']} dice
- Mend Amount: {char['mend_amount']} Superficial Damage
- Power Bonus: +{char['power_bonus']} to Discipline rolls
- Rouse Re-roll: {char['rouse_reroll']} failures
- Feeding Penalty: {char['feeding_penalty']} (slakes less Hunger)
- Bane Severity: {char['bane_severity']}

DISCIPLINES:
"""
    
    for disc in disciplines:
        character_context += f"- {disc['discipline_name']}: Level {disc['level']}\n"
    
    if powers:
        character_context += "\nPOWERS:\n"
        for power in powers:
            character_context += f"- {power['power_name']} ({power['discipline']} {power['level']})\n"
    
    character_context += f"\nEXPERIENCE: {char['total_experience']} XP (Spent: {char['spent_experience']})\n"
    
    if char['backstory']:
        character_context += f"\nBACKSTORY:\n{char['backstory']}\n"
    
    conn.close()
    
    return character_context

if __name__ == '__main__':
    print("Enhanced Character System initialized")
    print("\nAvailable Power Levels:")
    for level, data in CHARACTER_POWER_LEVELS.items():
        print(f"  - {data['name']}: {data['description']}")
        print(f"    Bonus XP: {data['bonus_xp']}, Bonus Attributes: {data['bonus_attributes']}")
        print(f"    Bonus Skills: {data['bonus_skills']}, Bonus Disciplines: {data['bonus_disciplines']}")
        print()

