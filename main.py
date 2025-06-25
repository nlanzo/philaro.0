import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

alerts_role = "rm2-alerts"

rm2_server_id = 859685499441512478
rm2_global_shout_user_id = 939082155483598858
lanz_user_id = 71730438560813056
lanz_server_id = 1387179883637244064
lanz_server_channel_id_general = 1387179884375179446
lanz_server_channel_id_alerts = 1387513258784718898
lanz2_server_id = 1387519724933480520
lanz2_server_channel_id_general = 1387519726225461482



@bot.event
async def on_ready():
    print(f"{bot.user.name} is here to defeat the Sun!")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.id == lanz_user_id and message.channel.id == lanz2_server_channel_id_general:
        # Send alerts to "rm2-alerts" channel in all guilds where bot is installed
        for guild in bot.guilds:
            alert_channel = discord.utils.get(guild.channels, name="rm2-alerts")
            if alert_channel:
                if "food shop war is starting in 15 minutes" in message.content.lower():
                    await alert_channel.send("Food Shop War starts in 15 minutes!")

                if "hq war starting in 5 minutes!" in message.content.lower():
                    await alert_channel.send("HQ War starts in 5 minutes!")

                if "sky skirmish complete, join the uni raid within 5 minutes" in message.content.lower():
                    await alert_channel.send("Uni open for 5 minutes")

                if "sky dungeon skirmish complete, join the uni sky dungeon raid within 5 minutes" in message.content.lower():
                    await alert_channel.send("Uni Dungeon open for 5 minutes")

                if "battle dimension starts in 30 minutes" in message.content.lower():
                    await alert_channel.send("Battle Dimension opens in 30 minutes")

                if "battle simulation opens in 5 minutes!" in message.content.lower():
                    await alert_channel.send("Battle Simulation opens in 5 minutes!")
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
