import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from constants import *


load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

origin_server_id = LANZ2_SERVER_ID


@bot.event
async def on_ready():
    print(f"{bot.user.name} is here to defeat the Sun!")
    
    # Create role assignment message in rm2-alerts-setup channels
    for guild in bot.guilds:
        if guild.id == origin_server_id:
            continue
        
        # Check if rm2-alerts-setup channel exists, create if it doesn't
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
            except discord.Forbidden:
                print(f"Bot doesn't have permission to create channels in {guild.name}")
                continue
            except Exception as e:
                print(f"Error creating channel in {guild.name}: {e}")
                continue
        
        # Ensure rm2-alerts role exists
        alerts_role = discord.utils.get(guild.roles, name=ALERTS_ROLE_NAME)
        if not alerts_role:
            try:
                alerts_role = await guild.create_role(
                    name=ALERTS_ROLE_NAME,
                    color=discord.Color.red(),
                    reason="Auto-created for rm2 alerts system"
                )
                print(f"Created {ALERTS_ROLE_NAME} role in {guild.name}")
            except discord.Forbidden:
                print(f"Bot doesn't have permission to create roles in {guild.name}")
            except Exception as e:
                print(f"Error creating role in {guild.name}: {e}")
        
        # Ensure rm2-alerts channel exists
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
            except discord.Forbidden:
                print(f"Bot doesn't have permission to create channels in {guild.name}")
            except Exception as e:
                print(f"Error creating alerts channel in {guild.name}: {e}")
        
        # Check if there's already a role assignment message
        async for message in setup_channel.history(limit=50):
            if message.author == bot.user and "React to this message to subscribe to rm2 alerts on this server" in message.content:
                # Message already exists, add reaction if not present
                if not message.reactions:
                    await message.add_reaction("🔔")
                break
        else:
            # No existing message found, create a new one
            role_message = await setup_channel.send("React to this message to subscribe to rm2 alerts on this server")
            await role_message.add_reaction("🔔")

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
                
                # Get or create the rm2-alerts role
                alerts_role = discord.utils.get(guild.roles, name=ALERTS_ROLE_NAME)
                if not alerts_role:
                    try:
                        alerts_role = await guild.create_role(
                            name=ALERTS_ROLE_NAME,
                            color=discord.Color.red(),
                            reason="Auto-created for rm2 alerts system"
                        )
                        print(f"Created {ALERTS_ROLE_NAME} role in {guild.name} for user {user.name}")
                    except discord.Forbidden:
                        await user.send(f"Sorry, I don't have permission to create the {ALERTS_ROLE_NAME} role in {guild.name}. Please ask an administrator to create it.")
                        return
                    except Exception as e:
                        await user.send(f"Sorry, there was an error creating the role in {guild.name}. Please try again later.")
                        print(f"Error creating role in {guild.name}: {e}")
                        return
                
                # Ensure rm2-alerts channel exists
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
                        print(f"Created {ALERTS_CHANNEL_NAME} channel in {guild.name} for user {user.name}")
                    except discord.Forbidden:
                        await user.send(f"Sorry, I don't have permission to create the {ALERTS_CHANNEL_NAME} channel in {guild.name}. Please ask an administrator to create it.")
                        return
                    except Exception as e:
                        await user.send(f"Sorry, there was an error creating the alerts channel in {guild.name}. Please try again later.")
                        print(f"Error creating alerts channel in {guild.name}: {e}")
                        return
                
                try:
                    await user.add_roles(alerts_role)
                    await user.send(f"You have been subscribed to rm2 alerts in {guild.name}!")
                except discord.Forbidden:
                    await user.send(f"Sorry, I don't have permission to assign the {ALERTS_ROLE_NAME} role in {guild.name}. Please ask an administrator to give me the 'Manage Roles' permission.")
                except Exception as e:
                    await user.send(f"Sorry, there was an error assigning the role in {guild.name}. Please try again later.")
                    print(f"Error assigning role in {guild.name}: {e}")

@bot.event
async def on_raw_reaction_remove(payload):
    # Check if the reaction is in a rm2-alerts-setup channel
    if payload.channel_id:
        channel = bot.get_channel(payload.channel_id)
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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.id == LANZ_USER_ID and message.channel.id == LANZ2_SERVER_CHANNEL_ID_GENERAL:
        # Send alerts to "rm2-alerts" channel in all guilds where bot is installed
        for guild in bot.guilds:
            alert_channel = discord.utils.get(guild.channels, name=ALERTS_CHANNEL_NAME)
            if alert_channel:
                # Get the rm2-alerts role for this guild
                alerts_role = discord.utils.get(guild.roles, name=ALERTS_ROLE_NAME)
                role_mention = alerts_role.mention if alerts_role else "@rm2-alerts"
                
                if "food shop war is starting in 15 minutes" in message.content.lower():
                    await alert_channel.send(f"{role_mention} Food Shop War starts in 15 minutes!")

                if "hq war starting in 5 minutes!" in message.content.lower():
                    await alert_channel.send(f"{role_mention} HQ War starts in 5 minutes!")

                if "sky skirmish complete, join the uni raid within 5 minutes" in message.content.lower():
                    await alert_channel.send(f"{role_mention} Uni open for 5 minutes")

                if "sky dungeon skirmish complete, join the uni sky dungeon raid within 5 minutes" in message.content.lower():
                    await alert_channel.send(f"{role_mention} Uni Dungeon open for 5 minutes")

                if "battle dimension starts in 30 minutes" in message.content.lower():
                    await alert_channel.send(f"{role_mention} Battle Dimension opens in 30 minutes")

                if "battle simulation opens in 5 minutes!" in message.content.lower():
                    await alert_channel.send(f"{role_mention} Battle Simulation opens in 5 minutes!")
            else:
                print(f"Could not find 'rm2-alerts' channel in guild: {guild.name}")

    await bot.process_commands(message)


# just trying things out

# @bot.event
# async def on_member_join(member):
#     await member.send(f"Welcome to the server, {member.name}")

# @bot.command()
# async def hello(ctx):
#     await ctx.send(f"Hello {ctx.author.mention}!")

# @bot.command()
# async def assign(ctx):
#     role = discord.utils.get(ctx.guild.roles, name=tester_role)
#     if role:
#         await ctx.author.add_roles(role)
#         await ctx.send(f"{ctx.author.mention} is now assigned to {tester_role}")
#     else:
#         await ctx.send("Role doesn't exist")

# @bot.command()
# async def remove(ctx):
#     role = discord.utils.get(ctx.guild.roles, name=tester_role)
#     if role:
#         await ctx.author.remove_roles(role)
#         await ctx.send(f"{ctx.author.mention} has had the role '{tester_role}' removed")
#     else:
#         await ctx.send("Role doesn't exist")

# @bot.command()
# async def dm(ctx, *, msg):
#     await ctx.author.send(f"You said {msg}")

# @bot.command()
# async def reply(ctx):
#     await ctx.reply("This is a reply to your message!")

# @bot.command()
# async def poll(ctx, *, question):
#     embed = discord.Embed(title="New Poll", description=question)
#     poll_message = await ctx.send(embed=embed)
#     await poll_message.add_reaction("👍")
#     await poll_message.add_reaction("👎")

# @bot.command()
# @commands.has_role(tester_role)
# async def secret(ctx):
#     await ctx.send("Welcome to the club!")

# @secret.error
# async def secret_error(ctx, error):
#     if isinstance(error, commands.MissingRole):
#         await ctx.send("You do not have permission to join the club.")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
