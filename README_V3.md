# 🧛 VTM Storyteller v3.0 - Enhanced Edition

**Vampire: The Masquerade 5th Edition AI Game Master**

A comprehensive web-based platform for running VTM 5e chronicles, featuring an AI-powered Storyteller, hybrid character management, advanced dice mechanics, and complete integration with Demiplane and Roll20.

---

## 🎉 What's New in v3.0

### **Major Features**

#### 1. 📜 **Roll History with Narrative Checkpoints**
- Complete log of all dice rolls with context
- Create checkpoints at critical narrative moments
- Rewind to any checkpoint and restart from there
- Track successes, failures, and messy criticals
- Session-by-session organization

#### 2. 📄 **PDF Character Sheet Export**
- Professional PDF generation
- Complete character stats and attributes
- Skills, Disciplines, and backgrounds
- Gothic VTM styling
- Download and print ready

#### 3. 🎲 **Roll20 Integration**
- Sync characters to Roll20
- Automatic stat updates
- Portrait synchronization
- One-click character export

#### 4. 🖼️ **Character Portraits**
- Upload custom character images
- Support for PNG, JPG, JPEG, GIF, WEBP
- 5MB max file size
- Automatic thumbnail generation

#### 5. 📚 **Chronicle Management**
- Create and track multiple chronicles
- Session numbering
- Chronicle descriptions and settings
- Storyteller notes
- Character-chronicle linking

#### 6. ⭐ **XP Tracking System**
- Automatic experience point tracking
- XP gain logging with reasons
- XP spending with validation
- Complete transaction history
- Current/total XP display

#### 7. 🔮 **Complete Disciplines Database**
- **69 discipline powers** from VTM 5e
- All 9 core Disciplines:
  - Animalism
  - Auspex
  - Celerity
  - Dominate
  - Fortitude
  - Obfuscate
  - Potence
  - Presence
  - Protean
- Blood Sorcery (Tremere)
- Thin-Blood Alchemy
- Detailed descriptions, systems, costs
- Dice pools and duration
- Amalgam and prerequisite info

---

## 🎮 Core Features (from v2.0)

### **Hybrid Character System**
- **Option A**: Link Demiplane characters
- **Option B**: Create custom characters with wizard
- Interactive character sheets
- Real-time stat tracking

### **AI Storyteller**
- GPT-4 powered narrative engine
- VTM 5e rules expert
- Character-aware storytelling
- Dynamic NPC generation
- Atmospheric descriptions

### **Advanced Dice Roller**
- VTM 5e mechanics (d10 system)
- Hunger dice tracking
- Success counting
- Critical wins detection
- Messy criticals and bestial failures
- Difficulty settings

---

## 🚀 Quick Start

### **Access the Application**
🌐 **https://web-production-492a9.up.railway.app/**

### **Create Your First Character**

#### **Option 1: Link Demiplane Character**
1. Go to **Character** tab
2. Click **Link Demiplane Character**
3. Enter your Demiplane character URL
4. Fill in basic info (name, clan, predator type)
5. Click **Link Character**

#### **Option 2: Create Custom Character**
1. Go to **Character** tab
2. Click **Create Custom Character**
3. Follow the 5-step wizard:
   - Basic Information
   - Clan Selection
   - Attributes (distribute points)
   - Skills (distribute points)
   - Disciplines (choose based on clan)
4. Click **Create Character**

### **Start Playing**
1. Go to **Chat** tab
2. Talk to the Storyteller AI
3. Describe your actions
4. When prompted, use **Dice Roller** tab
5. The Storyteller narrates results

---

## 📊 API Endpoints

### **Character Management**
- `POST /character/create` - Create new character
- `GET /character/<id>` - Get character details
- `PUT /character/<id>` - Update character
- `DELETE /character/<id>` - Delete character
- `POST /character/<id>/portrait` - Upload portrait
- `GET /character/<id>/portrait` - Get portrait
- `GET /character/<id>/export/pdf` - Export to PDF
- `POST /character/<id>/sync/roll20` - Sync to Roll20

### **Chronicle Management**
- `POST /chronicle/create` - Create chronicle
- `GET /chronicle/list` - List all chronicles
- `GET /chronicle/<id>` - Get chronicle details
- `PUT /chronicle/<id>` - Update chronicle

### **Roll History**
- `GET /roll/history/<character_id>` - Get roll history
- `POST /roll/checkpoint/create` - Create checkpoint
- `GET /roll/checkpoint/list/<character_id>` - List checkpoints

### **XP System**
- `POST /character/<id>/xp/add` - Add XP
- `POST /character/<id>/xp/spend` - Spend XP
- `GET /character/<id>/xp/history` - XP transaction history

### **Disciplines**
- `GET /disciplines/list` - List all discipline powers
- `GET /disciplines/<name>` - Get specific discipline

### **System**
- `GET /health` - System health check
- `POST /chat` - Chat with Storyteller AI

---

## 🎭 The Nine Clans

| Clan | Disciplines | Archetype |
|------|-------------|-----------|
| **Brujah** | Celerity, Potence, Presence | Rebels, Fighters |
| **Gangrel** | Animalism, Fortitude, Protean | Survivors, Loners |
| **Malkavian** | Auspex, Dominate, Obfuscate | Seers, Madmen |
| **Nosferatu** | Animalism, Obfuscate, Potence | Spies, Brokers |
| **Toreador** | Auspex, Celerity, Presence | Artists, Socialites |
| **Tremere** | Auspex, Blood Sorcery, Dominate | Sorcerers, Scholars |
| **Ventrue** | Dominate, Fortitude, Presence | Leaders, Nobles |
| **Caitiff** | Choose any 3 | Outcasts, Flexible |
| **Thin-Blood** | Thin-Blood Alchemy | Weak Vampires, Unique |

