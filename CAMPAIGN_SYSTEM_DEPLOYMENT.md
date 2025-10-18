# Campaign and Session Management System - Deployment Guide

## Overview

This deployment adds a comprehensive Campaign and Session Management system to the VTM Storyteller, including:

- Campaign creation and management UI
- Session tracking with start/end controls
- Command system with `/campaign`, `/session`, `/npc`, `/location`, `/item` commands
- Commands help modal
- Persistent memory across sessions
- Multi-campaign support

## Files Included

### Backend Files:
1. `campaign_database_schema.py` - Database schema for campaigns, sessions, NPCs, locations, items
2. `campaign_auto_save.py` - Auto-save system for AI-generated content
3. `campaign_recall.py` - Search and recall functionality
4. `campaign_ai_integration.py` - AI context integration
5. `campaign_session_api.py` - API endpoints for campaign/session management
6. `command_system.py` - Command parser and handler

### Frontend Files:
7. `campaign_session_ui.html` - UI components (CSS + HTML + JavaScript)

### Modified Files:
8. `app.py` - Updated with:
   - Import statements for campaign modules
   - Command system integration in chat endpoint
   - API routes for campaigns and sessions

## Deployment Steps

### 1. Upload Files to GitHub

Upload the following files:
- `campaign_database_schema.py`
- `campaign_auto_save.py`
- `campaign_recall.py`
- `campaign_ai_integration.py`
- `campaign_session_api.py`
- `command_system.py`
- `campaign_session_ui.html`
- `app.py` (modified)
- `CAMPAIGN_SYSTEM_DEPLOYMENT.md` (this file)

### 2. Database Initialization

The system will automatically create the necessary tables on first run:
- `campaigns`
- `campaign_sessions`
- `campaign_npcs`
- `campaign_locations`
- `campaign_items`
- `campaign_events`
- `npc_relationships`

### 3. UI Integration (Manual Step)

The campaign UI needs to be integrated into the HTML template in `app.py`. 

**Insert Location:** After the `<header>` section and before the `<div class="tabs">` section.

**What to Insert:** The entire content of `campaign_session_ui.html`

This includes:
- Campaign Management Panel (CSS)
- Session Controls (CSS)
- Commands Modal (CSS + HTML)
- New Campaign Modal (CSS + HTML)
- JavaScript for campaign/session management

## Features

### Campaign Management
- Create new campaigns with name, city, faction, description
- Load existing campaigns from dropdown
- View campaign info (sessions, NPCs, locations, items count)
- Automatic campaign selection persistence

### Session Management
- Start/End session buttons with visual indicators
- Session counter
- Auto-save on session end
- Session summary generation

### Command System

#### Campaign Commands:
```
/campaign new <name> - Create a new campaign
/campaign load <name> - Load an existing campaign
/campaign list - List all campaigns
/campaign info - Show current campaign details
```

#### Session Commands:
```
/session start - Start a new session
/session end - End current session
/session summary - Get session summary
```

#### Database Commands:
```
/npc list - List all NPCs
/npc search <name> - Search for NPCs
/location list - List all locations
/location search <name> - Search for locations
/item list - List all items
/item search <name> - Search for items
```

#### Help Commands:
```
/help - Show all commands
/help <command> - Get detailed help for a command
```

### Commands Help Modal
- Accessible via "📋 Commands" button
- Categorized command list
- Syntax, description, and examples for each command
- Keyboard shortcut support

## API Endpoints

### Campaign Endpoints:
- `GET /api/campaigns` - Get all campaigns
- `GET /api/campaigns/<id>` - Get specific campaign
- `POST /api/campaigns` - Create new campaign
- `PUT /api/campaigns/<id>` - Update campaign
- `DELETE /api/campaigns/<id>` - Delete campaign

### Session Endpoints:
- `POST /api/session/start` - Start new session
- `POST /api/session/end` - End current session
- `GET /api/session/<id>/summary` - Get session summary
- `GET /api/campaigns/<id>/sessions` - Get all sessions for campaign

### Database Query Endpoints:
- `GET /api/campaigns/<id>/npcs` - List NPCs
- `GET /api/campaigns/<id>/npcs/search?q=<term>` - Search NPCs
- `GET /api/campaigns/<id>/locations` - List locations
- `GET /api/campaigns/<id>/locations/search?q=<term>` - Search locations
- `GET /api/campaigns/<id>/items` - List items
- `GET /api/campaigns/<id>/items/search?q=<term>` - Search items

## Testing Checklist

After deployment, test the following:

### Campaign Management:
- [ ] Create a new campaign via UI
- [ ] Create a campaign via `/campaign new` command
- [ ] Load campaign from dropdown
- [ ] View campaign info with `/campaign info`
- [ ] List campaigns with `/campaign list`

### Session Management:
- [ ] Start a session via button
- [ ] Start a session via `/session start`
- [ ] Session indicator shows "active"
- [ ] End session via button
- [ ] End session via `/session end`
- [ ] Session summary via `/session summary`

### Database Queries:
- [ ] List NPCs with `/npc list`
- [ ] Search NPCs with `/npc search <name>`
- [ ] List locations with `/location list`
- [ ] Search locations with `/location search <name>`
- [ ] List items with `/item list`
- [ ] Search items with `/item search <name>`

### UI Elements:
- [ ] Campaign selector dropdown works
- [ ] "New Campaign" button opens modal
- [ ] "Commands" button opens help modal
- [ ] Session start/end buttons toggle correctly
- [ ] Campaign info displays correctly

### AI Integration:
- [ ] AI remembers NPCs from previous sessions
- [ ] AI remembers locations from previous sessions
- [ ] AI remembers items from previous sessions
- [ ] Commands return proper responses
- [ ] Error messages display correctly

## Troubleshooting

### Commands not working:
- Check that `command_system.py` is imported in `app.py`
- Verify command integration in chat endpoint
- Check browser console for JavaScript errors

### Campaign UI not showing:
- Verify `campaign_session_ui.html` content is inserted into HTML template
- Check for CSS conflicts
- Verify API endpoints are accessible

### Database errors:
- Run `campaign_database_schema.py` manually to create tables
- Check database file permissions
- Verify SQLite3 is available

### API errors:
- Check that all campaign modules are imported
- Verify Flask routes are registered
- Check server logs for Python errors

## Notes

- The system uses Flask sessions for tracking active campaign/session
- Campaign data persists across server restarts
- NPCs, locations, and items can be reused across multiple campaigns
- The command system is extensible - new commands can be added easily

## Future Enhancements

Potential improvements for future versions:
- Campaign export/import functionality
- Session notes and journal
- NPC relationship graphs
- Location maps integration
- Item inventory management
- Character-NPC relationship tracking
- Timeline visualization
- Campaign statistics dashboard

## Support

For issues or questions:
1. Check server logs for errors
2. Verify all files are uploaded correctly
3. Test API endpoints directly with curl/Postman
4. Check browser console for JavaScript errors
5. Review this deployment guide for missed steps

