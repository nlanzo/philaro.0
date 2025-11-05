"""Event handlers for Discord bot events"""
import discord
from constants import RM2_SERVER_ID, DEV_SERVER_ID, ALERTS_SETUP_CHANNEL_NAME, ROLE_CONFIGS
from channel_manager import setup_guild_infrastructure


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

