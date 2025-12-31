"""Handle special game events and send alerts to the appropriate channels."""

from datetime import datetime
from constants import SEASONAL_EVENT_ROLE_NAME, HALLOWEEN, THANKSGIVING, CHRISTMAS, EASTER
from utils import get_next_event_time, get_role_mention


async def handle_friendly_hallowvern(message, guild, alert_channel):
    """
    Handle the "friendly hallowvern appeared" special event.
    
    Args:
        message: The Discord message object
        guild: The Discord guild object
        alert_channel: The channel to send the alert to
    """
    if message.content.lower().startswith("**friendly hallowvern appeared in"):
        try:
            words = message.content.split()
            # Find the index of "in" and extract everything after it until the trailing "!**"
            in_index = -1
            for i, word in enumerate(words):
                if word.lower() == "in":
                    in_index = i
                    break
            if in_index != -1 and in_index + 1 < len(words):
                map_words = words[in_index + 1:]
                map = " ".join(map_words).replace("!**", "")  # Exclude the trailing "!**"
                role_mention = get_role_mention(guild, SEASONAL_EVENT_ROLE_NAME)
                await alert_channel.send(f"{role_mention} Friendly Hallowvern appeared in {map}!")
            else:
                print(f"Could not parse map from message: {message.content}")
        except Exception as e:
            print(f"Error parsing friendly hallowvern map: {e}")


async def handle_feast(message, guild, alert_channel):
    """
    Handle the "feast appeared" special event.
    
    Args:
        message: The Discord message object
        guild: The Discord guild object
        alert_channel: The channel to send the alert to
    """
    if not message.content.lower().startswith("**a thanksgiving feast has been started by"):
        return
    role_mention = get_role_mention(guild, SEASONAL_EVENT_ROLE_NAME)
    await alert_channel.send(f"{role_mention} A Thanksgiving Feast has been started!")


async def handle_santa(message, guild, alert_channel):
    """
    Handle the "big santa spawned" special event.
    
    Args:
        message: The Discord message object
        guild: The Discord guild object
        alert_channel: The channel to send the alert to
    """
    if not message.content.lower().startswith("**a big santa spawned in street 1"):
        return
    current_time = datetime.now()
    minutes_until_next = 60 * 7
    role_mention = get_role_mention(guild, SEASONAL_EVENT_ROLE_NAME)
    next_event_time = get_next_event_time(current_time, minutes_until_next)
    await alert_channel.send(f"{role_mention} Big Santa spawned in Street 1!  Next Big Santa at {next_event_time}")


async def handle_halloween(message, guild, alert_channel):
    await handle_friendly_hallowvern(message, guild, alert_channel)

async def handle_thanksgiving(message, guild, alert_channel):
    await handle_feast(message, guild, alert_channel)

async def handle_christmas(message, guild, alert_channel):
    await handle_santa(message, guild, alert_channel)

async def handle_seasonal_event(message, guild, alert_channel):
    """
    Handle the seasonal event.
    
    Args:
        message: The Discord message object
        guild: The Discord guild object
        alert_channel: The channel to send the alert to
    """
    if HALLOWEEN:
        await handle_halloween(message, guild, alert_channel)
    elif THANKSGIVING:
        await handle_thanksgiving(message, guild, alert_channel)
    elif CHRISTMAS:
        await handle_christmas(message, guild, alert_channel)