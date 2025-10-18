#!/usr/bin/env python3
"""
AI Character Integration System
Integrates character sheets into AI context for coherent narration
"""

import sqlite3
import json
import os

def get_active_character(user_id):
    """Get the currently active character for a user"""
    db_path = os.path.join(os.path.dirname(__file__), 'vtm_storyteller.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get most recently played character
    cursor.execute('''
    SELECT id FROM characters 
    WHERE user_id = ? 
    ORDER BY last_played DESC, updated_at DESC 
    LIMIT 1
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['id'] if result else None

def build_character_context_for_ai(character_id):
    """
    Build comprehensive character context for AI storytelling
    Returns formatted text optimized for AI understanding
    """
    
    db_path = os.path.join(os.path.dirname(__file__), 'vtm_storyteller.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get character data
    cursor.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
    char = cursor.fetchone()
    
    if not char:
        conn.close()
        return None
    
    # Get disciplines
    cursor.execute('''
    SELECT discipline_name, level 
    FROM character_disciplines 
    WHERE character_id = ? 
    ORDER BY level DESC
    ''', (character_id,))
    disciplines = cursor.fetchall()
    
    # Get powers
    cursor.execute('''
    SELECT power_name, discipline, level, cost, dice_pool 
    FROM character_powers 
    WHERE character_id = ?
    ORDER BY level DESC
    ''', (character_id,))
    powers = cursor.fetchall()
    
    # Get advantages (merits)
    cursor.execute('''
    SELECT advantage_name, dots, description 
    FROM character_advantages 
    WHERE character_id = ?
    ''', (character_id,))
    advantages = cursor.fetchall()
    
    # Get flaws
    cursor.execute('''
    SELECT flaw_name, dots, description 
    FROM character_flaws 
    WHERE character_id = ?
    ''', (character_id,))
    flaws = cursor.fetchall()
    
    # Get touchstones
    cursor.execute('''
    SELECT touchstone_name, conviction, relationship 
    FROM character_touchstones 
    WHERE character_id = ? AND status = 'active'
    ''', (character_id,))
    touchstones = cursor.fetchall()
    
    # Build AI-optimized context
    context = f"""
=== ACTIVE CHARACTER SHEET ===

NAME: {char['name']}
CONCEPT: {char['concept']}
CLAN: {char['clan']} (Generation {char['generation']})
PREDATOR TYPE: {char['predator_type']}

CURRENT STATE:
- Health: {char['health'] - char['health_damage']}/{char['health']} ({char['health_damage']} damage taken)
- Willpower: {char['willpower'] - char['willpower_damage']}/{char['willpower']} ({char['willpower_damage']} spent)
- Humanity: {char['humanity']} ({char['humanity_stains']} stains)
- Hunger: {char['hunger']}/5
- Blood Potency: {char['blood_potency']}

ATTRIBUTES (for dice pools):
Physical: Strength {char['strength']}, Dexterity {char['dexterity']}, Stamina {char['stamina']}
Social: Charisma {char['charisma']}, Manipulation {char['manipulation']}, Composure {char['composure']}
Mental: Intelligence {char['intelligence']}, Wits {char['wits']}, Resolve {char['resolve']}

KEY SKILLS (only listing non-zero):
"""
    
    # Add non-zero skills
    skill_names = [
        'athletics', 'brawl', 'craft', 'drive', 'firearms', 'larceny', 'melee', 'stealth', 'survival',
        'animal_ken', 'etiquette', 'insight', 'intimidation', 'leadership', 'performance', 
        'persuasion', 'streetwise', 'subterfuge',
        'academics', 'awareness', 'finance', 'investigation', 'medicine', 'occult', 
        'politics', 'science', 'technology'
    ]
    
    skills_text = []
    for skill in skill_names:
        value = char[skill]
        if value > 0:
            skills_text.append(f"{skill.replace('_', ' ').title()}: {value}")
    
    context += ", ".join(skills_text) + "\n\n"
    
    # Add disciplines
    if disciplines:
        context += "DISCIPLINES:\n"
        for disc in disciplines:
            context += f"- {disc['discipline_name']}: Level {disc['level']}\n"
        context += "\n"
    
    # Add powers
    if powers:
        context += "AVAILABLE POWERS:\n"
        for power in powers:
            cost_info = f" (Cost: {power['cost']})" if power['cost'] else ""
            pool_info = f" [Pool: {power['dice_pool']}]" if power['dice_pool'] else ""
            context += f"- {power['power_name']}{cost_info}{pool_info}\n"
        context += "\n"
    
    # Add advantages
    if advantages:
        context += "ADVANTAGES (Merits/Backgrounds):\n"
        for adv in advantages:
            dots = "●" * adv['dots']
            context += f"- {adv['advantage_name']} {dots}\n"
        context += "\n"
    
    # Add flaws
    if flaws:
        context += "FLAWS:\n"
        for flaw in flaws:
            dots = "●" * flaw['dots']
            context += f"- {flaw['flaw_name']} {dots}\n"
        context += "\n"
    
    # Add touchstones
    if touchstones:
        context += "TOUCHSTONES & CONVICTIONS:\n"
        for ts in touchstones:
            context += f"- {ts['touchstone_name']} (Conviction: {ts['conviction']})\n"
        context += "\n"
    
    # Add Blood Potency benefits
    context += f"""BLOOD POTENCY MECHANICS:
- Blood Surge: Add {char['blood_surge']} dice to one Physical or Discipline roll
- Mend: Heal {char['mend_amount']} Superficial Health damage per Rouse Check
- Discipline Power Bonus: +{char['power_bonus']} to Discipline dice pools
- Rouse Re-roll: Re-roll up to {char['rouse_reroll']} failed dice on Discipline rolls
- Feeding Penalty: Slake {char['feeding_penalty']} less Hunger when feeding
- Bane Severity: {char['bane_severity']} (affects clan bane)

"""
    
    # Add character motivations
    if char['ambition'] or char['desire']:
        context += "CHARACTER MOTIVATIONS:\n"
        if char['ambition']:
            context += f"- Ambition: {char['ambition']}\n"
        if char['desire']:
            context += f"- Desire: {char['desire']}\n"
        context += "\n"
    
    # Add backstory if available
    if char['backstory']:
        context += f"BACKSTORY:\n{char['backstory']}\n\n"
    
    context += "=== END CHARACTER SHEET ===\n"
    
    conn.close()
    
    return context

def get_dice_pool_for_action(character_id, attribute, skill):
    """
    Calculate dice pool for a specific action
    Returns: (dice_pool, hunger_dice)
    """
    
    db_path = os.path.join(os.path.dirname(__file__), 'vtm_storyteller.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
    char = cursor.fetchone()
    
    if not char:
        conn.close()
        return (0, 0)
    
    # Get attribute value
    attribute_value = char[attribute.lower()] if attribute else 0
    
    # Get skill value
    skill_value = char[skill.lower().replace(' ', '_')] if skill else 0
    
    # Calculate total pool
    dice_pool = attribute_value + skill_value
    
    # Get hunger dice
    hunger = char['hunger']
    
    conn.close()
    
    return (dice_pool, hunger)

def update_character_state(character_id, updates):
    """
    Update character state after actions
    
    updates = {
        'health_damage': +1,  # Take 1 damage
        'willpower_damage': +1,  # Spend 1 willpower
        'hunger': +1,  # Increase hunger
        'humanity_stains': +1  # Add stain
    }
    """
    
    db_path = os.path.join(os.path.dirname(__file__), 'vtm_storyteller.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for field, change in updates.items():
        cursor.execute(f'''
        UPDATE characters 
        SET {field} = {field} + ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (change, character_id))
    
    # Update last_played timestamp
    cursor.execute('''
    UPDATE characters 
    SET last_played = CURRENT_TIMESTAMP 
    WHERE id = ?
    ''', (character_id,))
    
    conn.commit()
    conn.close()
    
    return {'success': True, 'message': 'Character state updated'}

def get_character_summary_for_chat(user_id):
    """
    Get a brief character summary for chat context
    Shorter version for ongoing conversations
    """
    
    character_id = get_active_character(user_id)
    if not character_id:
        return None
    
    db_path = os.path.join(os.path.dirname(__file__), 'vtm_storyteller.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
    char = cursor.fetchone()
    
    if not char:
        conn.close()
        return None
    
    summary = f"""
[ACTIVE CHARACTER: {char['name']} - {char['clan']} {char['predator_type']}]
Current State: Health {char['health'] - char['health_damage']}/{char['health']}, Willpower {char['willpower'] - char['willpower_damage']}/{char['willpower']}, Humanity {char['humanity']}, Hunger {char['hunger']}
"""
    
    conn.close()
    return summary

if __name__ == '__main__':
    print("AI Character Integration System initialized")
    print("\nAvailable functions:")
    print("  - get_active_character(user_id)")
    print("  - build_character_context_for_ai(character_id)")
    print("  - get_dice_pool_for_action(character_id, attribute, skill)")
    print("  - update_character_state(character_id, updates)")
    print("  - get_character_summary_for_chat(user_id)")

