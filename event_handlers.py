"""Event handlers for Discord bot events"""
import discord
from constants import (
    RM2_SERVER_ID, 
    DEV_SERVER_ID, 
    ALERTS_SETUP_CHANNEL_NAME, 
    ROLE_CONFIGS,
    ALERTS_CHANNEL_NAME,
    FSWAR_ROLE_NAME,
    HQWAR_ROLE_NAME,
    PVP_TOURNAMENT_ROLE_NAME,
    UNI_ROLE_NAME,
    BD_ROLE_NAME,
    BSIM_ROLE_NAME,
    FV_ROLE_NAME,
    MI_ROLE_NAME,
    PVP_BATTLE_ROLE_NAME,
    RM2_SERVER_CHANNEL_ID_GLOBAL,
    RM2_GLOBAL_SHOUT_USER_ID,
    OUTLAW_ROLE_NAME
)
from channel_manager import setup_guild_infrastructure
from special_events import handle_friendly_hallowvern
from admin_commands import handle_dm_commands
from utils import get_role_mention


async def handle_ready(bot, environment):
    """Handle when the bot is ready and connected"""
    print(f"ENVIRONMENT: {environment}")
    
    # only setup on my test server in development
    if environment == "dev":
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
    elif environment == "prod":
        for guild in bot.guilds:
            if guild.id == RM2_SERVER_ID:
                print(f"Skipping setup infrastructure for {guild.name} because it's the rm2 server")
                continue
            print(f"Setting up infrastructure for {guild.name}")
            success = await setup_guild_infrastructure(guild)
            if success:
                print(f"Successfully set up infrastructure for {guild.name}")
            else:
                print(f"Failed to set up infrastructure for {guild.name}")
    
    print(f"{bot.user.name} is here to defeat the Sun!")


