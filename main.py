import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from constants import *
from channel_manager import setup_guild_infrastructure, setup_guild_for_user


load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# change these to the rm2 ids in production
rm2_discord_server_id = RM2_SERVER_ID
rm2_general_chat_id = RM2_SERVER_CHANNEL_ID_GLOBAL
rm2_global_shout_user_id = RM2_GLOBAL_SHOUT_USER_ID


@bot.event
async def on_ready():  
    # Set up infrastructure for all guilds (not on rm2 server)
    for guild in bot.guilds:
        print(f"Setting up infrastructure for {guild.name}")
        if guild.id == rm2_discord_server_id:
            print(f"Skipping setup infrastructure for {guild.name} because it's the rm2 server")
            print("Channels I see in rm2 discord server:")
            for channel in guild.channels:
                print(f"Channel: {channel.name}")
            continue
        await setup_guild_infrastructure(guild)
    print(f"{bot.user.name} is here to defeat the Sun!")

# add the role to the user when the reaction is added
@bot.event
async def on_raw_reaction_add(payload):
    # Check if the reaction is in a rm2-alerts-setup channel
    if payload.channel_id:
        channel = bot.get_channel(payload.channel_id)
        if channel and channel.name == ALERTS_SETUP_CHANNEL_NAME:
            # Check if it's the bell emoji
            if payload.emoji.name == "🔔":
                guild = bot.get_guild(payload.guild_id)
                user = guild.get_member(payload.user_id)
                
                # Don't assign role to the bot itself
                if user == bot.user:
                    return
                
                # Set up guild infrastructure and get the role
                alerts_role = await setup_guild_for_user(guild, user)
                if not alerts_role:
                    return
                
                try:
                    await user.add_roles(alerts_role)
                    await user.send(f"You have been subscribed to rm2 alerts in {guild.name}!")
                except discord.Forbidden:
                    await user.send(f"Sorry, I don't have permission to assign the {ALERTS_ROLE_NAME} role in {guild.name}. Please ask an administrator to give me the 'Manage Roles' permission.")
                except Exception as e:
                    await user.send(f"Sorry, there was an error assigning the role in {guild.name}. Please try again later.")
                    print(f"Error assigning role in {guild.name}: {e}")

# remove the role from the user when the reaction is removed
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.channel_id:
        channel = bot.get_channel(payload.channel_id)
        # Check if the reaction is in a rm2-alerts-setup channel
        if channel and channel.name == ALERTS_SETUP_CHANNEL_NAME:
            # Check if it's the bell emoji
            if payload.emoji.name == "🔔":
                guild = bot.get_guild(payload.guild_id)
                user = guild.get_member(payload.user_id)
                
                # Get the rm2-alerts role
                alerts_role = discord.utils.get(guild.roles, name=ALERTS_ROLE_NAME)
                if alerts_role:
                    try:
                        await user.remove_roles(alerts_role)
                        await user.send(f"You have been unsubscribed from rm2 alerts in {guild.name}!")
                    except discord.Forbidden:
                        await user.send(f"Sorry, I don't have permission to remove the {ALERTS_ROLE_NAME} role in {guild.name}. Please ask an administrator to give me the 'Manage Roles' permission.")
                    except Exception as e:
                        await user.send(f"Sorry, there was an error removing the role in {guild.name}. Please try again later.")
                        print(f"Error removing role in {guild.name}: {e}")
                else:
                    await user.send(f"The {ALERTS_ROLE_NAME} role doesn't exist in {guild.name}.")

# send alerts to the "rm2-alerts" channel in all guilds where bot is installed
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.id == rm2_global_shout_user_id and message.channel.id == rm2_general_chat_id:
        # DEBUG
        print(f"Message content from rm2 global shout: {message.content.lower()}")
        for guild in bot.guilds:
            if guild.id == rm2_discord_server_id:
                continue
            alert_channel = discord.utils.get(guild.channels, name=ALERTS_CHANNEL_NAME)
            if alert_channel:
                # Get the rm2-alerts role for this guild
                alerts_role = discord.utils.get(guild.roles, name=ALERTS_ROLE_NAME)
                role_mention = alerts_role.mention if alerts_role else "@rm2-alerts"
                
                if "**food shop war is starting in 15 minutes in street 2!**" == message.content.lower():
                    await alert_channel.send(f"{role_mention} Food Shop War (street 2) starts in 15 minutes!")

                if "**food shop war is starting in 15 minutes in signus ax-1!**" == message.content.lower():
                    await alert_channel.send(f"{role_mention} Food Shop War (Signus AX-1) starts in 15 minutes!")

                if "**food shop war is starting in 15 minutes in downtown 4!**" == message.content.lower():
                    await alert_channel.send(f"{role_mention} Food Shop War (Downtown 4) starts in 15 minutes!")

                if "**hq war starting in 5 minutes!**" == message.content.lower():
                    await alert_channel.send(f"{role_mention} HQ War starts in 5 minutes!")

                if "**sky skirmish complete, join the uni raid within 5 minutes (solo or as a group)!**" == message.content.lower():
                    await alert_channel.send(f"{role_mention} Uni open for 5 minutes")

                if "**sky dungeon skirmish complete, join the uni sky dungeon raid within 5 minutes (solo or as a group)!**" == message.content.lower():
                    await alert_channel.send(f"{role_mention} Uni Dungeon open for 5 minutes")

                if "**battle dimension starts in 30 minutes**" == message.content.lower():
                    await alert_channel.send(f"{role_mention} Battle Dimension opens in 30 minutes")

                if "**battle simulation opens in 5 minutes!**" == message.content.lower():
                    await alert_channel.send(f"{role_mention} Battle Simulation opens in 5 minutes!")

                if "**sky city is launching an attack on freedom village in 30 minutes!**" == message.content.lower():
                    await alert_channel.send(f"{role_mention} Freedom Village in 30 minutes!")

                if "**monster invasion starts in 10 minutes!**" == message.content.lower():
                    await alert_channel.send(f"{role_mention} Monster Invasion starts in 10 minutes!")
            else:
                print(f"Could not find 'rm2-alerts' channel in guild: {guild.name}")

    await bot.process_commands(message)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
