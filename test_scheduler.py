"""Tests for scheduler.py"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from datetime import datetime, timedelta
import json
import os

from scheduler import ScheduledAnnouncement, AnnouncementScheduler
from constants import RM2_SERVER_ID, ALERTS_CHANNEL_NAME


class TestScheduledAnnouncement:
    """Tests for ScheduledAnnouncement dataclass"""
    
    def test_to_dict(self):
        """Test serialization to dictionary"""
        announcement_time = datetime(2024, 1, 1, 12, 0, 0)
        event_time = datetime(2024, 1, 1, 12, 15, 0)
        
        announcement = ScheduledAnnouncement(
            event_type="big_santa",
            announcement_time=announcement_time,
            event_time=event_time,
            role_name="test-role",
            message_template="{role} Test message {timestamp}"
        )
        
        result = announcement.to_dict()
        
        assert result["event_type"] == "big_santa"
        assert result["announcement_time"] == announcement_time.isoformat()
        assert result["event_time"] == event_time.isoformat()
        assert result["role_name"] == "test-role"
        assert result["message_template"] == "{role} Test message {timestamp}"
    
    def test_from_dict(self):
        """Test deserialization from dictionary"""
        data = {
            "event_type": "big_santa",
            "announcement_time": "2024-01-01T12:00:00",
            "event_time": "2024-01-01T12:15:00",
            "role_name": "test-role",
            "message_template": "{role} Test message {timestamp}"
        }
        
        announcement = ScheduledAnnouncement.from_dict(data)
        
        assert announcement.event_type == "big_santa"
        assert announcement.announcement_time == datetime(2024, 1, 1, 12, 0, 0)
        assert announcement.event_time == datetime(2024, 1, 1, 12, 15, 0)
        assert announcement.role_name == "test-role"
        assert announcement.message_template == "{role} Test message {timestamp}"
    
    def test_round_trip_serialization(self):
        """Test that serialization and deserialization are reversible"""
        original = ScheduledAnnouncement(
            event_type="test_event",
            announcement_time=datetime(2024, 6, 15, 14, 30, 45),
            event_time=datetime(2024, 6, 15, 14, 45, 45),
            role_name="test-role",
            message_template="Test {role} at {timestamp}"
        )
        
        serialized = original.to_dict()
        deserialized = ScheduledAnnouncement.from_dict(serialized)
        
        assert deserialized.event_type == original.event_type
        assert deserialized.announcement_time == original.announcement_time
        assert deserialized.event_time == original.event_time
        assert deserialized.role_name == original.role_name
        assert deserialized.message_template == original.message_template


class TestAnnouncementScheduler:
    """Tests for AnnouncementScheduler class"""
    
    @pytest.fixture
    def mock_bot(self):
        """Create a mock Discord bot"""
        bot = MagicMock()
        bot.guilds = []
        bot.wait_until_ready = AsyncMock()
        return bot
    
    @pytest.fixture
    def mock_guild(self):
        """Create a mock guild"""
        guild = MagicMock()
        guild.id = 12345
        guild.name = "Test Guild"
        guild.channels = []
        return guild
    
    @pytest.fixture
    def mock_alert_channel(self):
        """Create a mock alert channel"""
        channel = AsyncMock()
        channel.name = ALERTS_CHANNEL_NAME
        channel.send = AsyncMock()
        return channel
    
    @pytest.fixture
    def mock_role(self):
        """Create a mock role"""
        role = MagicMock()
        role.mention = "<@&123456789>"
        role.name = "test-role"
        return role
    
    def test_schedule_adds_announcement(self, mock_bot, tmp_path):
        """Test that schedule() adds an announcement"""
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(tmp_path / "test_announcements.json")):
            with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                mock_task.start = MagicMock()
                scheduler = AnnouncementScheduler(mock_bot)
                
                announcement_time = datetime.now() + timedelta(hours=1)
                event_time = datetime.now() + timedelta(hours=1, minutes=15)
                
                scheduler.schedule(
                    event_type="test_event",
                    announcement_time=announcement_time,
                    event_time=event_time,
                    role_name="test-role",
                    message_template="Test {role} {timestamp}"
                )
                
                assert len(scheduler.announcements) == 1
                assert scheduler.announcements[0].event_type == "test_event"
                assert scheduler.announcements[0].announcement_time == announcement_time
                assert scheduler.announcements[0].event_time == event_time
    
    def test_schedule_replaces_existing_event_type(self, mock_bot, tmp_path):
        """Test that scheduling the same event type replaces the old one"""
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(tmp_path / "test_announcements.json")):
            with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                mock_task.start = MagicMock()
                scheduler = AnnouncementScheduler(mock_bot)
                
                announcement_time1 = datetime.now() + timedelta(hours=1)
                event_time1 = datetime.now() + timedelta(hours=1, minutes=15)
                
                scheduler.schedule(
                    event_type="test_event",
                    announcement_time=announcement_time1,
                    event_time=event_time1,
                    role_name="test-role",
                    message_template="First"
                )
                
                announcement_time2 = datetime.now() + timedelta(hours=2)
                event_time2 = datetime.now() + timedelta(hours=2, minutes=15)
                
                scheduler.schedule(
                    event_type="test_event",
                    announcement_time=announcement_time2,
                    event_time=event_time2,
                    role_name="test-role",
                    message_template="Second"
                )
                
                assert len(scheduler.announcements) == 1
                assert scheduler.announcements[0].message_template == "Second"
                assert scheduler.announcements[0].announcement_time == announcement_time2
    
    def test_cancel_removes_announcement(self, mock_bot, tmp_path):
        """Test that cancel() removes an announcement"""
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(tmp_path / "test_announcements.json")):
            with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                mock_task.start = MagicMock()
                scheduler = AnnouncementScheduler(mock_bot)
                
                announcement_time = datetime.now() + timedelta(hours=1)
                event_time = datetime.now() + timedelta(hours=1, minutes=15)
                
                scheduler.schedule(
                    event_type="test_event",
                    announcement_time=announcement_time,
                    event_time=event_time,
                    role_name="test-role",
                    message_template="Test"
                )
                
                assert len(scheduler.announcements) == 1
                
                scheduler.cancel("test_event")
                
                assert len(scheduler.announcements) == 0
    
    def test_cancel_nonexistent_event(self, mock_bot, tmp_path):
        """Test that cancel() handles nonexistent events gracefully"""
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(tmp_path / "test_announcements.json")):
            with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                mock_task.start = MagicMock()
                scheduler = AnnouncementScheduler(mock_bot)
                
                scheduler.cancel("nonexistent")
                
                assert len(scheduler.announcements) == 0
    
    def test_save_and_load_from_file(self, mock_bot, tmp_path):
        """Test saving and loading announcements from file"""
        storage_file = tmp_path / "test_announcements.json"
        
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(storage_file)):
            with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                mock_task.start = MagicMock()
                scheduler = AnnouncementScheduler(mock_bot)
                
                announcement_time = datetime.now() + timedelta(hours=1)
                event_time = datetime.now() + timedelta(hours=1, minutes=15)
                
                scheduler.schedule(
                    event_type="test_event",
                    announcement_time=announcement_time,
                    event_time=event_time,
                    role_name="test-role",
                    message_template="Test {role} {timestamp}"
                )
                
                # Create a new scheduler to test loading
                with patch.object(AnnouncementScheduler.check_announcements, 'start', MagicMock()):
                    scheduler2 = AnnouncementScheduler(mock_bot)
                
                assert len(scheduler2.announcements) == 1
                assert scheduler2.announcements[0].event_type == "test_event"
                assert scheduler2.announcements[0].announcement_time == announcement_time
    
    def test_load_filters_past_announcements(self, mock_bot, tmp_path):
        """Test that loading filters out past announcements"""
        storage_file = tmp_path / "test_announcements.json"
        
        # Create file with past and future announcements
        past_time = datetime.now() - timedelta(hours=1)
        future_time = datetime.now() + timedelta(hours=1)
        
        data = [
            {
                "event_type": "past_event",
                "announcement_time": past_time.isoformat(),
                "event_time": (past_time + timedelta(minutes=15)).isoformat(),
                "role_name": "test-role",
                "message_template": "Past"
            },
            {
                "event_type": "future_event",
                "announcement_time": future_time.isoformat(),
                "event_time": (future_time + timedelta(minutes=15)).isoformat(),
                "role_name": "test-role",
                "message_template": "Future"
            }
        ]
        
        with open(storage_file, 'w') as f:
            json.dump(data, f)
        
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(storage_file)):
            with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                mock_task.start = MagicMock()
                scheduler = AnnouncementScheduler(mock_bot)
                
                assert len(scheduler.announcements) == 1
                assert scheduler.announcements[0].event_type == "future_event"
    
    def test_load_handles_missing_file(self, mock_bot, tmp_path):
        """Test that loading handles missing file gracefully"""
        storage_file = tmp_path / "nonexistent.json"
        
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(storage_file)):
            with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                mock_task.start = MagicMock()
                scheduler = AnnouncementScheduler(mock_bot)
                
                assert len(scheduler.announcements) == 0
    
    def test_load_handles_invalid_json(self, mock_bot, tmp_path):
        """Test that loading handles invalid JSON gracefully"""
        storage_file = tmp_path / "invalid.json"
        
        with open(storage_file, 'w') as f:
            f.write("invalid json content")
        
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(storage_file)):
            with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                mock_task.start = MagicMock()
                scheduler = AnnouncementScheduler(mock_bot)
                
                assert len(scheduler.announcements) == 0
    
    @pytest.mark.asyncio
    async def test_check_announcements_sends_due_announcements(self, mock_bot, mock_guild, mock_alert_channel, mock_role, tmp_path):
        """Test that check_announcements sends due announcements"""
        storage_file = tmp_path / "test_announcements.json"
        mock_guild.channels = [mock_alert_channel]
        mock_bot.guilds = [mock_guild]
        
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(storage_file)):
            # Patch start() to prevent the task from actually starting
            with patch.object(AnnouncementScheduler.check_announcements, 'start', MagicMock()):
                scheduler = AnnouncementScheduler(mock_bot)
                
                # Schedule an announcement that's due now
                announcement_time = datetime.now() - timedelta(seconds=30)
                event_time = datetime.now() + timedelta(minutes=15)
                
                scheduler.schedule(
                    event_type="test_event",
                    announcement_time=announcement_time,
                    event_time=event_time,
                    role_name="test-role",
                    message_template="{role} Test {timestamp}"
                )
                
                with patch('scheduler.get_role_mention', return_value=mock_role.mention):
                    with patch('scheduler.get_next_event_time', return_value="<t:1234567890:F>"):
                        await scheduler.check_announcements()
                
                # Announcement should be sent and removed
                assert len(scheduler.announcements) == 0
                mock_alert_channel.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_announcements_cleans_up_past_announcements(self, mock_bot, tmp_path):
        """Test that check_announcements removes past announcements"""
        storage_file = tmp_path / "test_announcements.json"
        
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(storage_file)):
            # Patch start() to prevent the task from actually starting
            with patch.object(AnnouncementScheduler.check_announcements, 'start', MagicMock()):
                scheduler = AnnouncementScheduler(mock_bot)
                
                # Add a past announcement directly (simulating missed announcement)
                past_time = datetime.now() - timedelta(hours=1)
                event_time = datetime.now() - timedelta(minutes=45)
                
                announcement = ScheduledAnnouncement(
                    event_type="past_event",
                    announcement_time=past_time,
                    event_time=event_time,
                    role_name="test-role",
                    message_template="Past"
                )
                scheduler.announcements.append(announcement)
                
                await scheduler.check_announcements()
                
                # Past announcement should be removed
                assert len(scheduler.announcements) == 0
    
    @pytest.mark.asyncio
    async def test_check_announcements_does_not_send_future_announcements(self, mock_bot, mock_guild, mock_alert_channel, tmp_path):
        """Test that check_announcements doesn't send future announcements"""
        storage_file = tmp_path / "test_announcements.json"
        mock_guild.channels = [mock_alert_channel]
        mock_bot.guilds = [mock_guild]
        
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(storage_file)):
            # Patch start() to prevent the task from actually starting
            with patch.object(AnnouncementScheduler.check_announcements, 'start', MagicMock()):
                scheduler = AnnouncementScheduler(mock_bot)
                
                # Schedule a future announcement
                announcement_time = datetime.now() + timedelta(hours=1)
                event_time = datetime.now() + timedelta(hours=1, minutes=15)
                
                scheduler.schedule(
                    event_type="future_event",
                    announcement_time=announcement_time,
                    event_time=event_time,
                    role_name="test-role",
                    message_template="Future"
                )
                
                await scheduler.check_announcements()
                
                # Announcement should still be in queue
                assert len(scheduler.announcements) == 1
                mock_alert_channel.send.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_announcement_sends_to_all_guilds(self, mock_bot, mock_guild, mock_alert_channel, mock_role, tmp_path):
        """Test that send_announcement sends to all guilds"""
        storage_file = tmp_path / "test_announcements.json"
        mock_guild.channels = [mock_alert_channel]
        mock_bot.guilds = [mock_guild]
        
        announcement = ScheduledAnnouncement(
            event_type="test_event",
            announcement_time=datetime.now(),
            event_time=datetime.now() + timedelta(minutes=15),
            role_name="test-role",
            message_template="{role} Test {timestamp}"
        )
        
        with patch('scheduler.get_role_mention', return_value=mock_role.mention):
            with patch('scheduler.get_next_event_time', return_value="<t:1234567890:F>"):
                with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(storage_file)):
                    with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                        mock_task.start = MagicMock()
                        scheduler = AnnouncementScheduler(mock_bot)
                        
                        await scheduler.send_announcement(announcement)
                        
                        mock_alert_channel.send.assert_called_once()
                        call_args = mock_alert_channel.send.call_args[0][0]
                        assert mock_role.mention in call_args
                        assert "<t:1234567890:F>" in call_args
    
    @pytest.mark.asyncio
    async def test_send_announcement_skips_rm2_server(self, mock_bot, mock_guild, mock_alert_channel, tmp_path):
        """Test that send_announcement skips RM2 server"""
        storage_file = tmp_path / "test_announcements.json"
        rm2_guild = MagicMock()
        rm2_guild.id = RM2_SERVER_ID
        rm2_guild.channels = [mock_alert_channel]
        
        mock_guild.channels = [mock_alert_channel]
        mock_bot.guilds = [rm2_guild, mock_guild]
        
        announcement = ScheduledAnnouncement(
            event_type="test_event",
            announcement_time=datetime.now(),
            event_time=datetime.now() + timedelta(minutes=15),
            role_name="test-role",
            message_template="Test"
        )
        
        with patch('scheduler.get_role_mention', return_value="<@&123>"):
            with patch('scheduler.get_next_event_time', return_value="<t:1234567890:F>"):
                with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(storage_file)):
                    with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                        mock_task.start = MagicMock()
                        scheduler = AnnouncementScheduler(mock_bot)
                        
                        await scheduler.send_announcement(announcement)
                        
                        # Should only send to non-RM2 guild
                        assert mock_alert_channel.send.call_count == 1
    
    @pytest.mark.asyncio
    async def test_send_announcement_handles_missing_channel(self, mock_bot, mock_guild, tmp_path):
        """Test that send_announcement handles missing alert channel gracefully"""
        storage_file = tmp_path / "test_announcements.json"
        mock_guild.channels = []  # No alert channel
        mock_bot.guilds = [mock_guild]
        
        announcement = ScheduledAnnouncement(
            event_type="test_event",
            announcement_time=datetime.now(),
            event_time=datetime.now() + timedelta(minutes=15),
            role_name="test-role",
            message_template="Test"
        )
        
        with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(storage_file)):
            with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                mock_task.start = MagicMock()
                scheduler = AnnouncementScheduler(mock_bot)
                
                # Should not raise an exception
                await scheduler.send_announcement(announcement)
    
    @pytest.mark.asyncio
    async def test_send_announcement_handles_permission_errors(self, mock_bot, mock_guild, mock_alert_channel, tmp_path):
        """Test that send_announcement handles permission errors gracefully"""
        storage_file = tmp_path / "test_announcements.json"
        import discord
        mock_alert_channel.send = AsyncMock(side_effect=discord.Forbidden(MagicMock(), "test"))
        mock_guild.channels = [mock_alert_channel]
        mock_bot.guilds = [mock_guild]
        
        announcement = ScheduledAnnouncement(
            event_type="test_event",
            announcement_time=datetime.now(),
            event_time=datetime.now() + timedelta(minutes=15),
            role_name="test-role",
            message_template="Test"
        )
        
        with patch('scheduler.get_role_mention', return_value="<@&123>"):
            with patch('scheduler.get_next_event_time', return_value="<t:1234567890:F>"):
                with patch('scheduler.AnnouncementScheduler.STORAGE_FILE', str(storage_file)):
                    with patch.object(AnnouncementScheduler, 'check_announcements') as mock_task:
                        mock_task.start = MagicMock()
                        scheduler = AnnouncementScheduler(mock_bot)
                        
                        # Should not raise an exception
                        await scheduler.send_announcement(announcement)

