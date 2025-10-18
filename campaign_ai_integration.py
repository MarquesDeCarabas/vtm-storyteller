#!/usr/bin/env python3
"""
Campaign AI Integration
Seamlessly integrates campaign database with AI Storyteller
- Auto-saves AI-generated content
- Auto-recalls relevant content
- Injects context into AI prompts
"""

import re
from campaign_auto_save import CampaignAutoSave
from campaign_recall import CampaignRecall

class CampaignAIIntegration:
    def __init__(self, db_path='campaign_data.db'):
        self.auto_save = CampaignAutoSave(db_path)
        self.recall = CampaignRecall(db_path)
        self.db_path = db_path
    
    def process_ai_response(self, ai_response: str, campaign_id: int = None) -> dict:
        """
        Process AI response:
        1. Auto-save any generated content
        2. Return metadata about what was saved
        """
        saved_items = self.auto_save.auto_detect_and_save(ai_response, campaign_id)
        
        return {
            'saved_items': saved_items,
            'saved_count': len(saved_items)
        }
    
    def detect_mentions(self, user_message: str) -> dict:
        """
        Detect mentions of NPCs, Locations, or Items in user message
        Returns dict with detected entities
        """
        mentions = {
            'npcs': [],
            'locations': [],
            'items': []
        }
        
        # Common NPC indicators
        npc_indicators = ['meet', 'talk to', 'visit', 'find', 'see', 'encounter', 'speak with']
        for indicator in npc_indicators:
            if indicator in user_message.lower():
                # Try to extract name after indicator
                pattern = f"{indicator}\\s+([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)"
                matches = re.findall(pattern, user_message, re.IGNORECASE)
                for match in matches:
                    # Check if this NPC exists in database
                    npc = self.recall.get_npc_by_name(match)
                    if npc:
                        mentions['npcs'].append(npc)
        
        # Common location indicators
        location_indicators = ['go to', 'visit', 'return to', 'arrive at', 'enter', 'at the', 'in the']
        for indicator in location_indicators:
            if indicator in user_message.lower():
                # Try to extract location name
                pattern = f"{indicator}\\s+(The\\s+[A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)"
                matches = re.findall(pattern, user_message, re.IGNORECASE)
                for match in matches:
                    location = self.recall.get_location_by_name(match)
                    if location:
                        mentions['locations'].append(location)
        
        # Common item indicators
        item_indicators = ['use', 'ride', 'drive', 'wear', 'equip', 'with my', 'on my']
        for indicator in item_indicators:
            if indicator in user_message.lower():
                # Try to extract item name
                pattern = f"{indicator}\\s+(The\\s+[A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)"
                matches = re.findall(pattern, user_message, re.IGNORECASE)
                for match in matches:
                    item = self.recall.get_item_by_name(match)
                    if item:
                        mentions['items'].append(item)
        
        return mentions
    
    def build_context_for_ai(self, user_message: str, campaign_id: int = None) -> str:
        """
        Build additional context for AI based on user message
        Automatically recalls relevant NPCs, Locations, Items
        """
        context_parts = []
        
        # Detect mentions
        mentions = self.detect_mentions(user_message)
        
        # Add recalled NPCs
        if mentions['npcs']:
            context_parts.append("=== RECALLED NPCs (from campaign database) ===")
            for npc in mentions['npcs']:
                context_parts.append(self.recall.format_npc_for_ai(npc))
                context_parts.append("")
        
        # Add recalled Locations
        if mentions['locations']:
            context_parts.append("=== RECALLED LOCATIONS (from campaign database) ===")
            for location in mentions['locations']:
                context_parts.append(self.recall.format_location_for_ai(location))
                context_parts.append("")
        
        # Add recalled Items
        if mentions['items']:
            context_parts.append("=== RECALLED ITEMS (from campaign database) ===")
            for item in mentions['items']:
                context_parts.append(self.recall.format_item_for_ai(item))
                context_parts.append("")
        
        # If specific city is mentioned, load city context
        cities = ['Vienna', 'Paris', 'London', 'Chicago', 'Los Angeles', 'Berlin', 'Barcelona']
        for city in cities:
            if city.lower() in user_message.lower():
                city_data = self.recall.get_all_for_city(city)
                if city_data['npcs'] or city_data['locations']:
                    context_parts.append(f"=== {city.upper()} CAMPAIGN DATA ===")
                    context_parts.append(f"Known NPCs in {city}: {len(city_data['npcs'])}")
                    context_parts.append(f"Known Locations in {city}: {len(city_data['locations'])}")
                    
                    # Add brief list of NPCs
                    if city_data['npcs']:
                        context_parts.append(f"\nNPCs in {city}:")
                        for npc in city_data['npcs'][:5]:  # Top 5
                            context_parts.append(f"- {npc['name']} ({npc.get('clan', 'Unknown')}, {npc.get('faction', 'Independent')})")
                    
                    # Add brief list of locations
                    if city_data['locations']:
                        context_parts.append(f"\nLocations in {city}:")
                        for loc in city_data['locations'][:5]:  # Top 5
                            context_parts.append(f"- {loc['name']} ({loc.get('type', 'Unknown')})")
                    
                    context_parts.append("")
                break
        
        if not context_parts:
            return ""
        
        # Add instruction for AI
        instruction = """
IMPORTANT: The following information is from the campaign database. These NPCs, Locations, and Items have been previously established in this campaign. Use this information to maintain continuity and consistency in your storytelling.
"""
        
        return instruction + "\n" + "\n".join(context_parts)
    
    def get_campaign_memory_summary(self, campaign_id: int) -> str:
        """Get a summary of all campaign memory for AI context"""
        summary = self.recall.get_campaign_summary(campaign_id)
        
        if not summary['campaign']:
            return "No campaign data found."
        
        campaign = summary['campaign']
        
        output = f"""
=== CAMPAIGN MEMORY SUMMARY ===

Campaign: {campaign.get('name', 'Unnamed Campaign')}
City: {campaign.get('city', 'Unknown')}
Chronicle: {campaign.get('chronicle_name', 'Unknown')}
Status: {campaign.get('status', 'active')}
Last Played: {campaign.get('last_played', 'Never')}

**Campaign Database:**
- NPCs: {summary['npc_count']}
- Locations: {summary['location_count']}
- Items: {summary['item_count']}
- Events: {summary['event_count']}

**Storyteller Notes:**
{campaign.get('storyteller_notes', 'None')}
"""
        return output.strip()
    
    def create_system_prompt_addition(self) -> str:
        """
        Create additional system prompt text to inform AI about campaign database
        """
        return """
=== CAMPAIGN DATABASE SYSTEM ===

You have access to a persistent campaign database that stores:
- **NPCs**: Complete character sheets with stats, personality, appearance, quirks
- **Locations**: Detailed descriptions with rooms, atmosphere, security, supernatural elements
- **Items**: Custom items with stats, features, and game mechanics

**How it works:**
1. When you create an NPC, Location, or Item, it is automatically saved to the database
2. When the player mentions a previously created element, it will be recalled and provided to you
3. You should maintain consistency with previously established information

**Guidelines:**
- When you create something new, use clear formatting (NAME:, CLAN:, ATTRIBUTES:, etc.)
- When referencing previously established elements, maintain their characteristics
- If a player returns to a location or meets an NPC again, recall their previous interactions
- NPCs can evolve and change, but maintain core personality traits
- Locations can be modified by events, but maintain architectural consistency

**Memory Persistence:**
- All content you create is saved across sessions
- Players can return to the same city with different characters and encounter the same NPCs
- The campaign world is persistent and evolves over time

Use this system to create a rich, consistent, and memorable World of Darkness experience.
"""

