import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from constants import *
from channel_manager import setup_guild_infrastructure
from special_events import handle_friendly_hallowvern


load_dotenv()
token = os.getenv("DISCORD_TOKEN")
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
    print(f"ENVIRONMENT: {ENVIRONMENT}")
        # only setup on my test server in development
    if ENVIRONMENT == "dev":
        print("DEV: getting guild")
        guild = bot.get_guild(DEV_SERVER_ID)
        print(f"DEV: guild: {guild.name}")
        print(f"Setting up infrastructure for {guild.name}")
        success = await setup_guild_infrastructure(guild)
        if success:
            print(f"DEV: Successfully set up infrastructure for {guild.name}")
        else:
            print(f"DEV: Failed to set up infrastructure for {guild.name}")
    # setup on all guilds in production
    elif ENVIRONMENT == "prod":
        for guild in bot.guilds:
            if guild.id == rm2_discord_server_id:
                print(f"Skipping setup infrastructure for {guild.name} because it's the rm2 server")
                continue
            print(f"Setting up infrastructure for {guild.name}")
            success = await setup_guild_infrastructure(guild)
            if success:
                print(f"Successfully set up infrastructure for {guild.name}")
            else:
                print(f"Failed to set up infrastructure for {guild.name}")
    print(f"{bot.user.name} is here to defeat the Sun!")


