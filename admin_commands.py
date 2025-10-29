"""Handle admin commands sent via DM."""

import discord


async def handle_server_list_command(message, bot):
    """
    Handle the !servers, !serverlist, or !guilds command via DM.
    
    Args:
        message: The Discord message object
        bot: The Discord bot instance
    """
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


async def handle_dm_commands(message, bot, admin_id):
    """
    Handle all DM commands.
    
    Args:
        message: The Discord message object
        bot: The Discord bot instance
        admin_id: The ID of the admin user
    """
    if message.author.id != admin_id:
        await message.channel.send("Hi! I'm here to defeat the Sun!")
        return
    
    if message.content.lower() in ['!servers', '!serverlist', '!guilds']:
        await handle_server_list_command(message, bot)
    else:
        # For other DMs, just acknowledge
        await message.channel.send("Hi! I'm here to defeat the Sun!")
