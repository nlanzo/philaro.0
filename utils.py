"""Utility functions for the Discord bot"""
import discord
from datetime import datetime, timedelta


def get_role_mention(guild, role_name):
    """Helper function to get role mention or fallback to @role_name"""
    role = discord.utils.get(guild.roles, name=role_name)
    return role.mention if role else f"@{role_name}"


def get_next_event_time(current_time, minutes_until_next):
    """
    Calculate the time of the next occurrence of an event and return it in Discord timestamp format.
    
    Args:
        current_time: datetime object representing the current time
        minutes_until_next: int or float representing the number of minutes until the next occurrence
    
    Returns:
        str: Discord timestamp format string (e.g., '<t:1767048372:F>')
    """
    next_time = current_time + timedelta(minutes=minutes_until_next)
    unix_timestamp = int(next_time.timestamp())
    return f"<t:{unix_timestamp}:F>"
