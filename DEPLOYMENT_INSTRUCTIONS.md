# VTM Storyteller v3.2 - Deployment Instructions

## 🚀 What's New in v3.2

### Fixed Issues
- ✅ Fixed JSON error in character endpoints
- ✅ Added missing CRUD endpoints for characters
- ✅ Fixed database schema for characters table

### New Features
- ✅ Complete VTM 5e rules database
  - Character creation rules
  - 9 Attributes with descriptions
  - 27 Skills with specializations
  - Combat mechanics
  - Hunger system (6 levels)
  - Humanity system (11 levels)
  - Experience costs
- ✅ New API endpoints:
  - `GET /character` - List all characters
  - `POST /character` - Create character
  - `GET /character/<id>` - Get specific character
  - `PUT /character/<id>` - Update character
  - `DELETE /character/<id>` - Delete character
  - `POST /character/link-demiplane` - Link Demiplane character
  - `GET /rules/<type>` - Get rules by type

---

## 📋 Deployment Steps

### Step 1: Run Database Migrations

After deployment, you need to run these scripts **once** to set up the database:

```bash
# SSH into Railway container or run locally
python3 fix_character_system.py
python3 migrate_characters_table.py
```

These scripts will:
1. Create all VTM 5e rules tables
2. Populate with complete rule sets
3. Migrate characters table to new schema

### Step 2: Verify Endpoints

Test the new endpoints:

```bash
# Health check
curl https://web-production-492a9.up.railway.app/health

# List characters
curl https://web-production-492a9.up.railway.app/character

# Get rules
curl https://web-production-492a9.up.railway.app/rules/attributes
curl https://web-production-492a9.up.railway.app/rules/skills
curl https://web-production-492a9.up.railway.app/rules/combat
curl https://web-production-492a9.up.railway.app/rules/hunger
curl https://web-production-492a9.up.railway.app/rules/humanity
```

---

## 🎯 What This Fixes

### Before (v3.1)
- ❌ Character tab showed "Unexpected token '<'" error
- ❌ No way to create/list characters via API
- ❌ Missing VTM 5e rules in database

### After (v3.2)
- ✅ Character tab works correctly
- ✅ Full CRUD API for characters
- ✅ Complete VTM 5e rules database
- ✅ Storyteller AI can access all rules

---

## 📊 Database Schema

### New Tables

1. **character_creation_rules** - Point distribution rules
2. **attributes_rules** - 9 attributes with descriptions
3. **skills_rules** - 27 skills with specializations
4. **combat_rules** - Combat mechanics and examples
5. **hunger_rules** - 6 hunger levels
6. **humanity_rules** - 11 humanity levels
7. **damage_healing_rules** - Damage types and healing
8. **experience_rules** - XP costs for advancement

### Updated Tables

- **characters** - Now includes all necessary columns:
  - Basic info: name, clan, concept, chronicle_id
  - Background: generation, sire, predator_type, ambition, desire
  - Stats: attributes, skills, disciplines, backgrounds
  - Trackers: health, willpower, humanity, hunger, experience
  - Integration: demiplane_url, portrait
  - Timestamps: created_at, updated_at

---

## 🔧 Troubleshooting

### If character tab still shows errors:

1. Clear browser cache
2. Check Railway logs for errors
3. Verify database migrations ran successfully
4. Test endpoints directly with curl

### If rules endpoints return 500:

1. Run `fix_character_system.py` again
2. Check database file exists and has correct permissions
3. Verify all tables were created

---

## 📞 Support

For issues, check:
- Railway logs: https://railway.com/project/[project-id]/logs
- GitHub repo: https://github.com/MarquesDeCarabas/vtm-storyteller
- Health endpoint: https://web-production-492a9.up.railway.app/health

---

**Version**: 3.2  
**Date**: 2025-10-17  
**Author**: MarquesDeCarabas

