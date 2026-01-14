"""Tests for event_handlers.py"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import discord

from event_handlers import (
    handle_foodshop_war,
    handle_hq_war,
    handle_pvp_tournament,
    handle_uni_events,
    handle_battle_dimension,
    handle_battle_match,
    handle_battle_simulation,
    handle_freedom_village,
    handle_monster_invasion,
    handle_open_pvp_battle,
    handle_outlaw,
)
from constants import (
    FSWAR_ROLE_NAME,
    HQWAR_ROLE_NAME,
    PVP_TOURNAMENT_ROLE_NAME,
    UNI_ROLE_NAME,
    BD_ROLE_NAME,
    BM_ROLE_NAME,
    BSIM_ROLE_NAME,
    FV_ROLE_NAME,
    MI_ROLE_NAME,
    PVP_BATTLE_ROLE_NAME,
    OUTLAW_ROLE_NAME,
)


@pytest.fixture
def mock_guild():
    """Create a mock guild with roles"""
    guild = MagicMock(spec=discord.Guild)
    guild.roles = []
    return guild


@pytest.fixture
def mock_alert_channel():
    """Create a mock alert channel"""
    channel = AsyncMock(spec=discord.TextChannel)
    channel.send = AsyncMock()
    return channel


@pytest.fixture
def mock_message():
    """Create a mock message"""
    message = MagicMock(spec=discord.Message)
    message.content = ""
    return message


@pytest.fixture
def mock_role():
    """Create a mock role"""
    role = MagicMock(spec=discord.Role)
    role.mention = "<@&123456789>"
    role.name = ""
    return role


class TestHandleFoodshopWar:
    """Tests for handle_foodshop_war"""

    @pytest.mark.asyncio
    async def test_handles_street_2_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**food shop war is starting in 15 minutes in street 2!**"
        mock_role.name = FSWAR_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_foodshop_war(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Food Shop War (street 2) starts in 15 minutes!"
            )

    @pytest.mark.asyncio
    async def test_handles_signus_ax1_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**food shop war is starting in 15 minutes in signus ax-1!**"
        mock_role.name = FSWAR_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_foodshop_war(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Food Shop War (Signus AX-1) starts in 15 minutes!"
            )

    @pytest.mark.asyncio
    async def test_handles_downtown_4_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**food shop war is starting in 15 minutes in downtown 4!**"
        mock_role.name = FSWAR_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_foodshop_war(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Food Shop War (Downtown 4) starts in 15 minutes!"
            )

    @pytest.mark.asyncio
    async def test_ignores_non_matching_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "Some random message"
        
        await handle_foodshop_war(mock_message, mock_guild, mock_alert_channel)
        mock_alert_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_case_insensitive(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**FOOD SHOP WAR IS STARTING IN 15 MINUTES IN STREET 2!**"
        mock_role.name = FSWAR_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_foodshop_war(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once()


class TestHandleHqWar:
    """Tests for handle_hq_war"""

    @pytest.mark.asyncio
    async def test_handles_hq_war_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**hq war starting in 5 minutes!**"
        mock_role.name = HQWAR_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_hq_war(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} HQ War starts in 5 minutes!"
            )

    @pytest.mark.asyncio
    async def test_ignores_non_matching_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "Some random message"
        
        await handle_hq_war(mock_message, mock_guild, mock_alert_channel)
        mock_alert_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_case_insensitive(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**HQ WAR STARTING IN 5 MINUTES!**"
        mock_role.name = HQWAR_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_hq_war(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once()


class TestHandlePvpTournament:
    """Tests for handle_pvp_tournament"""

    @pytest.mark.asyncio
    async def test_handles_pvp_tournament_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**pvp tournament starts in 20 minutes, please opt in in the special battle arena!**"
        mock_role.name = PVP_TOURNAMENT_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_pvp_tournament(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} PvP Tournament starts in 20 minutes!  Opt in!"
            )

    @pytest.mark.asyncio
    async def test_ignores_non_matching_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "Some random message"
        
        await handle_pvp_tournament(mock_message, mock_guild, mock_alert_channel)
        mock_alert_channel.send.assert_not_called()


class TestHandleUniEvents:
    """Tests for handle_uni_events"""

    @pytest.mark.asyncio
    async def test_handles_uni_raid_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**sky skirmish complete, join the uni raid within 5 minutes (solo or as a group)!**"
        mock_role.name = UNI_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_uni_events(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Uni open for 5 minutes"
            )

    @pytest.mark.asyncio
    async def test_handles_uni_dungeon_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**sky dungeon skirmish complete, join the uni sky dungeon raid within 5 minutes (solo or as a group)!**"
        mock_role.name = UNI_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_uni_events(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Uni Dungeon open for 5 minutes"
            )

    @pytest.mark.asyncio
    async def test_ignores_non_matching_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "Some random message"
        
        await handle_uni_events(mock_message, mock_guild, mock_alert_channel)
        mock_alert_channel.send.assert_not_called()


class TestHandleBattleDimension:
    """Tests for handle_battle_dimension"""

    @pytest.mark.asyncio
    async def test_handles_battle_dimension_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**battle dimension starts in 30 minutes!**"
        mock_role.name = BD_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_battle_dimension(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Battle Dimension opens in 30 minutes"
            )

    @pytest.mark.asyncio
    async def test_ignores_non_matching_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "Some random message"
        
        await handle_battle_dimension(mock_message, mock_guild, mock_alert_channel)
        mock_alert_channel.send.assert_not_called()


class TestHandleBattleMatch:
    """Tests for handle_battle_match"""

    @pytest.mark.asyncio
    async def test_handles_battle_match_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**battle match opens in 30 minutes!**"
        mock_role.name = BM_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_battle_match(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Battle Match opens in 30 minutes!"
            )

    @pytest.mark.asyncio
    async def test_ignores_non_matching_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "Some random message"
        
        await handle_battle_match(mock_message, mock_guild, mock_alert_channel)
        mock_alert_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_case_insensitive(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**BATTLE MATCH OPENS IN 30 MINUTES!**"
        mock_role.name = BM_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_battle_match(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once()


class TestHandleBattleSimulation:
    """Tests for handle_battle_simulation"""

    @pytest.mark.asyncio
    async def test_handles_battle_simulation_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**battle simulation opens in 5 minutes!**"
        mock_role.name = BSIM_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_battle_simulation(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Battle Simulation opens in 5 minutes!"
            )

    @pytest.mark.asyncio
    async def test_ignores_non_matching_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "Some random message"
        
        await handle_battle_simulation(mock_message, mock_guild, mock_alert_channel)
        mock_alert_channel.send.assert_not_called()


class TestHandleFreedomVillage:
    """Tests for handle_freedom_village"""

    @pytest.mark.asyncio
    async def test_handles_freedom_village_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**sky city is launching an attack on freedom village in 30 minutes!**"
        mock_role.name = FV_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_freedom_village(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Freedom Village in 30 minutes!"
            )

    @pytest.mark.asyncio
    async def test_ignores_non_matching_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "Some random message"
        
        await handle_freedom_village(mock_message, mock_guild, mock_alert_channel)
        mock_alert_channel.send.assert_not_called()


class TestHandleMonsterInvasion:
    """Tests for handle_monster_invasion"""

    @pytest.mark.asyncio
    async def test_handles_monster_invasion_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**monster invasion starts in 30 minutes!**"
        mock_role.name = MI_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_monster_invasion(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Monster Invasion starts in 30 minutes!"
            )

    @pytest.mark.asyncio
    async def test_ignores_non_matching_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "Some random message"
        
        await handle_monster_invasion(mock_message, mock_guild, mock_alert_channel)
        mock_alert_channel.send.assert_not_called()


class TestHandleOpenPvpBattle:
    """Tests for handle_open_pvp_battle"""

    @pytest.mark.asyncio
    async def test_handles_open_pvp_battle_with_map(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**open pvp battle starts in 30 minutes in street 2!**"
        mock_role.name = PVP_BATTLE_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_open_pvp_battle(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Open PvP Battle starts in 30 minutes in street 2!"
            )

    @pytest.mark.asyncio
    async def test_handles_open_pvp_battle_with_multi_word_map(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**open pvp battle starts in 30 minutes in downtown 4!**"
        mock_role.name = PVP_BATTLE_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_open_pvp_battle(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} Open PvP Battle starts in 30 minutes in downtown 4!"
            )

    @pytest.mark.asyncio
    async def test_ignores_non_matching_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "Some random message"
        
        await handle_open_pvp_battle(mock_message, mock_guild, mock_alert_channel)
        mock_alert_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_handles_parse_error_gracefully(self, mock_guild, mock_alert_channel, mock_message):
        # Test case where an exception occurs during parsing (inside the try block)
        # We'll create a message that causes an exception when split() is called
        class ErrorString:
            def lower(self):
                return self
            
            def startswith(self, prefix):
                return True
            
            def split(self):
                raise Exception("Parse error")
        
        class ErrorMessage:
            @property
            def content(self):
                return ErrorString()
        
        error_message = ErrorMessage()
        
        with patch('builtins.print') as mock_print:
            await handle_open_pvp_battle(error_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_not_called()
            # The exception should be caught and printed
            mock_print.assert_called()


class TestHandleOutlaw:
    """Tests for handle_outlaw"""

    @pytest.mark.asyncio
    async def test_handles_outlaw_announcement(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**player TestPlayer became an outlaw at street 2!**"
        mock_role.name = OUTLAW_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_outlaw(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} TestPlayer became an outlaw at street 2!"
            )

    @pytest.mark.asyncio
    async def test_handles_outlaw_with_multi_word_map(self, mock_guild, mock_alert_channel, mock_message, mock_role):
        mock_message.content = "**player AnotherPlayer became an outlaw at downtown 4!**"
        mock_role.name = OUTLAW_ROLE_NAME
        mock_guild.roles = [mock_role]
        
        with patch('event_handlers.get_role_mention', return_value=mock_role.mention):
            await handle_outlaw(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_called_once_with(
                f"{mock_role.mention} AnotherPlayer became an outlaw at downtown 4!"
            )

    @pytest.mark.asyncio
    async def test_ignores_non_matching_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "Some random message"
        
        await handle_outlaw(mock_message, mock_guild, mock_alert_channel)
        mock_alert_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_ignores_malformed_outlaw_message(self, mock_guild, mock_alert_channel, mock_message):
        mock_message.content = "**player TestPlayer something else!**"
        
        with patch('builtins.print') as mock_print:
            await handle_outlaw(mock_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_not_called()
            mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_handles_parse_error_gracefully(self, mock_guild, mock_alert_channel, mock_message):
        # Test case where an exception occurs during parsing (inside the try block)
        # We need to trigger an exception after the startswith check passes
        # So we'll use a message that passes the check but causes an error in split()
        class ErrorString:
            def lower(self):
                return self
            
            def startswith(self, prefix):
                return True
            
            def split(self):
                raise Exception("Parse error")
        
        class ErrorMessage:
            @property
            def content(self):
                return ErrorString()
        
        error_message = ErrorMessage()
        
        with patch('builtins.print') as mock_print:
            await handle_outlaw(error_message, mock_guild, mock_alert_channel)
            mock_alert_channel.send.assert_not_called()
            # The exception should be caught and printed
            mock_print.assert_called()

