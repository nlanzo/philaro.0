"""Utility functions for the Discord bot"""
import discord


def get_role_mention(guild, role_name):
    """Helper function to get role mention or fallback to @role_name"""
    role = discord.utils.get(guild.roles, name=role_name)
    return role.mention if role else f"@{role_name}"