def integrate_with_chat_endpoint(user_message: str, campaign_id: int = None, 
                                 db_path: str = 'campaign_data.db') -> dict:
    """
    Main integration function to be called from chat endpoint
    Returns dict with context to add to AI prompt and callback for processing response
    """
    integration = CampaignAIIntegration(db_path)
    
    # Build context from campaign database
    additional_context = integration.build_context_for_ai(user_message, campaign_id)
    
    # Return context and a callback function
    return {
        'additional_context': additional_context,
        'process_response': lambda ai_response: integration.process_ai_response(ai_response, campaign_id)
    }

if __name__ == "__main__":
    # Test integration
    integration = CampaignAIIntegration()
    
    print("🧪 Testing AI Integration\n")
    
    # Test 1: Detect mentions
    print("=== Test 1: Detect Mentions ===")
    test_message = "I want to visit The Hallowed Hall and meet with The Archivist"
    mentions = integration.detect_mentions(test_message)
    print(f"Detected NPCs: {len(mentions['npcs'])}")
    print(f"Detected Locations: {len(mentions['locations'])}")
    print(f"Detected Items: {len(mentions['items'])}")
    
    # Test 2: Build context
    print("\n=== Test 2: Build Context ===")
    context = integration.build_context_for_ai(test_message)
    if context:
        print("Context built successfully:")
        print(context[:500] + "..." if len(context) > 500 else context)
    else:
        print("No context built (no matches found)")
    
    # Test 3: System prompt addition
    print("\n=== Test 3: System Prompt Addition ===")
    system_addition = integration.create_system_prompt_addition()
    print(system_addition[:300] + "...")

