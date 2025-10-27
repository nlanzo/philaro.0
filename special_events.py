"""Handle special game events and send alerts to the appropriate channels."""

from constants import HALLOWVERN_ROLE_NAME


async def handle_friendly_hallowvern(message, guild, alert_channel, get_role_mention):
    """
    Handle the "friendly hallowvern appeared" special event.
    
    Args:
        message: The Discord message object
        guild: The Discord guild object
        alert_channel: The channel to send the alert to
        get_role_mention: Function to get role mentions
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
                role_mention = get_role_mention(guild, HALLOWVERN_ROLE_NAME)
                await alert_channel.send(f"{role_mention} Friendly Hallowvern appeared in {map}!")
            else:
                print(f"Could not parse map from message: {message.content}")
        except Exception as e:
            print(f"Error parsing friendly hallowvern map: {e}")

