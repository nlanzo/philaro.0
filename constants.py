# alert setup variables
import discord


ALERTS_SETUP_CHANNEL_NAME = "rm2-alerts-setup"
ALERTS_CHANNEL_NAME = "rm2-alerts"

# specific event role names
FSWAR_ROLE_NAME = "rm2-alerts-fswar"
HQWAR_ROLE_NAME = "rm2-alerts-hqwar"
PVP_TOURNAMENT_ROLE_NAME = "rm2-alerts-pvpt"
UNI_ROLE_NAME = "rm2-alerts-uni"
BD_ROLE_NAME = "rm2-alerts-bd"
BSIM_ROLE_NAME = "rm2-alerts-bsim"
FV_ROLE_NAME = "rm2-alerts-fv"
MI_ROLE_NAME = "rm2-alerts-mi"
PVP_BATTLE_ROLE_NAME = "rm2-alerts-pvpbattle"
OUTLAW_ROLE_NAME = "rm2-alerts-outlaw"

# seasonal events
SEASONAL_EVENT_ROLE_NAME = "rm2-alerts-seasonal-event"
HALLOWEEN = False
THANKSGIVING = True
CHRISTMAS = False
EASTER = False


# role configs (ROLE_NAME, REASON, COLOR, EMOJI)
ROLE_CONFIGS = [
    (FSWAR_ROLE_NAME, "Food Shop War", discord.Color.red(), "🍔"),
    (HQWAR_ROLE_NAME, "HQ War", discord.Color.red(), "🏢"),
    (PVP_TOURNAMENT_ROLE_NAME, "PvP Tournament", discord.Color.red(), "💪"),
    (UNI_ROLE_NAME, "Uni", discord.Color.blue(), "🎓"),
    (BD_ROLE_NAME, "Battle Dimension / Battle Match", discord.Color.purple(), "⚔️"),
    (BSIM_ROLE_NAME, "Battle Simulation", discord.Color.purple(), "🎮"),
    (FV_ROLE_NAME, "Freedom Village", discord.Color.blue(), "🏘️"),
    (MI_ROLE_NAME, "Monster Invasion", discord.Color.blue(), "👹"),
    (PVP_BATTLE_ROLE_NAME, "Open PvP Battle", discord.Color.purple(), "🔥"),
    (OUTLAW_ROLE_NAME, "Player became an outlaw", discord.Color.red(), "👮"),
    # halloween events
    (SEASONAL_EVENT_ROLE_NAME, "Seasonal Event", discord.Color.orange(), "🎉"),
]


# rm2 server variables
RM2_SERVER_ID = 859685499441512478
RM2_SERVER_CHANNEL_ID_GLOBAL = 939091598216675338
RM2_GLOBAL_SHOUT_USER_ID = 939082155483598858

# testing variables
DEV_SERVER_ID = 1387179883637244064
DEV_SERVER_CHANNEL_ID_GENERAL = 1387179884375179446
DEV_SERVER_CHANNEL_ID_ALERTS = 1387513258784718898
DEV2_SERVER_ID = 1387519724933480520
DEV2_SERVER_CHANNEL_ID_GENERAL = 1387519726225461482