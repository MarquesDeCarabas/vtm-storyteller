# VTM Storyteller - Multi-Agent AI Game Master

An AI-powered Game Master system for **Vampire: The Masquerade 5th Edition**, built with OpenAI's Assistant API and deployed on Railway.

## Features

### Core Features
- **AI Storyteller**: Powered by OpenAI Assistant with V:TM 5e rules knowledge
- **Interactive Chat Interface**: Real-time conversation with the Storyteller
- **Server-Sent Events (SSE)**: Streaming responses for better UX
- **Character Sheet Storage**: Save and retrieve character sheets with unique URLs
- **System Health Monitoring**: `/health` endpoint for deployment status

### Premium Features
- **Discord Bot Integration**: Play V:TM directly from Discord
  - Slash commands for storytelling, dice rolling, character management
  - Voice channel support for immersive gameplay
- **Roll20 Integration**: Synchronize campaigns and maps
  - Campaign management
  - Character sheet sync
  - Map and token integration

## Deployment

### Railway Deployment

This application is configured for one-click deployment on Railway.

#### Required Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key_here
ASSISTANT_ID=your_assistant_id_here
VECTOR_STORE_ID=your_vector_store_id_here
DISCORD_TOKEN=your_discord_bot_token_here
ROLL20_API_KEY=your_roll20_api_key_here
```

#### Quick Deploy

1. Fork this repository
2. Connect to Railway
3. Add environment variables
4. Deploy automatically

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key
export ASSISTANT_ID=your_assistant_id
export VECTOR_STORE_ID=your_vector_store_id

# Run the application
python app.py
```

## API Endpoints

### Web Interface
- `GET /` - Main chat interface
- `POST /chat` - Send messages to the Storyteller
- `GET /stream` - SSE endpoint for real-time updates

### Character Management
- `GET /character/<character_id>` - View character sheet
- `POST /character` - Save new character sheet

### System
- `GET /health` - Health check endpoint

## Discord Bot

The Discord bot provides the following slash commands:

- `/story <message>` - Interact with the Storyteller
- `/roll <pool> <hunger>` - Roll dice with hunger mechanics
- `/character <action>` - Manage character sheets
- `/campaign <action>` - Manage Roll20 campaigns

## Roll20 Integration

Synchronize your V:TM game with Roll20:

- Import/export character sheets
- Sync campaign data
- Update maps and tokens
- Track game state

## Technology Stack

- **Backend**: Python Flask
- **AI**: OpenAI Assistant API
- **Database**: SQLite (character storage)
- **Deployment**: Railway
- **Discord**: Discord.py
- **Roll20**: Roll20 API

## Project Structure

```
vtm-storyteller/
├── app.py                    # Main Flask application
├── discord_bot.py            # Discord bot integration
├── roll20_integration.py     # Roll20 API integration
├── requirements.txt          # Python dependencies
├── Procfile                  # Railway deployment config
├── railway.json              # Railway configuration
└── README.md                 # This file
```

## Credits

Built with:
- OpenAI Assistant API
- Flask Web Framework
- Discord.py
- Roll20 API

**Vampire: The Masquerade** is a trademark of Paradox Interactive AB. This is a fan project and is not affiliated with or endorsed by Paradox Interactive.

## License

This project is for personal use and educational purposes.


## 🔄 Latest Update (Oct 17, 2025)

**Migrated to Chat Completions API**

The application has been updated to use OpenAI's Chat Completions API instead of the deprecated Assistants API. This provides:

- ✅ Better stability and reliability
- ✅ Faster response times
- ✅ Improved conversation context management
- ✅ Full streaming support
- ✅ Future-proof implementation

### Changes Made:
- Removed dependency on `ASSISTANT_ID` and `VECTOR_STORE_ID`
- Implemented in-memory conversation history management
- Updated both `/chat` and `/chat/stream` endpoints
- Added comprehensive VTM 5e system prompt
- Improved error handling and logging

### Testing:
All endpoints have been tested and verified:
- ✅ Health monitoring
- ✅ Chat functionality
- ✅ Streaming responses
- ✅ Character management


## 🎭 Hybrid Character System (Latest Feature)

### Overview
The VTM Storyteller now includes a comprehensive hybrid character management system that gives you two powerful options:

#### Option 1: Demiplane Integration 🔗
- **Link existing Demiplane characters** to the Storyteller
- Access professional, official VTM 5e character sheets
- Automatic Roll20 integration (via Demiplane)
- Perfect for serious campaigns and experienced players

#### Option 2: Custom Character Creation ✨
- **Built-in character creation wizard** with step-by-step guidance
- Interactive character sheets with all VTM 5e mechanics
- Quick character generation for one-shots or casual games
- No external account required

### Features

#### 🎲 Advanced Dice Roller
- Full VTM 5e dice mechanics with d10 pools
- **Hunger dice system** (red dice representing the Beast)
- Automatic success calculation (6+ = success)
- **Critical wins**: Pairs of 10s (4 successes per pair)
- **Messy criticals**: Criticals with Hunger dice showing 10
- **Bestial failures**: Zero successes with Hunger 1s
- Visual dice display with color coding

