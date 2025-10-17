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