@bot.event
async def on_guild_join(guild):
    """Handle when the bot joins a new guild"""
    try:
        print(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Skip setup for rm2 server
        if guild.id == rm2_discord_server_id:
            print(f"Skipping setup infrastructure for {guild.name} because it's the rm2 server")
            return
        
        # Set up infrastructure for the new guild
        print(f"Setting up infrastructure for new guild: {guild.name}")
        success = await setup_guild_infrastructure(guild)
        
        if success:
            print(f"Successfully set up infrastructure for {guild.name}")
        else:
            print(f"Failed to set up infrastructure for {guild.name}. The bot may need additional permissions.")
    except Exception as e:
        print(f"Error setting up infrastructure for new guild {guild.name}: {e}")



# Map emojis to role names
emoji_to_role = {emoji: role_name for role_name, _, _, emoji in ROLE_CONFIGS}
# map emojis to readable names
emoji_to_readable_name = {emoji: reason for _, reason, _, emoji in ROLE_CONFIGS}

def get_role_mention(guild, role_name):
    """Helper function to get role mention or fallback to @role_name"""
    role = discord.utils.get(guild.roles, name=role_name)
    return role.mention if role else f"@{role_name}"
    

# add the role to the user when the reaction is added
@bot.event
async def on_raw_reaction_add(payload):
    try:
        # Check if the reaction is in a rm2-alerts-setup channel
        if payload.channel_id:
            channel = bot.get_channel(payload.channel_id)
            if channel and channel.name == ALERTS_SETUP_CHANNEL_NAME:
                guild = bot.get_guild(payload.guild_id)
                user = guild.get_member(payload.user_id)
                
                # Don't assign role to the bot itself
                if user == bot.user:
                    return
                
                if payload.emoji.name in emoji_to_role:
                    role_name = emoji_to_role[payload.emoji.name]
                    role = discord.utils.get(guild.roles, name=role_name)
                    
                    if not role:
                        await user.send(f"Sorry, the {role_name} role doesn't exist in {guild.name}. Please ask an administrator to create it.")
                        return
                    
                    # Check if bot has Manage Roles permission
                    if not guild.me.guild_permissions.manage_roles:
                        await user.send(f"Sorry, I don't have the 'Manage Roles' permission in {guild.name}. Please ask an administrator to give me this permission.")
                        return
                    
                    # Check if bot can assign this specific role (role hierarchy)
                    if role.position >= guild.me.top_role.position:
                        await user.send(f"Sorry, I can't assign the {role_name} role in {guild.name} because it's higher than my role. Please ask an administrator to move my role higher in the role list.")
                        return
                    
                    try:
                        await user.add_roles(role)
                        await user.send(f"You have subscribed to {emoji_to_readable_name[payload.emoji.name]} alerts in {guild.name}!")
                    except discord.Forbidden as e:
                        await user.send(f"Sorry, I don't have permission to assign the {role_name} role in {guild.name}. Please ask an administrator to give me the 'Manage Roles' permission.")
                    except Exception as e:
                        await user.send(f"Sorry, there was an error assigning the role in {guild.name}. Please try again later.")
                        print(f"Error assigning role in {guild.name}: {e}")
    except Exception as e:
        print(f"Error in on_raw_reaction_add: {e}")

# remove the role from the user when the reaction is removed
@bot.event
async def on_raw_reaction_remove(payload):
    try:
        if payload.channel_id:
            channel = bot.get_channel(payload.channel_id)
            # Check if the reaction is in a rm2-alerts-setup channel
            if channel and channel.name == ALERTS_SETUP_CHANNEL_NAME:
                guild = bot.get_guild(payload.guild_id)
                user = guild.get_member(payload.user_id)
                
                if payload.emoji.name in emoji_to_role:
                    role_name = emoji_to_role[payload.emoji.name]
                    role = discord.utils.get(guild.roles, name=role_name)
                    
                    if role:
                        try:
                            await user.remove_roles(role)
                            await user.send(f"You have unsubscribed from {emoji_to_readable_name[payload.emoji.name]} alerts in {guild.name}!")
                        except discord.Forbidden:
                            await user.send(f"Sorry, I don't have permission to remove the {role_name} role in {guild.name}. Please ask an administrator to give me the 'Manage Roles' permission.")
                        except Exception as e:
                            await user.send(f"Sorry, there was an error removing the role in {guild.name}. Please try again later.")
                            print(f"Error removing role in {guild.name}: {e}")
                    else:
                        await user.send(f"The {role_name} role doesn't exist in {guild.name}.")
    except Exception as e:
        print(f"Error in on_raw_reaction_remove: {e}")

# send alerts to the "rm2-alerts" channel in all guilds where bot is installed
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Handle DM commands
    if isinstance(message.channel, discord.DMChannel):
        if message.content.lower() in ['!servers', '!serverlist', '!guilds']:
            try:
                if not bot.guilds:
                    await message.channel.send("I'm not in any servers right now.")
                    return
                
                server_list = []
                for guild in bot.guilds:
                    # Get member count
                    member_count = guild.member_count if guild.member_count else len(guild.members)
                    server_list.append(f"**{guild.name}** (ID: {guild.id})\n   Members: {member_count}\n   Owner: {guild.owner.name if guild.owner else 'Unknown'}")
                
                # Split into chunks if too long (Discord has a 2000 character limit)
                response = f"I'm currently in {len(bot.guilds)} server(s):\n\n" + "\n\n".join(server_list)
                
                if len(response) > 2000:
                    # Split into multiple messages
                    chunks = []
                    current_chunk = f"I'm currently in {len(bot.guilds)} server(s):\n\n"
                    
                    for server_info in server_list:
                        if len(current_chunk + server_info + "\n\n") > 1900:  # Leave some buffer
                            chunks.append(current_chunk)
                            current_chunk = server_info + "\n\n"
                        else:
                            current_chunk += server_info + "\n\n"
                    
                    if current_chunk:
                        chunks.append(current_chunk)
                    
                    for i, chunk in enumerate(chunks):
                        if i == 0:
                            await message.channel.send(chunk)
                        else:
                            await message.channel.send(f"**Continued...**\n\n{chunk}")
                else:
                    await message.channel.send(response)
                    
            except Exception as e:
                await message.channel.send(f"Sorry, there was an error getting the server list: {e}")
                print(f"Error in server list command: {e}")
        else:
            # For other DMs, just acknowledge
            await message.channel.send("Hi! I'm here to defeat the Sun!")
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
                    await handle_friendly_hallowvern(message, guild, alert_channel, get_role_mention)

                except discord.Forbidden:
                    print(f"Bot doesn't have permission to send messages in {guild.name}'s alerts channel")
                except Exception as e:
                    print(f"Error sending alert to {guild.name}: {e}")
            else:
                print(f"Could not find 'rm2-alerts' channel in guild: {guild.name}")

    await bot.process_commands(message)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
