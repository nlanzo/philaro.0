"""Tests for utils.py"""
import pytest
from datetime import datetime, timedelta

from utils import get_next_event_time


class TestGetNextEventTime:
    """Tests for get_next_event_time"""

    def test_basic_functionality_with_integer_minutes(self):
        """Test that the function correctly adds integer minutes and formats the result"""
        current_time = datetime(2024, 1, 1, 12, 0, 0)
        minutes_until_next = 15
        
        result = get_next_event_time(current_time, minutes_until_next)
        
        expected_time = current_time + timedelta(minutes=minutes_until_next)
        expected_timestamp = int(expected_time.timestamp())
        expected_format = f"<t:{expected_timestamp}:F>"
        
        assert result == expected_format

    def test_basic_functionality_with_float_minutes(self):
        """Test that the function correctly handles float minutes"""
        current_time = datetime(2024, 1, 1, 12, 0, 0)
        minutes_until_next = 15.5
        
        result = get_next_event_time(current_time, minutes_until_next)
        
        expected_time = current_time + timedelta(minutes=minutes_until_next)
        expected_timestamp = int(expected_time.timestamp())
        expected_format = f"<t:{expected_timestamp}:F>"
        
        assert result == expected_format

    def test_zero_minutes(self):
        """Test that the function handles zero minutes correctly"""
        current_time = datetime(2024, 1, 1, 12, 0, 0)
        minutes_until_next = 0
        
        result = get_next_event_time(current_time, minutes_until_next)
        
        expected_timestamp = int(current_time.timestamp())
        expected_format = f"<t:{expected_timestamp}:F>"
        
        assert result == expected_format

    def test_negative_minutes(self):
        """Test that the function handles negative minutes (past time)"""
        current_time = datetime(2024, 1, 1, 12, 0, 0)
        minutes_until_next = -30
        
        result = get_next_event_time(current_time, minutes_until_next)
        
        expected_time = current_time + timedelta(minutes=minutes_until_next)
        expected_timestamp = int(expected_time.timestamp())
        expected_format = f"<t:{expected_timestamp}:F>"
        
        assert result == expected_format

    def test_large_minutes_value(self):
        """Test that the function handles large minute values"""
        current_time = datetime(2024, 1, 1, 12, 0, 0)
        minutes_until_next = 1440  # 24 hours
        
        result = get_next_event_time(current_time, minutes_until_next)
        
        expected_time = current_time + timedelta(minutes=minutes_until_next)
        expected_timestamp = int(expected_time.timestamp())
        expected_format = f"<t:{expected_timestamp}:F>"
        
        assert result == expected_format

    def test_fractional_minutes(self):
        """Test that the function handles fractional minutes correctly"""
        current_time = datetime(2024, 1, 1, 12, 0, 0)
        minutes_until_next = 0.5  # 30 seconds
        
        result = get_next_event_time(current_time, minutes_until_next)
        
        expected_time = current_time + timedelta(minutes=minutes_until_next)
        expected_timestamp = int(expected_time.timestamp())
        expected_format = f"<t:{expected_timestamp}:F>"
        
        assert result == expected_format

    def test_discord_timestamp_format(self):
        """Test that the result follows Discord timestamp format"""
        current_time = datetime(2024, 1, 1, 12, 0, 0)
        minutes_until_next = 30
        
        result = get_next_event_time(current_time, minutes_until_next)
        
        # Verify format: <t:timestamp:F>
        assert result.startswith("<t:")
        assert result.endswith(":F>")
        assert len(result) > 5  # Should have content between <t: and :F>
        
        # Extract timestamp and verify it's numeric
        timestamp_str = result[3:-3]  # Remove <t: and :F>
        assert timestamp_str.isdigit()

    def test_timestamp_is_integer(self):
        """Test that the timestamp is converted to integer (no decimal)"""
        current_time = datetime(2024, 1, 1, 12, 0, 30)  # 30 seconds past minute
        minutes_until_next = 0.5  # 30 more seconds
        
        result = get_next_event_time(current_time, minutes_until_next)
        
        # Extract timestamp
        timestamp_str = result[3:-3]
        timestamp = int(timestamp_str)
        
        # Verify it's an integer (no decimal point in string)
        assert "." not in timestamp_str
        assert isinstance(timestamp, int)

    def test_different_datetime_values(self):
        """Test with various datetime values"""
        test_cases = [
            datetime(2024, 1, 1, 0, 0, 0),  # Midnight
            datetime(2024, 6, 15, 14, 30, 45),  # Random date/time
            datetime(2023, 12, 31, 23, 59, 59),  # End of year
        ]
        
        for current_time in test_cases:
            minutes_until_next = 60
            result = get_next_event_time(current_time, minutes_until_next)
            
            expected_time = current_time + timedelta(minutes=minutes_until_next)
            expected_timestamp = int(expected_time.timestamp())
            expected_format = f"<t:{expected_timestamp}:F>"
            
            assert result == expected_format

    def test_very_small_fractional_minutes(self):
        """Test with very small fractional minutes"""
        current_time = datetime(2024, 1, 1, 12, 0, 0)
        minutes_until_next = 0.001  # Very small value
        
        result = get_next_event_time(current_time, minutes_until_next)
        
        expected_time = current_time + timedelta(minutes=minutes_until_next)
        expected_timestamp = int(expected_time.timestamp())
        expected_format = f"<t:{expected_timestamp}:F>"
        
        assert result == expected_format