---

## 🎲 Dice Rolling Guide

### **Basic Roll**
1. Set **Pool Size** (Attribute + Skill)
2. Set **Hunger Dice** (current Hunger level)
3. Set **Difficulty** (number of successes needed)
4. Click **ROLL**

### **Interpreting Results**
- **Critical Win**: 2+ pairs of 10s (double successes)
- **Success**: Successes ≥ Difficulty
- **Failure**: Successes < Difficulty
- **Messy Critical**: Critical with Hunger dice showing 10s
- **Bestial Failure**: All Hunger dice show 1s

### **Common Dice Pools**
- **Perception Check**: Wits + Awareness
- **Melee Attack**: Strength + Brawl/Melee
- **Persuasion**: Manipulation + Persuasion
- **Stealth**: Dexterity + Stealth
- **Intimidation**: Charisma + Intimidation

---

## 📖 Using the Storyteller AI

### **Tips for Best Results**

1. **Be Descriptive**
   - Describe your character's actions in detail
   - Include emotional state and motivations
   - Reference your Disciplines when appropriate

2. **Ask Questions**
   - "What do I see?"
   - "Who is in the room?"
   - "What does the NPC want?"

3. **Declare Actions**
   - "I want to use Auspex to sense the unseen"
   - "I attempt to Dominate the guard"
   - "I feed from the victim"

4. **Request Rolls**
   - "Should I roll for this?"
   - "What's the difficulty?"
   - "Do I need to make a Rouse Check?"

### **Example Interaction**
```
You: I enter the Elysium and look for the Prince.

Storyteller: The grand hall of Elysium stretches before you, 
its vaulted ceilings adorned with gothic architecture. Several 
Kindred mill about, their conversations hushed. You spot Prince 
Vannevar near the throne, speaking with a Tremere advisor. 
What do you do?

You: I approach the Prince respectfully and bow.

Storyteller: The Prince acknowledges your presence with a slight 
nod. "Ah, another petitioner. State your business quickly, I have 
little patience tonight." Roll Charisma + Etiquette, difficulty 2.
```

---

## 🔧 Technical Details

### **Stack**
- **Backend**: Flask (Python 3.11)
- **AI**: OpenAI GPT-4
- **Database**: SQLite
- **PDF**: ReportLab
- **Deployment**: Railway
- **Frontend**: HTML5, CSS3, JavaScript

### **Database Schema**
- `characters` - Character data and stats
- `chronicles` - Chronicle information
- `roll_history` - Dice roll logs with checkpoints
- `xp_log` - Experience point transactions
- `disciplines` - Complete discipline powers database
- `health_logs` - System health monitoring

### **Environment Variables**
```
OPENAI_API_KEY=your_openai_api_key
```

---

## 📚 Resources

### **Official VTM 5e**
- [Renegade Game Studios](https://www.renegadegamestudios.com/vampire)
- [World of Darkness](https://www.worldofdarkness.com/)

### **Character Tools**
- [Demiplane](https://app.demiplane.com/) - Official character sheets
- [Roll20](https://roll20.net/) - Virtual tabletop
- [Mr. Gone's Character Sheets](https://mrgone.rocksolidshells.com/)

### **Community**
- [r/WhiteWolfRPG](https://www.reddit.com/r/WhiteWolfRPG/)
- [r/vtm](https://www.reddit.com/r/vtm/)

---

## 🐛 Troubleshooting

### **Character not saving**
- Check internet connection
- Verify all required fields are filled
- Try refreshing the page

### **Dice roller not working**
- Ensure Pool Size > 0
- Check that Hunger Dice ≤ Pool Size
- Refresh the page if stuck

### **PDF export fails**
- Character must be saved first
- Check that all stats are valid
- Try exporting again after a moment

### **Roll20 sync issues**
- Verify Roll20 credentials
- Check that character is saved
- Ensure Roll20 API access is enabled

---

## 📝 Changelog

### **v3.0 (2025-10-17)**
- ✅ Roll history with narrative checkpoints
- ✅ PDF character sheet export
- ✅ Roll20 API integration
- ✅ Character portrait upload
- ✅ Chronicle management system
- ✅ XP tracking and spending
- ✅ Complete disciplines database (69 powers)
- ✅ Enhanced database schema
- ✅ Improved error handling

### **v2.0 (2025-10-17)**
- ✅ Hybrid character system (Demiplane + Custom)
- ✅ Character creation wizard
- ✅ Interactive character sheets
- ✅ Advanced dice roller with Hunger mechanics
- ✅ Chat Completions API migration
- ✅ System health monitoring

### **v1.0 (2025-10-16)**
- ✅ Basic AI Storyteller
- ✅ Simple chat interface
- ✅ OpenAI integration

---

## 📄 License

This project is for personal use. Vampire: The Masquerade is © 2024 Renegade Game Studios. All rights reserved.

---

## Author & Owner

**MarquesDeCarabas**  
ilmarquesducarabas@gmail.com

This is a personal project for VTM 5e gameplay.

---

## 🙏 Credits

- **AI**: OpenAI GPT-4
- **VTM 5e**: Renegade Game Studios
- **Character Sheets**: Demiplane
- **Virtual Tabletop**: Roll20
- **Deployment**: Railway

---

**🌙 Welcome to the World of Darkness, Kindred. The night awaits... 🦇**

