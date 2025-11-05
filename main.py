import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from constants import *
from special_events import handle_friendly_hallowvern
from admin_commands import handle_dm_commands
from event_handlers import handle_guild_join, handle_ready, handle_raw_reaction_add, handle_raw_reaction_remove
from utils import get_role_mention


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


rm2_discord_server_id = RM2_SERVER_ID
rm2_general_chat_id = RM2_SERVER_CHANNEL_ID_GLOBAL
rm2_global_shout_user_id = RM2_GLOBAL_SHOUT_USER_ID


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

# send alerts to the "rm2-alerts" channel in all guilds where bot is installed
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Handle DM commands
    if isinstance(message.channel, discord.DMChannel):
        await handle_dm_commands(message, bot, admin_id)
        return
    
    if message.author.id == rm2_global_shout_user_id and message.channel.id == rm2_general_chat_id:
        for guild in bot.guilds:
            if guild.id == rm2_discord_server_id:
                continue
            alert_channel = discord.utils.get(guild.channels, name=ALERTS_CHANNEL_NAME)
            if alert_channel:
                try:
                    # Food Shop War events - use rm2-alerts-fswar role
                    if "**food shop war is starting in 15 minutes in street 2!**" == message.content.lower():
                        role_mention = get_role_mention(guild, FSWAR_ROLE_NAME)
                        await alert_channel.send(f"{role_mention} Food Shop War (street 2) starts in 15 minutes!")

                    if "**food shop war is starting in 15 minutes in signus ax-1!**" == message.content.lower():
                        role_mention = get_role_mention(guild, FSWAR_ROLE_NAME)
                        await alert_channel.send(f"{role_mention} Food Shop War (Signus AX-1) starts in 15 minutes!")

                    if "**food shop war is starting in 15 minutes in downtown 4!**" == message.content.lower():
                        role_mention = get_role_mention(guild, FSWAR_ROLE_NAME)
                        await alert_channel.send(f"{role_mention} Food Shop War (Downtown 4) starts in 15 minutes!")
                    
                    # HQ War events - use rm2-alerts-hqwar role
                    if "**hq war starting in 5 minutes!**" == message.content.lower():
                        role_mention = get_role_mention(guild, HQWAR_ROLE_NAME)
                        await alert_channel.send(f"{role_mention} HQ War starts in 5 minutes!")

                    # PVP tournament - use rm2-alerts-pvpt role
                    if "**pvp tournament starts in 20 minutes, please opt in in the special battle arena!**" == message.content.lower():
                        role_mention = get_role_mention(guild, PVP_TOURNAMENT_ROLE_NAME)
                        await alert_channel.send(f"{role_mention} PvP Tournament starts in 30 minutes!  Opt in!")

                    # Uni events - use rm2-alerts-uni role
                    if "**sky skirmish complete, join the uni raid within 5 minutes (solo or as a group)!**" == message.content.lower():
                        role_mention = get_role_mention(guild, UNI_ROLE_NAME)
                        await alert_channel.send(f"{role_mention} Uni open for 5 minutes")

                    if "**sky dungeon skirmish complete, join the uni sky dungeon raid within 5 minutes (solo or as a group)!**" == message.content.lower():
                        role_mention = get_role_mention(guild, UNI_ROLE_NAME)
                        await alert_channel.send(f"{role_mention} Uni Dungeon open for 5 minutes")

                    # Battle Dimension events - use rm2-alerts-bd role
                    if "**battle dimension starts in 30 minutes**" == message.content.lower():
                        role_mention = get_role_mention(guild, BD_ROLE_NAME)
                        await alert_channel.send(f"{role_mention} Battle Dimension opens in 30 minutes")

                    # Battle Simulation events - use rm2-alerts-bsim role
                    if "**battle simulation opens in 5 minutes!**" == message.content.lower():
                        role_mention = get_role_mention(guild, BSIM_ROLE_NAME)
                        await alert_channel.send(f"{role_mention} Battle Simulation opens in 5 minutes!")

                    # Freedom Village events - use rm2-alerts-fv role
                    if "**sky city is launching an attack on freedom village in 30 minutes!**" == message.content.lower():
                        role_mention = get_role_mention(guild, FV_ROLE_NAME)
                        await alert_channel.send(f"{role_mention} Freedom Village in 30 minutes!")

                    # Monster Invasion events - use rm2-alerts-mi role
                    if "**monster invasion starts in 30 minutes!**" == message.content.lower():
                        role_mention = get_role_mention(guild, MI_ROLE_NAME)
                        await alert_channel.send(f"{role_mention} Monster Invasion starts in 30 minutes!")

                    if message.content.lower().startswith("**open pvp battle starts in 30 minutes in"):
                        try:
                            # More robust map parsing
                            words = message.content.split()
                            # Find the index of the second "in" and extract everything after it until the trailing "!**"
                            in_index = -1
                            in_count = 0
                            for i, word in enumerate(words):
                                if word.lower() == "in":
                                    in_index = i
                                    in_count += 1
                                    if in_count == 2:
                                        break
                            
                            if in_index != -1 and in_index + 1 < len(words):
                                map_words = words[in_index + 1:]
                                map = " ".join(map_words).replace("!**", "")  # Exclude the trailing "!**"
                                role_mention = get_role_mention(guild, PVP_BATTLE_ROLE_NAME)
                                await alert_channel.send(f"{role_mention} Open PvP Battle starts in 30 minutes in {map}!")
                            else:
                                print(f"Could not parse map from message: {message.content}")
                        except Exception as e:
                            print(f"Error parsing open PvP battle map: {e}")

                    # friendly hallowvern appeared
                    await handle_friendly_hallowvern(message, guild, alert_channel)

                except discord.Forbidden:
                    print(f"Bot doesn't have permission to send messages in {guild.name}'s alerts channel")
                except Exception as e:
                    print(f"Error sending alert to {guild.name}: {e}")
            else:
                print(f"Could not find 'rm2-alerts' channel in guild: {guild.name}")

    await bot.process_commands(message)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
