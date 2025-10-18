"""
Intelligent Dice Rolling System for VTM Storyteller
Allows the AI to suggest rolls and the user to execute them with simple /roll command
"""

import re
import random
from typing import Dict, List, Tuple, Optional

class IntelligentDiceSystem:
    def __init__(self):
        # Store last suggested roll per session
        self.last_suggested_rolls = {}
    
    def extract_roll_from_ai_message(self, ai_message: str) -> Optional[Dict]:
        """
        Extract dice roll suggestion from AI message.
        Looks for patterns like:
        - "roll Intelligence + Auspex"
        - "roll Dexterity + Stealth"
        - "roll Strength + Brawl"
        """
        # Pattern to match "roll <Attribute> + <Skill>"
        pattern = r"roll\s+([A-Z][a-z]+)\s*\+\s*([A-Z][a-z]+)"
        match = re.search(pattern, ai_message, re.IGNORECASE)
        
        if match:
            attribute = match.group(1).capitalize()
            skill = match.group(2).capitalize()
            
            return {
                'attribute': attribute,
                'skill': skill,
                'type': 'attribute_skill'
            }
        
        # Pattern to match "roll <Discipline>" for discipline powers
        pattern_discipline = r"roll\s+([A-Z][a-z]+)\s*\(discipline\)"
        match_disc = re.search(pattern_discipline, ai_message, re.IGNORECASE)
        
        if match_disc:
            discipline = match_disc.group(1).capitalize()
            return {
                'discipline': discipline,
                'type': 'discipline'
            }
        
        return None
    
    def store_suggested_roll(self, session_id: str, roll_data: Dict):
        """Store the last suggested roll for a session"""
        self.last_suggested_rolls[session_id] = roll_data
    
    def get_last_suggested_roll(self, session_id: str) -> Optional[Dict]:
        """Get the last suggested roll for a session"""
        return self.last_suggested_rolls.get(session_id)
    
    def parse_roll_command(self, command: str) -> Dict:
        """
        Parse /roll command variants:
        - /roll - Use last suggested roll
        - /roll + blood surge - Use last suggested roll + Blood Potency
        - /roll Intelligence + Auspex - Specific roll
        - /roll Intelligence + Auspex + blood surge - Specific roll + Blood Potency
        """
        result = {
            'use_last_suggested': False,
            'blood_surge': False,
            'attribute': None,
            'skill': None,
            'discipline': None
        }
        
        # Check for blood surge
        if 'blood surge' in command.lower() or 'bloodsurge' in command.lower():
            result['blood_surge'] = True
            # Remove blood surge from command for further parsing
            command = re.sub(r'\+?\s*blood\s*surge', '', command, flags=re.IGNORECASE)
        
        # Remove /roll prefix
        command = command.replace('/roll', '').strip()
        
        # If command is empty or just "+", use last suggested
        if not command or command == '+':
            result['use_last_suggested'] = True
            return result
        
        # Try to parse specific roll
        pattern = r'([A-Z][a-z]+)\s*\+\s*([A-Z][a-z]+)'
        match = re.search(pattern, command, re.IGNORECASE)
        
        if match:
            result['attribute'] = match.group(1).capitalize()
            result['skill'] = match.group(2).capitalize()
        else:
            # Maybe it's just a discipline name
            if command.strip():
                result['discipline'] = command.strip().capitalize()
        
        return result
    
    def get_attribute_value(self, character_data: Dict, attribute: str) -> int:
        """Get attribute value from character data"""
        attribute_map = {
            'Strength': 'strength',
            'Dexterity': 'dexterity',
            'Stamina': 'stamina',
            'Charisma': 'charisma',
            'Manipulation': 'manipulation',
            'Composure': 'composure',
            'Intelligence': 'intelligence',
            'Wits': 'wits',
            'Resolve': 'resolve'
        }
        
        attr_key = attribute_map.get(attribute, attribute.lower())
        
        # First try to get from JSON attributes field (PDF upload system)
        if 'attributes' in character_data and character_data['attributes']:
            try:
                import json
                attributes = json.loads(character_data['attributes']) if isinstance(character_data['attributes'], str) else character_data['attributes']
                if attr_key in attributes:
                    return attributes[attr_key]
            except:
                pass
        
        # Fallback to individual column (legacy system)
        return character_data.get(attr_key, 0)
    
    def get_skill_value(self, character_data: Dict, skill: str) -> int:
        """Get skill value from character data"""
        skill_map = {
            'Athletics': 'athletics',
            'Brawl': 'brawl',
            'Craft': 'craft',
            'Drive': 'drive',
            'Firearms': 'firearms',
            'Melee': 'melee',
            'Larceny': 'larceny',
            'Stealth': 'stealth',
            'Survival': 'survival',
            'AnimalKen': 'animal_ken',
            'Etiquette': 'etiquette',
            'Insight': 'insight',
            'Intimidation': 'intimidation',
            'Leadership': 'leadership',
            'Performance': 'performance',
            'Persuasion': 'persuasion',
            'Streetwise': 'streetwise',
            'Subterfuge': 'subterfuge',
            'Academics': 'academics',
            'Awareness': 'awareness',
            'Finance': 'finance',
            'Investigation': 'investigation',
            'Medicine': 'medicine',
            'Occult': 'occult',
            'Politics': 'politics',
            'Science': 'science',
            'Technology': 'technology',
            'Auspex': 'auspex',
            'Obfuscate': 'obfuscate',
            'Presence': 'presence',
            'Dominate': 'dominate',
            'Fortitude': 'fortitude',
            'Potence': 'potence',
            'Celerity': 'celerity',
            'Protean': 'protean',
            'Animalism': 'animalism'
        }
        
        skill_key = skill_map.get(skill, skill.lower())
        
        # First try to get from JSON skills field (PDF upload system)
        if 'skills' in character_data and character_data['skills']:
            try:
                import json
                skills = json.loads(character_data['skills']) if isinstance(character_data['skills'], str) else character_data['skills']
                if skill_key in skills:
                    return skills[skill_key]
            except:
                pass
        
        # Fallback to individual column (legacy system)
        return character_data.get(skill_key, 0)
    
    def calculate_dice_pool(self, character_data: Dict, roll_data: Dict) -> Tuple[int, str]:
        """
        Calculate dice pool based on roll data and character stats.
        Returns (pool_size, description)
        """
        pool = 0
        description = ""
        
        if roll_data.get('attribute') and roll_data.get('skill'):
            attr = roll_data['attribute']
            skill = roll_data['skill']
            
            attr_value = self.get_attribute_value(character_data, attr)
            skill_value = self.get_skill_value(character_data, skill)
            
            pool = attr_value + skill_value
            description = f"{attr} ({attr_value}) + {skill} ({skill_value})"
        
        elif roll_data.get('discipline'):
            discipline = roll_data['discipline']
            disc_value = self.get_skill_value(character_data, discipline)
            pool = disc_value
            description = f"{discipline} ({disc_value})"
        
        # Add Blood Potency if Blood Surge is used
        if roll_data.get('blood_surge'):
            blood_potency = character_data.get('blood_potency', 0)
            pool += blood_potency
            description += f" + Blood Surge ({blood_potency})"
        
        return pool, description
    
    def roll_dice(self, pool_size: int, hunger: int = 0, difficulty: int = 0) -> Dict:
        """
        Roll V5 dice with Hunger dice.
        Returns detailed results including successes, criticals, bestial failure, etc.
        """
        if pool_size <= 0:
            return {
                'success': False,
                'total_successes': 0,
                'criticals': 0,
                'bestial_failure': False,
                'messy_critical': False,
                'message': "❌ Dice pool is 0 or negative. Cannot roll."
            }
        
        # Determine how many regular dice and hunger dice
        regular_dice = max(0, pool_size - hunger)
        hunger_dice = min(hunger, pool_size)
        
        # Roll regular dice (d10)
        regular_rolls = [random.randint(1, 10) for _ in range(regular_dice)]
        hunger_rolls = [random.randint(1, 10) for _ in range(hunger_dice)]
        
        # Count successes (6+)
        regular_successes = sum(1 for d in regular_rolls if d >= 6)
        hunger_successes = sum(1 for d in hunger_rolls if d >= 6)
        total_successes = regular_successes + hunger_successes
        
        # Count 10s for criticals
        regular_tens = sum(1 for d in regular_rolls if d == 10)
        hunger_tens = sum(1 for d in hunger_rolls if d == 10)
        total_tens = regular_tens + hunger_tens
        
        # Critical pairs (each pair of 10s adds 2 successes)
        critical_pairs = total_tens // 2
        total_successes += critical_pairs * 2
        
        # Check for Messy Critical (at least one hunger die is a 10 and we have a critical)
        messy_critical = hunger_tens > 0 and critical_pairs > 0
        
        # Check for Bestial Failure (all hunger dice are 1 and total successes < difficulty)
        bestial_failure = (hunger_dice > 0 and 
                          all(d == 1 for d in hunger_rolls) and 
                          total_successes < difficulty)
        
        # Determine success
        success = total_successes >= difficulty
        
        return {
            'success': success,
            'total_successes': total_successes,
            'regular_rolls': regular_rolls,
            'hunger_rolls': hunger_rolls,
            'criticals': critical_pairs,
            'messy_critical': messy_critical,
            'bestial_failure': bestial_failure,
            'difficulty': difficulty,
            'message': self._format_roll_message(
                regular_rolls, hunger_rolls, total_successes, 
                difficulty, success, critical_pairs, messy_critical, bestial_failure
            )
        }
    
    def _format_roll_message(self, regular_rolls, hunger_rolls, successes, 
                            difficulty, success, criticals, messy_critical, bestial_failure):
        """Format the dice roll result message"""
        msg = "🎲 **DICE ROLL RESULT**\n\n"
        
        if regular_rolls:
            msg += f"**Regular Dice:** {', '.join(str(d) for d in regular_rolls)}\n"
        if hunger_rolls:
            msg += f"**Hunger Dice:** {', '.join(str(d) for d in hunger_rolls)} 🩸\n"
        
        msg += f"\n**Total Successes:** {successes}"
        
        if difficulty > 0:
            msg += f" (Difficulty: {difficulty})"
        
        msg += "\n\n"
        
        if bestial_failure:
            msg += "💀 **BESTIAL FAILURE!** Your Beast takes control!\n"
        elif messy_critical:
            msg += "⚠️ **MESSY CRITICAL!** You succeed spectacularly, but at a cost...\n"
        elif criticals > 0:
            msg += f"✨ **CRITICAL SUCCESS!** ({criticals} pair{'s' if criticals > 1 else ''})\n"
        elif success:
            msg += "✅ **SUCCESS!**\n"
        else:
            msg += "❌ **FAILURE**\n"
        
        return msg

# Global instance
intelligent_dice = IntelligentDiceSystem()

