"""Scheduler for sending announcements before events occur."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json
import os
import discord
from discord.ext import tasks
from constants import ALERTS_CHANNEL_NAME, RM2_SERVER_ID
from utils import get_role_mention, get_next_event_time


@dataclass
class ScheduledAnnouncement:
    """Represents a scheduled announcement."""
    event_type: str
    announcement_time: datetime
    event_time: datetime
    role_name: str
    message_template: str
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "event_type": self.event_type,
            "announcement_time": self.announcement_time.isoformat(),
            "event_time": self.event_time.isoformat(),
            "role_name": self.role_name,
            "message_template": self.message_template
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary loaded from JSON."""
        return cls(
            event_type=data["event_type"],
            announcement_time=datetime.fromisoformat(data["announcement_time"]),
            event_time=datetime.fromisoformat(data["event_time"]),
            role_name=data["role_name"],
            message_template=data["message_template"]
        )


class AnnouncementScheduler:
    """Manages scheduled announcements for events."""
    
    STORAGE_FILE = "scheduled_announcements.json"
    
    def __init__(self, bot: discord.Client):
        """
        Initialize the scheduler.
        
        Args:
            bot: The Discord bot client
        """
        self.bot = bot
        self.announcements: list[ScheduledAnnouncement] = []
        self.load_from_file()
        self.check_announcements.start()
    
    def schedule(
        self,
        event_type: str,
        announcement_time: datetime,
        event_time: datetime,
        role_name: str,
        message_template: str
    ):
        """
        Schedule an announcement.
        
        Args:
            event_type: Type of event (e.g., "big_santa")
            announcement_time: When to send the announcement
            event_time: When the actual event occurs
            role_name: Role to mention in the announcement
            message_template: Message template (can include {role} and {timestamp} placeholders)
        """
        # Remove any existing announcement for this event type
        self.cancel(event_type)
        
        announcement = ScheduledAnnouncement(
            event_type=event_type,
            announcement_time=announcement_time,
            event_time=event_time,
            role_name=role_name,
            message_template=message_template
        )
        self.announcements.append(announcement)
        self.save_to_file()
    
    def cancel(self, event_type: str):
        """
        Cancel a scheduled announcement.
        
        Args:
            event_type: Type of event to cancel
        """
        self.announcements = [
            a for a in self.announcements if a.event_type != event_type
        ]
        self.save_to_file()
    
    @tasks.loop(minutes=1)
    async def check_announcements(self):
        """Check for due announcements and send them."""
        now = datetime.now()
        
        # Find announcements that are due (should be sent now)
        due_announcements = [
            a for a in self.announcements
            if a.announcement_time <= now
        ]
        
        # Send and remove due announcements
        for announcement in due_announcements:
            await self.send_announcement(announcement)
            self.announcements.remove(announcement)
        
        # Clean up any past announcements that weren't caught (safety measure)
        # This handles edge cases where announcements might have been missed
        past_announcements = [
            a for a in self.announcements
            if a.announcement_time < now
        ]
        
        for announcement in past_announcements:
            print(f"Removing past announcement for {announcement.event_type} (announcement_time: {announcement.announcement_time})")
            self.announcements.remove(announcement)
        
        # Save if we made any changes
        if due_announcements or past_announcements:
            self.save_to_file()
    
    async def send_announcement(self, announcement: ScheduledAnnouncement):
        """
        Send an announcement to all guilds with proper role mentions.
        
        Args:
            announcement: The scheduled announcement to send
        """
        event_timestamp = get_next_event_time(announcement.event_time, 0)
        
        for guild in self.bot.guilds:
            if guild.id == RM2_SERVER_ID:
                continue
            
            alert_channel = discord.utils.get(guild.channels, name=ALERTS_CHANNEL_NAME)
            if alert_channel:
                try:
                    role_mention = get_role_mention(guild, announcement.role_name)
                    message = announcement.message_template.format(
                        role=role_mention,
                        timestamp=event_timestamp
                    )
                    await alert_channel.send(message)
                except discord.Forbidden:
                    print(f"Bot doesn't have permission to send messages in {guild.name}'s alerts channel")
                except Exception as e:
                    print(f"Error sending announcement to {guild.name}: {e}")
            else:
                print(f"Could not find '{ALERTS_CHANNEL_NAME}' channel in guild: {guild.name}")
    
    @check_announcements.before_loop
    async def before_check_announcements(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()
    
    def load_from_file(self):
        """Load scheduled announcements from JSON file."""
        if not os.path.exists(self.STORAGE_FILE):
            print(f"Storage file {self.STORAGE_FILE} not found, starting with empty schedule")
            return
        
        try:
            with open(self.STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                loaded_announcements = [
                    ScheduledAnnouncement.from_dict(item) for item in data
                ]
            
            # Filter out past announcements (in case bot was down)
            now = datetime.now()
            self.announcements = [
                a for a in loaded_announcements if a.announcement_time > now
            ]
            
            removed_count = len(loaded_announcements) - len(self.announcements)
            if removed_count > 0:
                print(f"Removed {removed_count} past announcement(s) when loading")
                self.save_to_file()  # Save the cleaned list
            
            print(f"Loaded {len(self.announcements)} scheduled announcement(s) from {self.STORAGE_FILE}")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from {self.STORAGE_FILE}: {e}")
            print("Starting with empty schedule")
            self.announcements = []
        except Exception as e:
            print(f"Error loading announcements from {self.STORAGE_FILE}: {e}")
            print("Starting with empty schedule")
            self.announcements = []
    
    def save_to_file(self):
        """Save scheduled announcements to JSON file."""
        try:
            data = [announcement.to_dict() for announcement in self.announcements]
            with open(self.STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving announcements to {self.STORAGE_FILE}: {e}")
    
    def cleanup(self):
        """Clean up the scheduler (stop the background task)."""
        self.check_announcements.cancel()