#### 👤 Character Management
- Create and store multiple characters
- Track **Health**, **Willpower**, **Humanity**, and **Hunger**
- Manage **Attributes** (Physical, Social, Mental)
- Manage **Skills** (27 skills across 3 categories)
- Manage **Disciplines** (clan-specific vampire powers)
- Character progression and experience tracking

#### 🤖 Character-Aware Storyteller
When you have a linked or created character, the AI automatically:
- References your character's clan and abilities
- Suggests appropriate actions based on your Disciplines
- Tracks your current Hunger and Humanity
- Provides contextual guidance for your character type

### Supported Clans

| Clan | Disciplines |
|------|-------------|
| **Brujah** | Celerity, Potence, Presence |
| **Gangrel** | Animalism, Fortitude, Protean |
| **Malkavian** | Auspex, Dominate, Obfuscate |
| **Nosferatu** | Animalism, Obfuscate, Potence |
| **Toreador** | Auspex, Celerity, Presence |
| **Tremere** | Auspex, Blood Sorcery, Dominate |
| **Ventrue** | Dominate, Fortitude, Presence |
| **Caitiff** | Choose any 3 disciplines |
| **Thin-Blood** | Thin-Blood Alchemy |

### How to Use

#### Link a Demiplane Character
1. Navigate to the **Character** tab
2. Click "Link Demiplane Character"
3. Enter your character sheet URL from Demiplane
4. Fill in character name, clan, and predator type
5. Click "Save Link"
6. Your character is now accessible to the Storyteller!

#### Create a Custom Character
1. Navigate to the **Character** tab
2. Click "Create Custom Character"
3. Follow the 5-step wizard:
   - **Step 1**: Basic Information (Name, Concept, Chronicle)
   - **Step 2**: Choose Your Clan (9 clans available)
   - **Step 3**: Distribute Attributes (7 dots per category)
   - **Step 4**: Distribute Skills (13 total dots)
   - **Step 5**: Choose Disciplines (2 dots from clan options)
4. Click "Create Character"
5. View your character in the **Character Sheet** tab

#### Roll Dice
1. Navigate to the **Dice Roller** tab
2. Set your **pool size** (Attribute + Skill + modifiers)
3. Set **hunger dice** (0-5, representing your current Hunger)
4. Set **difficulty** (target number of successes)
5. Click "ROLL"
6. View detailed results with automatic interpretation

### API Endpoints (New)

#### Character Management
```
POST /character/link        - Link Demiplane character
POST /character/create      - Create custom character
GET  /character/<id>        - Get character details
PUT  /character/<id>        - Update character stats
```

#### Dice Rolling
```
POST /roll                  - Roll VTM 5e dice pool
  Parameters:
    - pool: int (total dice to roll)
    - hunger: int (hunger dice, 0-5)
    - user_id: string
    - character_id: int (optional)
    - context: string (optional)
  
  Returns:
    - normal_dice: array of results
    - hunger_dice: array of results
    - successes: int
    - critical: boolean
    - messy_critical: boolean
    - bestial_failure: boolean
```

### Database Schema (New Tables)

```sql
-- Demiplane character links
CREATE TABLE demiplane_links (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    character_id TEXT,
    demiplane_url TEXT,
    character_name TEXT,
    clan TEXT,
    predator_type TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Custom character sheets
CREATE TABLE character_sheets (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    name TEXT,
    clan TEXT,
    predator_type TEXT,
    generation INTEGER,
    attributes JSON,
    skills JSON,
    disciplines JSON,
    health INTEGER,
    willpower INTEGER,
    humanity INTEGER,
    hunger INTEGER,
    blood_potency INTEGER,
    experience INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Dice roll history
CREATE TABLE dice_rolls (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    character_id INTEGER,
    pool_size INTEGER,
    hunger_dice INTEGER,
    results JSON,
    successes INTEGER,
    critical BOOLEAN,
    messy_critical BOOLEAN,
    bestial_failure BOOLEAN,
    context TEXT,
    timestamp TIMESTAMP
);
```

### Technical Implementation

- **Frontend**: Vanilla JavaScript with modern ES6+ features
- **Backend**: Flask with SQLite database
- **AI Integration**: Character context automatically injected into prompts
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Gothic Theme**: Dark red/black color scheme matching VTM aesthetic

### Benefits of Hybrid Approach

1. **Flexibility**: Choose the system that fits your playstyle
2. **No Vendor Lock-in**: Works with or without Demiplane
3. **Best of Both Worlds**: Professional sheets OR quick creation
4. **Seamless Integration**: Both options work identically with the AI
5. **Future-Proof**: Easy to add more integrations (Roll20, D&D Beyond, etc.)

---

## Author & Owner

**MarquesDeCarabas**  
ilmarquesducarabas@gmail.com

This is a personal project for VTM 5e gameplay.

---

**System Status**: ✅ Fully Operational  
**Last Updated**: October 17, 2025  
**Version**: 2.0 (Hybrid Character System)
