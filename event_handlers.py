"""Event handlers for Discord bot events"""
import discord
from constants import RM2_SERVER_ID, DEV_SERVER_ID
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

