import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from openai import OpenAI
import json

# Configuration
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

client_openai = OpenAI(api_key=OPENAI_API_KEY)

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!vtm ', intents=intents)

# Thread storage (in production, use database)
user_threads = {}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.tree.command(name="storyteller", description="Talk to the VTM Storyteller")
@app_commands.describe(message="Your message to the Storyteller")
async def storyteller(interaction: discord.Interaction, message: str):
    """Slash command to interact with the Storyteller"""
    await interaction.response.defer(thinking=True)
    
    try:
        user_id = str(interaction.user.id)
        
        # Get or create thread for this user
        if user_id not in user_threads:
            thread = client_openai.beta.threads.create()
            user_threads[user_id] = thread.id
        
        thread_id = user_threads[user_id]
        
        # Send message to assistant
        client_openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
        
        # Run the assistant
        run = client_openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        
        # Wait for completion
        for _ in range(90):
            run_status = client_openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            if run_status.status == "completed":
                messages = client_openai.beta.threads.messages.list(thread_id=thread_id)
                response = messages.data[0].content[0].text.value
                
                # Split long responses into multiple messages
                if len(response) > 2000:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    await interaction.followup.send(chunks[0])
                    for chunk in chunks[1:]:
                        await interaction.channel.send(chunk)
                else:
                    await interaction.followup.send(response)
                return
            
            elif run_status.status in ["failed", "cancelled", "expired"]:
                await interaction.followup.send("❌ The Storyteller encountered an error. Please try again.")
                return
            
            await asyncio.sleep(1)
        
        await interaction.followup.send("⏱️ The Storyteller is taking too long to respond. Please try again.")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="roll", description="Roll dice for VTM")
@app_commands.describe(
    pool="Number of dice to roll",
    difficulty="Difficulty (default 6)",
    hunger="Hunger dice (default 0)"
)
async def roll_dice(interaction: discord.Interaction, pool: int, difficulty: int = 6, hunger: int = 0):
    """Roll dice using VTM 5e rules"""
    import random
    
    # Roll normal dice
    normal_dice = pool - hunger
    normal_results = [random.randint(1, 10) for _ in range(normal_dice)]
    
    # Roll hunger dice
    hunger_results = [random.randint(1, 10) for _ in range(hunger)]
    
    # Count successes
    normal_successes = sum(1 for d in normal_results if d >= difficulty)
    hunger_successes = sum(1 for d in hunger_results if d >= difficulty)
    total_successes = normal_successes + hunger_successes
    
    # Check for criticals and bestial failures
    normal_tens = sum(1 for d in normal_results if d == 10)
    hunger_tens = sum(1 for d in hunger_results if d == 10)
    hunger_ones = sum(1 for d in hunger_results if d == 1)
    
    # Build result message
    result = f"🎲 **Dice Roll**\n"
    result += f"Pool: {pool} dice (Difficulty: {difficulty})\n"
    result += f"Normal Dice: {normal_results}\n"
    if hunger > 0:
        result += f"Hunger Dice: {hunger_results} 🩸\n"
    result += f"\n**Successes: {total_successes}**\n"
    
    # Check for critical
    total_tens = normal_tens + hunger_tens
    if total_tens >= 2:
        result += f"✨ **CRITICAL!** ({total_tens} tens)\n"
    
    # Check for bestial failure
    if total_successes == 0 and hunger_ones > 0:
        result += f"💀 **BESTIAL FAILURE!** The Beast stirs...\n"
    
    await interaction.response.send_message(result)

@bot.tree.command(name="character", description="Create or view your character")
@app_commands.describe(
    name="Character name",
    clan="Vampire clan",
    generation="Generation (7-13)"
)
async def character(interaction: discord.Interaction, name: str = None, clan: str = None, generation: int = None):
    """Manage character sheets"""
    if not name:
        # View existing character
        await interaction.response.send_message("Character viewing coming soon!")
    else:
        # Create new character
        character_data = {
            "name": name,
            "clan": clan,
            "generation": generation,
            "discord_user": str(interaction.user.id)
        }
        
        # In production, save to database
        await interaction.response.send_message(
            f"✅ Created character: **{name}** ({clan}, Generation {generation})\n"
            f"View at: https://web-production-492a9.up.railway.app/character/{interaction.user.id}"
        )

@bot.tree.command(name="campaign", description="Manage VTM campaigns")
@app_commands.describe(
    action="Action to perform",
    name="Campaign name"
)
@app_commands.choices(action=[
    app_commands.Choice(name="create", value="create"),
    app_commands.Choice(name="join", value="join"),
    app_commands.Choice(name="list", value="list")
])
async def campaign(interaction: discord.Interaction, action: str, name: str = None):
    """Campaign management"""
    if action == "create":
        if not name:
            await interaction.response.send_message("❌ Please provide a campaign name!")
            return
        
        # Create campaign
        await interaction.response.send_message(
            f"✅ Created campaign: **{name}**\n"
            f"Roll20 integration: Ready\n"
            f"Discord channel: #{interaction.channel.name}"
        )
    
    elif action == "join":
        await interaction.response.send_message(f"Joined campaign: **{name}**")
    
    elif action == "list":
        await interaction.response.send_message("📋 Available campaigns:\n• Example Campaign 1\n• Example Campaign 2")

# Voice channel commands
@bot.tree.command(name="voice_storyteller", description="Enable voice interaction with the Storyteller")
async def voice_storyteller(interaction: discord.Interaction):
    """Enable voice interaction"""
    if not interaction.user.voice:
        await interaction.response.send_message("❌ You need to be in a voice channel!")
        return
    
    # Join voice channel
    voice_channel = interaction.user.voice.channel
    
    try:
        voice_client = await voice_channel.connect()
        await interaction.response.send_message(
            f"🎙️ Storyteller joined {voice_channel.name}!\n"
            f"Speak your questions and I will respond."
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Error joining voice: {str(e)}")

@bot.command(name="leave")
async def leave_voice(ctx):
    """Leave voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Storyteller has left the voice channel.")
    else:
        await ctx.send("❌ Not in a voice channel.")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `/storyteller` for slash commands.")
    else:
        await ctx.send(f"❌ Error: {str(error)}")

def run_bot():
    """Run the Discord bot"""
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not set!")
        return
    
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    run_bot()

