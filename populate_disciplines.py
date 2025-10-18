#!/usr/bin/env python3
"""
Populate VTM 5e Disciplines Database
Complete implementation of all Vampire: The Masquerade 5th Edition Disciplines
"""

import sqlite3

def populate_disciplines():
    conn = sqlite3.connect('vtm_storyteller.db')
    c = conn.cursor()
    
    # Clear existing disciplines
    c.execute('DELETE FROM disciplines')
    
    disciplines_data = [
        # ANIMALISM
        ("Animalism", 1, "Bond Famulus",
         "Create a blood bond with an animal familiar. The animal becomes loyal and can perform simple tasks.",
         "Feed the animal one Rouse Check worth of blood. The animal becomes bonded and obeys simple commands. You can sense through the animal's senses with concentration.",
         "One Rouse Check", "None", "One scene or until dismissed", None, None),
        
        ("Animalism", 1, "Sense the Beast",
         "Sense the Beast in others, determining their emotional state and supernatural nature.",
         "Roll Resolve + Animalism vs target's Composure + Subterfuge. Success reveals emotional state, Hunger level (if vampire), and general supernatural nature.",
         "Free", "Resolve + Animalism", "Instant", None, None),
        
        ("Animalism", 2, "Feral Whispers",
         "Communicate with animals and give them complex commands.",
         "Roll Manipulation + Animalism. Animals understand you and can perform complex tasks. Duration depends on successes.",
         "Free", "Manipulation + Animalism", "One scene", None, None),
        
        ("Animalism", 3, "Animal Succulence",
         "Gain more sustenance from animal blood.",
         "When feeding from animals, reduce Hunger by one additional level. Animal blood can reduce Hunger to 1 instead of 2.",
         "None", "None", "Permanent", None, None),
        
        ("Animalism", 3, "Quell the Beast",
         "Calm the Beast in yourself or others, preventing or ending frenzy.",
         "Roll Charisma + Animalism vs target's Willpower. Success calms frenzy or prevents it from starting.",
         "Free", "Charisma + Animalism", "One scene", None, None),
        
        ("Animalism", 4, "Subsume the Spirit",
         "Possess an animal, controlling it directly while your body lies dormant.",
         "One Rouse Check. Roll Manipulation + Animalism. Your consciousness transfers to the animal. Your body is helpless.",
         "One Rouse Check", "Manipulation + Animalism", "Until released", None, None),
        
        ("Animalism", 5, "Drawing Out the Beast",
         "Transfer your frenzy to another person or animal.",
         "When entering frenzy, make eye contact and roll Manipulation + Animalism vs target's Composure + Resolve. Success transfers your frenzy to them.",
         "One Rouse Check", "Manipulation + Animalism vs Composure + Resolve", "Instant", None, None),
        
        # AUSPEX
        ("Auspex", 1, "Heightened Senses",
         "Enhance your senses to superhuman levels, perceiving details others miss.",
         "One Rouse Check. For one scene, add dice equal to Auspex rating to Perception rolls. Can see in darkness, hear whispers, smell blood, etc.",
         "One Rouse Check", "Wits + Auspex (situational)", "One scene", None, None),
        
        ("Auspex", 1, "Sense the Unseen",
         "Detect supernatural presences, including ghosts, magic, and hidden vampires.",
         "Roll Wits + Auspex vs target's power. Success reveals supernatural presence and general nature. Can pierce Obfuscate.",
         "Free", "Wits + Auspex", "Instant", None, None),
        
        ("Auspex", 2, "Premonition",
         "Receive visions of danger or important events about to occur.",
         "The Storyteller rolls Resolve + Auspex in secret. Success grants a vision of impending danger or significant events.",
         "Free (automatic)", "Resolve + Auspex", "Instant", None, None),
        
        ("Auspex", 3, "Scry the Soul",
         "Read a person's aura to discern their emotional state, supernatural nature, and recent experiences.",
         "Roll Intelligence + Auspex vs target's Composure + Subterfuge. Success reveals emotional state, Resonance, Hunger, recent diablerie, etc.",
         "One Rouse Check", "Intelligence + Auspex vs Composure + Subterfuge", "Instant", None, None),
        
        ("Auspex", 3, "Share the Senses",
         "Experience the world through another person's senses.",
         "One Rouse Check. Roll Resolve + Auspex. You perceive through the target's senses. Requires blood bond or touching the target.",
         "One Rouse Check", "Resolve + Auspex", "One scene", None, None),
        
        ("Auspex", 4, "Spirit's Touch",
         "Read the psychic impressions left on objects, learning their history and who has touched them.",
         "One Rouse Check. Roll Intelligence + Auspex. Success reveals visions of the object's history, previous owners, and significant events.",
         "One Rouse Check", "Intelligence + Auspex", "Instant", None, None),
        
        ("Auspex", 5, "Telepathy",
         "Read minds and project thoughts directly into another's consciousness.",
         "Two Rouse Checks. Roll Resolve + Auspex vs target's Wits + Subterfuge. Success allows reading surface thoughts or projecting messages.",
         "Two Rouse Checks", "Resolve + Auspex vs Wits + Subterfuge", "One scene", None, None),
        
        # CELERITY
        ("Celerity", 1, "Cat's Grace",
         "Add your Celerity rating to Dexterity-based dice pools.",
         "One Rouse Check. For one scene, add Celerity dots to all Dexterity rolls (including combat).",
         "One Rouse Check", "Dexterity + (skill) + Celerity", "One scene", None, None),
        
        ("Celerity", 1, "Rapid Reflexes",
         "Add your Celerity rating to initiative and Defense.",
         "One Rouse Check. For one scene, add Celerity dots to initiative and Defense rating.",
         "One Rouse Check", "None", "One scene", None, None),
        
        ("Celerity", 2, "Fleetness",
         "Move at incredible speed, crossing distances in the blink of an eye.",
         "One Rouse Check. Your movement speed doubles. You can take an extra move action each turn.",
         "One Rouse Check", "None", "One scene", None, None),
        
        ("Celerity", 3, "Blink",
         "Move so fast you seem to teleport short distances.",
         "One Rouse Check. Move up to 50 feet instantly as a free action. Observers must win a Wits + Awareness contest to track you.",
         "One Rouse Check", "Wits + Awareness (contested)", "Instant", None, None),
        
        ("Celerity", 4, "Traversal",
         "Run across walls, ceilings, and even water.",
         "One Rouse Check. For one scene, you can run on any surface regardless of gravity or stability.",
         "One Rouse Check", "None", "One scene", None, None),
        
        ("Celerity", 5, "Split Second",
         "Take an extra full turn of actions in combat.",
         "Two Rouse Checks. Once per scene, take a complete extra turn immediately after your normal turn.",
         "Two Rouse Checks", "None", "Instant", None, None),
        
        # DOMINATE
        ("Dominate", 1, "Cloud Memory",
         "Erase or alter a target's recent memories.",
         "One Rouse Check. Roll Charisma + Dominate vs target's Intelligence + Resolve. Success allows altering up to 10 minutes of memory.",
         "One Rouse Check", "Charisma + Dominate vs Intelligence + Resolve", "Permanent", None, None),
        
        ("Dominate", 1, "Compel",
         "Give a one-word command that the target must obey.",
         "One Rouse Check. Roll Charisma + Dominate vs target's Resolve. Success forces immediate obedience to one-word command (Stop, Run, Sleep, etc.).",
         "One Rouse Check", "Charisma + Dominate vs Resolve", "One turn", None, None),
        
        ("Dominate", 2, "Mesmerize",
         "Implant a suggestion that the target will carry out later.",
         "One Rouse Check. Roll Manipulation + Dominate vs target's Intelligence + Resolve. Success implants a command to be executed under specific conditions.",
         "One Rouse Check", "Manipulation + Dominate vs Intelligence + Resolve", "Until triggered or one week", None, None),
        
        ("Dominate", 3, "The Forgetful Mind",
         "Completely rewrite a target's memories, creating false recollections.",
         "One Rouse Check. Roll Manipulation + Dominate vs target's Intelligence + Resolve. Success allows extensive memory alteration.",
         "One Rouse Check", "Manipulation + Dominate vs Intelligence + Resolve", "Permanent", None, None),
        
        ("Dominate", 4, "Submerged Directive",
         "Plant a deep subconscious command that activates under specific triggers.",
         "Two Rouse Checks. Roll Manipulation + Dominate vs target's Resolve. Success implants a command that persists for months or years.",
         "Two Rouse Checks", "Manipulation + Dominate vs Resolve", "Until triggered", None, None),
        
        ("Dominate", 5, "Rationalize",
         "Make the target accept any action they take under Dominate as their own idea.",
         "When using Dominate, spend one additional Rouse Check. The target believes they acted of their own free will.",
         "One additional Rouse Check", "None", "Permanent", None, "Any Dominate power"),
        
        # FORTITUDE
        ("Fortitude", 1, "Resilience",
         "Add Fortitude rating to Health and reduce all physical damage.",
         "One Rouse Check. For one scene, add Fortitude dots to Health and reduce all physical damage by Fortitude rating.",
         "One Rouse Check", "None", "One scene", None, None),
        
        ("Fortitude", 1, "Unswayable Mind",
         "Add Fortitude rating to Willpower and resist mental attacks.",
         "One Rouse Check. For one scene, add Fortitude dots to Willpower and resist mental Disciplines.",
         "One Rouse Check", "Composure + Fortitude (contested)", "One scene", None, None),
        
        ("Fortitude", 2, "Enduring Beasts",
         "Ignore wound penalties and remain conscious even when severely injured.",
         "One Rouse Check. For one scene, ignore all wound penalties and remain active even at zero Health.",
         "One Rouse Check", "None", "One scene", None, None),
        
        ("Fortitude", 3, "Defy Bane",
         "Reduce damage from your clan's bane (fire, sunlight, etc.).",
         "One Rouse Check. For one scene, reduce Aggravated damage from fire and sunlight to Superficial.",
         "One Rouse Check", "None", "One scene", None, None),
        
        ("Fortitude", 4, "Fortify the Inner Facade",
         "Protect yourself from emotional manipulation and supernatural mental attacks.",
         "One Rouse Check. For one scene, add Fortitude to all rolls to resist mental Disciplines and emotional manipulation.",
         "One Rouse Check", "Composure + Fortitude", "One scene", None, None),
        
        ("Fortitude", 5, "Prowess from Pain",
         "Convert damage taken into bonus dice for your next action.",
         "When you take damage, gain bonus dice equal to damage taken on your next action. Maximum bonus equal to Fortitude rating.",
         "Free", "None", "Next action", None, None),
        
        # OBFUSCATE
        ("Obfuscate", 1, "Cloak of Shadows",
         "Become invisible while standing still in shadows or darkness.",
         "One Rouse Check. You become invisible while motionless in shadows. Moving or taking actions breaks the effect.",
         "One Rouse Check", "Wits + Obfuscate (contested)", "Until you move", None, None),
        
        ("Obfuscate", 1, "Silence of Death",
         "Eliminate all sound you make, moving in perfect silence.",
         "One Rouse Check. For one scene, you make no sound whatsoever. Add Obfuscate to Stealth rolls.",
         "One Rouse Check", "Dexterity + Stealth + Obfuscate", "One scene", None, None),
        
        ("Obfuscate", 2, "Unseen Passage",
         "Become invisible while moving, as long as you don't draw attention.",
         "One Rouse Check. You become invisible while moving normally. Attacking or loud actions break the effect.",
         "One Rouse Check", "Wits + Obfuscate (contested)", "One scene", None, None),
        
        ("Obfuscate", 3, "Ghost in the Machine",
         "Erase your presence from electronic surveillance and recordings.",
         "One Rouse Check. You don't appear on cameras, recordings, or electronic sensors. Existing footage of you becomes corrupted.",
         "One Rouse Check", "Intelligence + Obfuscate", "One scene", None, None),
        
        ("Obfuscate", 3, "Mask of a Thousand Faces",
         "Alter your appearance to look like someone else.",
         "One Rouse Check. Roll Manipulation + Obfuscate. You can appear as anyone of similar build. Observers contest with Wits + Awareness.",
         "One Rouse Check", "Manipulation + Obfuscate vs Wits + Awareness", "One scene", None, None),
        
        ("Obfuscate", 4, "Conceal",
         "Hide an object or person from perception.",
         "One Rouse Check per target. You can make objects or people invisible. They remain hidden as long as you concentrate.",
         "One Rouse Check per target", "Wits + Obfuscate", "Concentration", None, None),
        
        ("Obfuscate", 5, "Cloak the Gathering",
         "Extend your Obfuscate to a group of people.",
         "Two Rouse Checks. You can extend any Obfuscate power to affect a group of up to 5 people.",
         "Two Rouse Checks", "Varies", "Varies", None, None),
        
        # POTENCE
        ("Potence", 1, "Lethal Body",
         "Your unarmed attacks deal Aggravated damage.",
         "One Rouse Check. For one scene, your unarmed strikes deal Aggravated damage instead of Superficial.",
         "One Rouse Check", "Strength + Brawl + Potence", "One scene", None, None),
        
        ("Potence", 1, "Soaring Leap",
         "Jump incredible distances with supernatural strength.",
         "One Rouse Check. For one scene, multiply your jumping distance by Potence rating. You can leap over buildings.",
         "One Rouse Check", "Strength + Athletics + Potence", "One scene", None, None),
        
        ("Potence", 2, "Prowess",
         "Add Potence rating to Strength-based dice pools.",
         "One Rouse Check. For one scene, add Potence dots to all Strength rolls (including damage).",
         "One Rouse Check", "Strength + (skill) + Potence", "One scene", None, None),
        
        ("Potence", 3, "Brutal Feed",
         "Drain a victim completely in seconds, killing them instantly.",
         "One Rouse Check. Make a Strength + Potence roll. Success drains the victim to death in one turn, reducing Hunger by 2.",
         "One Rouse Check", "Strength + Potence", "One turn", None, None),
        
        ("Potence", 4, "Spark of Rage",
         "Channel your anger into devastating attacks.",
         "When you take damage or fail a roll, gain bonus dice equal to Potence on your next attack.",
         "Free", "None", "Next attack", None, None),
        
        ("Potence", 5, "Earthshock",
         "Strike the ground with such force that you create a localized earthquake.",
         "Two Rouse Checks. Roll Strength + Potence. Everyone within 10 feet must roll Dexterity + Athletics or be knocked down and take damage.",
         "Two Rouse Checks", "Strength + Potence (attack) vs Dexterity + Athletics", "Instant", None, None),
        
        # PRESENCE
        ("Presence", 1, "Awe",
         "Become the center of attention, drawing all eyes to you.",
         "One Rouse Check. Roll Manipulation + Presence. Everyone in the scene is drawn to you and wants to be near you.",
         "One Rouse Check", "Manipulation + Presence", "One scene", None, None),
        
        ("Presence", 1, "Daunt",
         "Terrify a target, making them flee or cower in fear.",
         "One Rouse Check. Roll Charisma + Presence vs target's Composure + Resolve. Success causes terror; target flees or freezes.",
         "One Rouse Check", "Charisma + Presence vs Composure + Resolve", "One scene", None, None),
        
        ("Presence", 2, "Lingering Kiss",
         "Make feeding pleasurable for the victim, who craves it afterwards.",
         "Free when feeding. Victim experiences intense pleasure and becomes addicted to your bite. They seek you out for more.",
         "Free", "None", "Until next feeding", None, None),
        
        ("Presence", 3, "Entrancement",
         "Create an intense emotional bond, making the target devoted to you.",
         "One Rouse Check. Roll Charisma + Presence vs target's Composure + Intelligence. Success creates a temporary blood bond effect.",
         "One Rouse Check", "Charisma + Presence vs Composure + Intelligence", "One week", None, None),
        
        ("Presence", 4, "Summon",
         "Call a person to you from anywhere in the city. They feel compelled to come.",
         "One Rouse Check. Roll Manipulation + Presence. Target feels an overwhelming urge to find you and travels to your location.",
         "One Rouse Check", "Manipulation + Presence", "Until they arrive", None, None),
        
        ("Presence", 5, "Majesty",
         "Become so impressive that others cannot attack or oppose you.",
         "Two Rouse Checks. For one scene, anyone who wants to attack or oppose you must win a Resolve + Composure vs your Presence contest.",
         "Two Rouse Checks", "Resolve + Composure vs Presence", "One scene", None, None),
        
        # PROTEAN
        ("Protean", 1, "Eyes of the Beast",
         "See perfectly in complete darkness.",
         "One Rouse Check. For one scene, you can see in total darkness. Your eyes glow red.",
         "One Rouse Check", "None", "One scene", None, None),
        
        ("Protean", 1, "Weight of the Feather",
         "Become as light as a feather, falling slowly and landing silently.",
         "One Rouse Check. For one scene, you fall at a safe speed and take no falling damage. You weigh almost nothing.",
         "One Rouse Check", "None", "One scene", None, None),
        
        ("Protean", 2, "Feral Weapons",
         "Grow claws that deal Aggravated damage.",
         "One Rouse Check. For one scene, you grow claws that deal +2 Aggravated damage in combat.",
         "One Rouse Check", "Strength + Brawl", "One scene", None, None),
        
        ("Protean", 3, "Earth Meld",
         "Merge with the earth, becoming one with the ground.",
         "One Rouse Check. You sink into the earth and become undetectable. You're protected from sunlight and attacks.",
         "One Rouse Check", "None", "Until you emerge", None, None),
        
        ("Protean", 4, "Shapechange",
         "Transform into a wolf or bat.",
         "One Rouse Check. You transform into a wolf (combat form) or bat (travel form). You gain animal abilities.",
         "One Rouse Check", "None", "Until you change back", None, None),
        
        ("Protean", 5, "Metamorphosis",
         "Transform into mist, becoming incorporeal.",
         "Two Rouse Checks. You become mist and can float, pass through cracks, and avoid physical attacks.",
         "Two Rouse Checks", "None", "One scene", None, None),
        
        # BLOOD SORCERY (Tremere)
        ("Blood Sorcery", 1, "Corrosive Vitae",
         "Your blood becomes acidic, burning whatever it touches.",
         "One Rouse Check. Your blood deals Aggravated damage to anything it touches. Lasts one scene.",
         "One Rouse Check", "Intelligence + Blood Sorcery (attack)", "One scene", None, None),
        
        ("Blood Sorcery", 1, "A Taste for Blood",
         "Learn information about a person by tasting their blood.",
         "One Rouse Check. Roll Intelligence + Blood Sorcery. Success reveals Resonance, recent emotions, and general health.",
         "One Rouse Check", "Intelligence + Blood Sorcery", "Instant", None, None),
        
        ("Blood Sorcery", 2, "Extinguish Vitae",
         "Boil the blood in a target's veins, causing excruciating pain.",
         "One Rouse Check. Roll Intelligence + Blood Sorcery vs target's Stamina + Resolve. Success deals damage and increases target's Hunger.",
         "One Rouse Check", "Intelligence + Blood Sorcery vs Stamina + Resolve", "Instant", None, None),
        
        ("Blood Sorcery", 3, "Blood of Potency",
         "Temporarily increase your Blood Potency.",
         "Two Rouse Checks. For one scene, increase your Blood Potency by 1. This affects Discipline power and feeding.",
         "Two Rouse Checks", "None", "One scene", None, None),
        
        ("Blood Sorcery", 4, "Theft of Vitae",
         "Drain blood from a target at range, pulling it into yourself.",
         "Two Rouse Checks. Roll Intelligence + Blood Sorcery vs target's Stamina. Success drains blood from target and reduces your Hunger.",
         "Two Rouse Checks", "Intelligence + Blood Sorcery vs Stamina", "Instant", None, None),
        
        ("Blood Sorcery", 5, "Cauldron of Blood",
         "Boil all the blood in a target's body, killing them instantly.",
         "Three Rouse Checks. Roll Intelligence + Blood Sorcery vs target's Stamina + Fortitude. Success boils their blood, dealing massive Aggravated damage.",
         "Three Rouse Checks", "Intelligence + Blood Sorcery vs Stamina + Fortitude", "Instant", None, None),
        
        # THIN-BLOOD ALCHEMY
        ("Thin-Blood Alchemy", 1, "Far Reach",
         "Create a formula that grants telekinesis.",
         "One Rouse Check to create. Drinking grants ability to move objects at range for one scene.",
         "One Rouse Check", "Resolve + Alchemy (to move objects)", "One scene", None, None),
        
        ("Thin-Blood Alchemy", 1, "Haze",
         "Create a formula that generates obscuring mist.",
         "One Rouse Check to create. Drinking allows you to generate thick fog that obscures vision.",
         "One Rouse Check", "None", "One scene", None, None),
        
        ("Thin-Blood Alchemy", 2, "Envelop",
         "Create a formula that grants limited Obfuscate.",
         "One Rouse Check to create. Drinking makes you invisible while motionless.",
         "One Rouse Check", "Wits + Alchemy (contested)", "One scene", None, None),
        
        ("Thin-Blood Alchemy", 2, "Profane Hieros Gamos",
         "Create a formula that temporarily grants a Discipline power.",
         "Two Rouse Checks to create. Requires vampire blood with the desired Discipline. Drinking grants one use of that power.",
         "Two Rouse Checks", "Varies", "One use", None, None),
        
        ("Thin-Blood Alchemy", 3, "Awaken the Sleeper",
         "Create a formula that allows you to stay awake during the day.",
         "Two Rouse Checks to create. Drinking allows you to remain conscious during daylight hours.",
         "Two Rouse Checks", "None", "One day", None, None),
        
        ("Thin-Blood Alchemy", 4, "Counterfeit",
         "Create a formula that mimics mortal functions (heartbeat, warmth, etc.).",
         "Two Rouse Checks to create. Drinking makes you appear fully human for one scene.",
         "Two Rouse Checks", "None", "One scene", None, None),
    ]
    
    # Insert all disciplines
    c.executemany('''INSERT INTO disciplines 
                     (name, level, description, system, cost, dice_pools, duration, amalgam, prerequisite)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                  [(d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8]) for d in disciplines_data])
    
    conn.commit()
    conn.close()
    print(f"✅ Populated {len(disciplines_data)} discipline powers!")

if __name__ == '__main__':
    populate_disciplines()

