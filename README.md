# Philaro.0 - Redmoon2 Discord Bot

[Redmoon2](https://redmoon2.com)

A Discord bot that automatically announces Redmoon2 events across multiple Discord servers. The bot monitors the main RM2 server for announcements and forwards them to all connected servers with proper role-based notifications.

## Features

- **Automatic Event Monitoring**: Monitors the official RM2 Discord server for announcements
- **Multi-Server Support**: Forwards alerts to all Discord servers where the bot is installed
- **Role-Based Notifications**: Users can subscribe/unsubscribe to alerts using reactions
- **Auto-Setup**: Automatically creates required channels and roles in new servers
- **Event Types Supported**:
  - Food Shop Wars (Street 2, Signus AX-1, Downtown 4)
  - HQ Wars
  - PVP Tournament
  - Uni Raids (Sky Skirmish, Sky Dungeon)
  - Battle Dimension
  - Battle Simulation
  - Freedom Village attacks


## Usage

### For Server Administrators

1. [**Invite the bot**](https://discord.com/oauth2/authorize?client_id=1387174596947611800) to your Discord server with appropriate permissions
2. The bot will automatically create:
   - `#rm2-alerts-setup` - Channel for users to subscribe to alerts
   - `#rm2-alerts` - Channel where alerts will be posted
   - Multiple roles - One for each category of alert
3. **IMPORTANT** - Make sure the bot's role is above the alerts roles or it will not be able to assign the roles!

### For Users

1. **Subscribe to alerts**: Go to the `#rm2-alerts-setup` channel and click the appropriate reaction
2. **Unsubscribe from alerts**: Remove the reaction from the setup message
3. **Receive notifications**: You'll be pinged in `#rm2-alerts` when events are announced

## Bot Permissions Required

The bot needs the following permissions in each server:
- **Manage Roles** - To create and assign the alerts role
- **Manage Channels** - To create the alerts and setup channels
- **Send Messages** - To post alerts and setup messages
- **Read Message History** - To check for existing setup messages
- **Add Reactions** - To add the bell emoji to setup messages



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