async def handle_guild_join(guild):
    """Handle when the bot joins a new guild"""
    try:
        print(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Skip setup for rm2 server
        if guild.id == RM2_SERVER_ID:
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


async def handle_raw_reaction_add(bot, payload):
    """Handle when a reaction is added to a message"""
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
                
                # Map emojis to role names
                emoji_to_role = {emoji: role_name for role_name, _, _, emoji in ROLE_CONFIGS}
                # map emojis to readable names
                emoji_to_readable_name = {emoji: reason for _, reason, _, emoji in ROLE_CONFIGS}
                
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
        print(f"Error in handle_raw_reaction_add: {e}")


async def handle_raw_reaction_remove(bot, payload):
    """Handle when a reaction is removed from a message"""
    try:
        if payload.channel_id:
            channel = bot.get_channel(payload.channel_id)
            # Check if the reaction is in a rm2-alerts-setup channel
            if channel and channel.name == ALERTS_SETUP_CHANNEL_NAME:
                guild = bot.get_guild(payload.guild_id)
                user = guild.get_member(payload.user_id)
                
                # Map emojis to role names
                emoji_to_role = {emoji: role_name for role_name, _, _, emoji in ROLE_CONFIGS}
                # map emojis to readable names
                emoji_to_readable_name = {emoji: reason for _, reason, _, emoji in ROLE_CONFIGS}
                
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
        print(f"Error in handle_raw_reaction_remove: {e}")


async def handle_foodshop_war(message, guild, alert_channel):
    """Send Food Shop War alerts to the provided channel when applicable."""
    content = message.content.lower()
    announcements = {
        "**food shop war is starting in 15 minutes in street 2!**": "Food Shop War (street 2) starts in 15 minutes!",
        "**food shop war is starting in 15 minutes in signus ax-1!**": "Food Shop War (Signus AX-1) starts in 15 minutes!",
        "**food shop war is starting in 15 minutes in downtown 4!**": "Food Shop War (Downtown 4) starts in 15 minutes!",
    }

    announcement = announcements.get(content)
    if not announcement:
        return

    role_mention = get_role_mention(guild, FSWAR_ROLE_NAME)
    await alert_channel.send(f"{role_mention} {announcement}")


async def handle_hq_war(message, guild, alert_channel):
    """Send HQ War alerts when applicable."""
    if message.content.lower() != "**hq war starting in 5 minutes!**":
        return

    role_mention = get_role_mention(guild, HQWAR_ROLE_NAME)
    await alert_channel.send(f"{role_mention} HQ War starts in 5 minutes!")


async def handle_pvp_tournament(message, guild, alert_channel):
    """Send PvP Tournament alerts when applicable."""
    if (
        message.content.lower()
        != "**pvp tournament starts in 20 minutes, please opt in in the special battle arena!**"
    ):
        return

    role_mention = get_role_mention(guild, PVP_TOURNAMENT_ROLE_NAME)
    await alert_channel.send(
        f"{role_mention} PvP Tournament starts in 20 minutes!  Opt in!"
    )


async def handle_uni_events(message, guild, alert_channel):
    """Send Uni event alerts when applicable."""
    content = message.content.lower()
    announcements = {
        "**sky skirmish complete, join the uni raid within 5 minutes (solo or as a group)!**": "Uni open for 5 minutes",
        "**sky dungeon skirmish complete, join the uni sky dungeon raid within 5 minutes (solo or as a group)!**": "Uni Dungeon open for 5 minutes",
    }

    announcement = announcements.get(content)
    if not announcement:
        return

    role_mention = get_role_mention(guild, UNI_ROLE_NAME)
    await alert_channel.send(f"{role_mention} {announcement}")


async def handle_battle_dimension(message, guild, alert_channel):
    """Send Battle Dimension alerts when applicable."""
    if message.content.lower() != "**battle dimension starts in 30 minutes**":
        return

    role_mention = get_role_mention(guild, BD_ROLE_NAME)
    await alert_channel.send(f"{role_mention} Battle Dimension opens in 30 minutes")


async def handle_battle_simulation(message, guild, alert_channel):
    """Send Battle Simulation alerts when applicable."""
    if message.content.lower() != "**battle simulation opens in 5 minutes!**":
        return

    role_mention = get_role_mention(guild, BSIM_ROLE_NAME)
    await alert_channel.send(f"{role_mention} Battle Simulation opens in 5 minutes!")


async def handle_battle_match(message, guild, alert_channel):
    """Send Battle Match alerts when applicable."""
    if message.content.lower() != "**battle match starts in 30 minutes!**":
        return

    role_mention = get_role_mention(guild, BD_ROLE_NAME)
    await alert_channel.send(f"{role_mention} Battle Match starts in 30 minutes!")


async def handle_freedom_village(message, guild, alert_channel):
    """Send Freedom Village alerts when applicable."""
    if (
        message.content.lower()
        != "**sky city is launching an attack on freedom village in 30 minutes!**"
    ):
        return

    role_mention = get_role_mention(guild, FV_ROLE_NAME)
    await alert_channel.send(f"{role_mention} Freedom Village in 30 minutes!")


async def handle_monster_invasion(message, guild, alert_channel):
    """Send Monster Invasion alerts when applicable."""
    if message.content.lower() != "**monster invasion starts in 30 minutes!**":
        return

    role_mention = get_role_mention(guild, MI_ROLE_NAME)
    await alert_channel.send(f"{role_mention} Monster Invasion starts in 30 minutes!")


async def handle_open_pvp_battle(message, guild, alert_channel):
    """Send Open PvP Battle alerts, including the map, when applicable."""
    if not message.content.lower().startswith("**open pvp battle starts in 30 minutes in"):
        return

    try:
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


async def handle_outlaw(message, guild, alert_channel):
    """Send alerts for outlaw notifications when applicable."""
    if not message.content.lower().startswith("**player "):
        return

    try:
        words = message.content.split()
        if len(words) >= 6 and words[2:6] == ["became", "an", "outlaw", "at"]:
            player_name = words[1]
            map = " ".join(words[6:]).replace("!**", "")
            role_mention = get_role_mention(guild, OUTLAW_ROLE_NAME)
            await alert_channel.send(f"{role_mention} {player_name} became an outlaw at {map}!")
        else:
            print(f"Could not parse player name or map from message: {message.content}")
    except Exception as e:
        print(f"Error parsing outlaw message: {e}")


async def handle_message(bot, message, admin_id):
    """Handle incoming messages and send alerts to rm2-alerts channels"""
    if message.author == bot.user:
        return
    
    # Handle DM commands
    if isinstance(message.channel, discord.DMChannel):
        await handle_dm_commands(message, bot, admin_id)
        return
    
    if message.author.id == RM2_GLOBAL_SHOUT_USER_ID and message.channel.id == RM2_SERVER_CHANNEL_ID_GLOBAL:
        for guild in bot.guilds:
            if guild.id == RM2_SERVER_ID:
                continue
            alert_channel = discord.utils.get(guild.channels, name=ALERTS_CHANNEL_NAME)
            if alert_channel:
                try:
                    await handle_foodshop_war(message, guild, alert_channel)
                    await handle_hq_war(message, guild, alert_channel)
                    await handle_pvp_tournament(message, guild, alert_channel)
                    await handle_uni_events(message, guild, alert_channel)
                    await handle_battle_dimension(message, guild, alert_channel)
                    await handle_battle_match(message, guild, alert_channel)
                    await handle_battle_simulation(message, guild, alert_channel)
                    await handle_freedom_village(message, guild, alert_channel)
                    await handle_monster_invasion(message, guild, alert_channel)
                    await handle_open_pvp_battle(message, guild, alert_channel)
                    await handle_outlaw(message, guild, alert_channel)

                    # friendly hallowvern appeared
                    await handle_friendly_hallowvern(message, guild, alert_channel)




                except discord.Forbidden:
                    print(f"Bot doesn't have permission to send messages in {guild.name}'s alerts channel")
                except Exception as e:
                    print(f"Error sending alert to {guild.name}: {e}")
            else:
                print(f"Could not find 'rm2-alerts' channel in guild: {guild.name}")

    await bot.process_commands(message)
