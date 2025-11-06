import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from event_handlers import handle_guild_join, handle_ready, handle_raw_reaction_add, handle_raw_reaction_remove, handle_message


load_dotenv()
token = os.getenv("DISCORD_TOKEN")
admin_id = int(os.getenv("ADMIN_USER_ID"))
ENVIRONMENT = os.getenv("ENVIRONMENT")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():  
    await handle_ready(bot, ENVIRONMENT)


@bot.event
async def on_guild_join(guild):
    await handle_guild_join(guild)


@bot.event
async def on_raw_reaction_add(payload):
    await handle_raw_reaction_add(bot, payload)


@bot.event
async def on_raw_reaction_remove(payload):
    await handle_raw_reaction_remove(bot, payload)


@bot.event
async def on_message(message):
    await handle_message(bot, message, admin_id)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
