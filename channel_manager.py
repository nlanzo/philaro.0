import discord
from constants import *


# create the setup channel in the guild if it doesn't exist
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
                topic="React to the message to subscribe to rm2 alerts on this server",
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


# create the alerts channel in the guild if it doesn't exist
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
                topic="Alerts for Wars/BD/BSIM/Uni/FV/MI",
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


# create all the specific alert roles in the guild if they don't exist
async def ensure_all_alert_roles(guild):
    """Ensure all rm2-alerts roles exist in the guild"""
    roles = {}
        
    for role_name, reason, color, _ in ROLE_CONFIGS:
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            try:
                role = await guild.create_role(
                    name=role_name,
                    color=color,
                    reason=f"Auto-created for {reason}"
                )
                print(f"Created {role_name} role in {guild.name}")
            except discord.Forbidden:
                print(f"Bot doesn't have permission to create roles in {guild.name}")
                return {}
            except Exception as e:
                print(f"Error creating role {role_name} in {guild.name}: {e}")
                return {}
        roles[role_name] = role
    
    return roles



EXPECTED_REACTIONS = [emoji for _, _, _, emoji in ROLE_CONFIGS]

async def create_setup_message(setup_channel):
    setup_message_content = "React to subscribe/unsubscribe to different rm2 alerts:\n" + "\n".join([f"{emoji} - {reason}" for _, reason, _, emoji in ROLE_CONFIGS])
    async for message in setup_channel.history(limit=50):
        if message.author == setup_channel.guild.me and "React to subscribe/unsubscribe to different rm2 alerts" in message.content:
            # Update content if needed
            if message.content != setup_message_content:
                message = await message.edit(content=setup_message_content)
            # Add missing reactions
            current_reactions = [str(reaction.emoji) for reaction in message.reactions]
            for emoji in EXPECTED_REACTIONS:
                if emoji not in current_reactions:
                    await message.add_reaction(emoji)
            return message  # Return the found/updated message

    # If no setup message found, create a new one
    message = await setup_channel.send(setup_message_content)
    for emoji in EXPECTED_REACTIONS:
        await message.add_reaction(emoji)
    return message


# set up all required channels and roles for a guild
async def setup_guild_infrastructure(guild):
    """Set up all required channels and roles for a guild"""
    # Ensure setup channel exists
    setup_channel = await ensure_setup_channel(guild)
    if not setup_channel:
        return False
    
    # Ensure all alert roles exist
    alert_roles = await ensure_all_alert_roles(guild)
    if not alert_roles:
        return False
    
    # Ensure alerts channel exists
    alerts_channel = await ensure_alerts_channel(guild)
    if not alerts_channel:
        return False
    
    # Create setup message
    await create_setup_message(setup_channel)
    
    return True
