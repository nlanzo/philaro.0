import discord
from constants import *

async def ensure_setup_channel(guild):
    """Ensure the rm2-alerts-setup channel exists in the guild"""
    setup_channel = discord.utils.get(guild.channels, name=ALERTS_SETUP_CHANNEL_NAME)
    if not setup_channel:
        try:
            # Create channel with specific permissions
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    send_messages=False,  # Everyone can't send messages
                    read_messages=True,   # Everyone can read messages
                    add_reactions=True    # Everyone can react
                ),
                guild.me: discord.PermissionOverwrite(
                    send_messages=True,   # Bot can send messages
                    read_messages=True,   # Bot can read messages
                    add_reactions=True,   # Bot can add reactions
                    manage_channels=True  # Bot can manage the channel
                )
            }
            
            setup_channel = await guild.create_text_channel(
                name=ALERTS_SETUP_CHANNEL_NAME,
                topic="Click the bell 🔔 to subscribe to rm2 alerts on this server",
                reason="Auto-created for rm2 alerts setup",
                overwrites=overwrites
            )
            print(f"Created {ALERTS_SETUP_CHANNEL_NAME} channel in {guild.name}")
            return setup_channel
        except discord.Forbidden:
            print(f"Bot doesn't have permission to create channels in {guild.name}")
            return None
        except Exception as e:
            print(f"Error creating channel in {guild.name}: {e}")
            return None
    return setup_channel

async def ensure_alerts_channel(guild):
    """Ensure the rm2-alerts channel exists in the guild"""
    alerts_channel = discord.utils.get(guild.channels, name=ALERTS_CHANNEL_NAME)
    if not alerts_channel:
        try:
            # Create alerts channel with specific permissions
            alerts_overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    read_messages=True,   # Everyone can read alerts
                    send_messages=False   # Only bot can send alerts
                ),
                guild.me: discord.PermissionOverwrite(
                    send_messages=True,   # Bot can send alerts
                    read_messages=True,   # Bot can read messages
                    manage_channels=True  # Bot can manage the channel
                )
            }
            
            alerts_channel = await guild.create_text_channel(
                name=ALERTS_CHANNEL_NAME,
                topic="Alerts for Wars/BD/BSIM/Uni/FV",
                reason="Auto-created for rm2 alerts",
                overwrites=alerts_overwrites
            )
            print(f"Created {ALERTS_CHANNEL_NAME} channel in {guild.name}")
            return alerts_channel
        except discord.Forbidden:
            print(f"Bot doesn't have permission to create channels in {guild.name}")
            return None
        except Exception as e:
            print(f"Error creating alerts channel in {guild.name}: {e}")
            return None
    return alerts_channel

async def ensure_alerts_role(guild):
    """Ensure the rm2-alerts role exists in the guild"""
    alerts_role = discord.utils.get(guild.roles, name=ALERTS_ROLE_NAME)
    if not alerts_role:
        try:
            alerts_role = await guild.create_role(
                name=ALERTS_ROLE_NAME,
                color=discord.Color.red(),
                reason="Auto-created for rm2 alerts system"
            )
            print(f"Created {ALERTS_ROLE_NAME} role in {guild.name}")
            return alerts_role
        except discord.Forbidden:
            print(f"Bot doesn't have permission to create roles in {guild.name}")
            return None
        except Exception as e:
            print(f"Error creating role in {guild.name}: {e}")
            return None
    return alerts_role

async def create_setup_message(setup_channel):
    """Create the role assignment message in the setup channel"""
    # Check if there's already a role assignment message
    async for message in setup_channel.history(limit=50):
        if message.author == setup_channel.guild.me and "React to this message to subscribe to rm2 alerts on this server" in message.content:
            # Message already exists, add reaction if not present
            if not message.reactions:
                await message.add_reaction("🔔")
            return message
    
    # No existing message found, create a new one
    role_message = await setup_channel.send("React to this message to subscribe to rm2 alerts on this server")
    await role_message.add_reaction("🔔")
    return role_message

async def setup_guild_infrastructure(guild):
    """Set up all required channels and roles for a guild"""
    # Ensure setup channel exists
    setup_channel = await ensure_setup_channel(guild)
    if not setup_channel:
        return False
    
    # Ensure alerts role exists
    alerts_role = await ensure_alerts_role(guild)
    if not alerts_role:
        return False
    
    # Ensure alerts channel exists
    alerts_channel = await ensure_alerts_channel(guild)
    if not alerts_channel:
        return False
    
    # Create setup message
    await create_setup_message(setup_channel)
    
    return True

async def setup_guild_for_user(guild, user):
    """Set up guild infrastructure when a user tries to subscribe"""
    # Ensure alerts role exists
    alerts_role = await ensure_alerts_role(guild)
    if not alerts_role:
        await user.send(f"Sorry, I don't have permission to create the {ALERTS_ROLE_NAME} role in {guild.name}. Please ask an administrator to create it.")
        return None
    
    # Ensure alerts channel exists
    alerts_channel = await ensure_alerts_channel(guild)
    if not alerts_channel:
        await user.send(f"Sorry, I don't have permission to create the {ALERTS_CHANNEL_NAME} channel in {guild.name}. Please ask an administrator to create it.")
        return None
    
    return alerts_role 