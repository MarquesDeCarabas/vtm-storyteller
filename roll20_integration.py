"""
Roll20 Integration for VTM Storyteller

This module provides integration with Roll20 for:
- Character sheet synchronization
- Dice rolling
- Map and token management
- Campaign tracking
"""

import requests
import json
import os
from typing import Dict, List, Optional

class Roll20API:
    """Roll20 API client"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ROLL20_API_KEY")
        self.base_url = "https://app.roll20.net/api/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_game(self, name: str, description: str = "") -> Dict:
        """Create a new Roll20 game"""
        payload = {
            "name": name,
            "description": description,
            "system": "vampire-the-masquerade-5th-edition"
        }
        
        response = requests.post(
            f"{self.base_url}/games",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create game: {response.text}")
    
    def get_game(self, game_id: str) -> Dict:
        """Get game details"""
        response = requests.get(
            f"{self.base_url}/games/{game_id}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get game: {response.text}")
    
    def create_character(self, game_id: str, character_data: Dict) -> Dict:
        """Create a character in a Roll20 game"""
        payload = {
            "name": character_data.get("name"),
            "avatar": character_data.get("avatar", ""),
            "bio": character_data.get("bio", ""),
            "attributes": self._convert_vtm_to_roll20(character_data)
        }
        
        response = requests.post(
            f"{self.base_url}/games/{game_id}/characters",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create character: {response.text}")
    
    def update_character(self, game_id: str, character_id: str, character_data: Dict) -> Dict:
        """Update a character in Roll20"""
        payload = {
            "attributes": self._convert_vtm_to_roll20(character_data)
        }
        
        response = requests.patch(
            f"{self.base_url}/games/{game_id}/characters/{character_id}",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to update character: {response.text}")
    
    def roll_dice(self, formula: str) -> Dict:
        """Roll dice using Roll20's dice engine"""
        payload = {
            "formula": formula
        }
        
        response = requests.post(
            f"{self.base_url}/dice/roll",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to roll dice: {response.text}")
    
    def create_handout(self, game_id: str, name: str, content: str) -> Dict:
        """Create a handout (for story notes, NPCs, etc.)"""
        payload = {
            "name": name,
            "notes": content,
            "gmnotes": ""
        }
        
        response = requests.post(
            f"{self.base_url}/games/{game_id}/handouts",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create handout: {response.text}")
    
    def upload_map(self, game_id: str, map_file_path: str, name: str) -> Dict:
        """Upload a map image to Roll20"""
        with open(map_file_path, 'rb') as f:
            files = {'file': f}
            data = {'name': name}
            
            response = requests.post(
                f"{self.base_url}/games/{game_id}/pages",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files,
                data=data
            )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to upload map: {response.text}")
    
    def create_token(self, game_id: str, page_id: str, token_data: Dict) -> Dict:
        """Create a token on a map"""
        payload = {
            "name": token_data.get("name"),
            "left": token_data.get("x", 0),
            "top": token_data.get("y", 0),
            "width": token_data.get("width", 70),
            "height": token_data.get("height", 70),
            "imgsrc": token_data.get("image_url", ""),
            "represents": token_data.get("character_id", "")
        }
        
        response = requests.post(
            f"{self.base_url}/games/{game_id}/pages/{page_id}/tokens",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create token: {response.text}")
    
    def _convert_vtm_to_roll20(self, character_data: Dict) -> Dict:
        """Convert VTM character data to Roll20 format"""
        attributes = {}
        
        # Basic info
        if "clan" in character_data:
            attributes["clan"] = character_data["clan"]
        if "generation" in character_data:
            attributes["generation"] = character_data["generation"]
        
        # Attributes
        if "attributes" in character_data:
            for attr, value in character_data["attributes"].items():
                attributes[attr.lower()] = value
        
        # Disciplines
        if "disciplines" in character_data:
            for disc, level in character_data["disciplines"].items():
                attributes[f"discipline_{disc.lower()}"] = level
        
        # Backgrounds
        if "backgrounds" in character_data:
            for bg, value in character_data["backgrounds"].items():
                attributes[f"background_{bg.lower()}"] = value
        
        return attributes

class VTMCampaignManager:
    """Manage VTM campaigns with Roll20 integration"""
    
    def __init__(self, roll20_api: Roll20API):
        self.roll20 = roll20_api
    
    def setup_new_campaign(self, campaign_name: str, storyteller_notes: str = "") -> Dict:
        """Set up a new VTM campaign in Roll20"""
        # Create the game
        game = self.roll20.create_game(
            name=campaign_name,
            description=f"Vampire: The Masquerade 5th Edition campaign\n\n{storyteller_notes}"
        )
        
        game_id = game["id"]
        
        # Create initial handouts
        self.roll20.create_handout(
            game_id,
            "Chronicle Rules",
            self._get_vtm_rules_handout()
        )
        
        self.roll20.create_handout(
            game_id,
            "Session Notes",
            "# Session 1\n\n(Notes will be added here)"
        )
        
        return {
            "game_id": game_id,
            "game_url": f"https://app.roll20.net/campaigns/details/{game_id}",
            "status": "ready"
        }
    
    def sync_character_to_roll20(self, game_id: str, character_data: Dict) -> Dict:
        """Sync a VTM character to Roll20"""
        try:
            # Check if character already exists
            character_id = character_data.get("roll20_id")
            
            if character_id:
                # Update existing character
                result = self.roll20.update_character(game_id, character_id, character_data)
            else:
                # Create new character
                result = self.roll20.create_character(game_id, character_data)
                character_data["roll20_id"] = result["id"]
            
            return {
                "success": True,
                "character_id": result["id"],
                "message": "Character synced successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_combat_map(self, game_id: str, location_name: str, map_image_path: str = None) -> Dict:
        """Create a combat map for a scene"""
        # Upload map if provided
        if map_image_path:
            page = self.roll20.upload_map(game_id, map_image_path, location_name)
        else:
            # Create blank page
            page = {"id": "default_page"}
        
        return {
            "page_id": page["id"],
            "name": location_name,
            "url": f"https://app.roll20.net/editor/setactivepage/{page['id']}"
        }
    
    def _get_vtm_rules_handout(self) -> str:
        """Get VTM 5e rules summary for handout"""
        return """
# Vampire: The Masquerade 5th Edition - Quick Reference

## Dice Rolling
- Roll a pool of d10s equal to Attribute + Skill
- 6+ is a success
- 10s count as 2 successes (critical)
- Hunger dice replace normal dice (based on Hunger level)

## Hunger
- Starts at 1
- Increases when using Disciplines or failing to feed
- Decreases when feeding
- At 5 Hunger, risk of frenzy

## Combat
- Initiative: Wits + Composure
- Attack: Dexterity + Brawl/Melee/Firearms
- Damage: Weapon damage + margin of success
- Health: Stamina + 3

## Disciplines
- Blood Sorcery, Celerity, Fortitude, Obfuscate, Potence, Presence, etc.
- Cost: 1 Rouse check per use (may increase Hunger)

## Willpower
- Max: Composure + Resolve
- Spend to reroll failures
- Regain through convictions and touchstones
"""

# Example usage
if __name__ == "__main__":
    # Initialize API
    api = Roll20API()
    manager = VTMCampaignManager(api)
    
    # Example: Create a campaign
    campaign = manager.setup_new_campaign(
        "Night Roads of Chicago",
        "A dark chronicle set in modern Chicago..."
    )
    
    print(f"Campaign created: {campaign['game_url']}")
    
    # Example: Sync a character
    character = {
        "name": "Marcus Vitel",
        "clan": "Ventrue",
        "generation": 8,
        "attributes": {
            "strength": 2,
            "dexterity": 3,
            "stamina": 3,
            "charisma": 4,
            "manipulation": 3,
            "composure": 4,
            "intelligence": 3,
            "wits": 3,
            "resolve": 4
        },
        "disciplines": {
            "Dominate": 3,
            "Fortitude": 2,
            "Presence": 2
        }
    }
    
    result = manager.sync_character_to_roll20(campaign["game_id"], character)
    print(f"Character synced: {result}")

