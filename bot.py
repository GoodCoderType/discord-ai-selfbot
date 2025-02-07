try:
    import discord
    from discord.ext import commands
    import requests
except:
    import os
    os.system("pip install discord.py-self")
    os.system("pip install requests")
    import discord
    from discord.ext import commands
    import requests
import asyncio
import random
import json

bot =commands.Bot(
    command_prefix="!",
    self_bot=True
)


with open("config.json") as f:
    config = json.load(f)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

async def ai(history,username, message):
    prompt = f"Message History For Context : {history}\nPrompt Author {username} Original Prompt {message}"
    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.post(
                "http://162.243.165.237:3000//api/completions",
                json={
                    "prompt": prompt
                }
            ).json()
        )
        
        return response.get("response","Oh Shit. Not Good.")
    
    except Exception as e:
        return f"Error: {str(e)} 🔥🚨😭"

async def is_reply(msg: discord.Message):
    if msg.reference:
        try:
            ref_msg = await msg.channel.fetch_message(msg.reference.message_id)
            return ref_msg.author == bot.user
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return False
    return False

@bot.event
async def on_message(msg: discord.Message):
    if (
        msg.channel.id in config.get("channel_ids") and
        msg.author != bot.user and
        not msg.author.bot and
        (bot.user in msg.mentions or await is_reply(msg))
    ):
        async with msg.channel.typing():
            channel_history = []
            async for user_msg in msg.channel.history(limit=7):
                if user_msg.author != bot.user:
                    channel_history.append({
                        "username": user_msg.author.display_name,
                        "message": f"{user_msg.content[:200]}........" if len(user_msg.content) > 200 else user_msg.content
                    })
            response = await ai(channel_history,msg.author.display_name, msg.content)

            funny_reactions = ["😂", "🤣", "😭", "💀", "👏","🤡","🤗"]
            await msg.add_reaction(random.choice(funny_reactions))
            
            await msg.reply(
                content=f"{msg.author.mention}\n[Ai From Mars] : {response}"
            )
bot.run(config.get("usertoken"))
