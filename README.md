# Cursor Cloud Sync

A Python tool to automatically sync Cursor editor settings to Google Drive.

## Features

- 🔄 Automatic sync of Cursor settings to Google Drive
- 📦 Complete backup of settings, keybindings, code snippets, and more
- 🔒 Secure OAuth 2.0 authentication
- 🕒 Periodic automatic sync (configurable interval)
- 🔔 macOS system notification support
- 🗂️ Automatic cleanup of old backup files
- 📱 Cross-platform support (macOS, Linux, Windows)

## Supported Configuration Files

- `settings.json` - Main settings
- `keybindings.json` - Keybinding settings
- `snippets/` - Code snippets
- `extensions/` - Extension settings
- `workspaceStorage/` - Workspace settings

## Installation

1. Ensure you have Python 3.6 or newer
2. Run the installation script:

```bash
python setup.py
```

The installation script will:
- Install required Python packages
- Guide you through setting up Google Drive API credentials
- Check Cursor settings file paths
- Set up automatic sync (macOS)

## Google Drive API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API
4. Create credentials (OAuth 2.0 Client ID)
5. Select application type as "Desktop application"
6. Download the credentials file and rename it to `credentials.json`
7. Place `credentials.json` in the project directory

## Usage

### Basic Commands

```bash
# First-time authentication
python cursor_sync.py auth

# Upload settings to Google Drive
python cursor_sync.py up

# Download settings from Google Drive
python cursor_sync.py down

# Validate Cursor settings file paths
python cursor_sync.py validate
```

### Automatic Sync

```bash
# Run sync once
python auto_sync.py --once

# Start automatic sync (continuous)
python auto_sync.py
```

### Custom Configuration

You can modify `config.json` to customize sync settings:

```json
{
  "sync_settings": {
    "auto_sync": true,
    "sync_interval_minutes": 60,
    "backup_folder_name": "Cursor Backups",
    "max_backups": 10,
    "include_extensions": true,
    "include_workspace_storage": false
  },
  "notification_settings": {
    "enable_notifications": true,
    "success_notification": true,
    "error_notification": true
  },
  "cursor_paths": {
    "custom_enabled": false,
    "settings": null,
    "keybindings": null,
    "snippets": null,
    "extensions": null,
    "workspaceStorage": null
  }
}
```

### Custom Cursor Paths

If your Cursor configuration files are in non-standard locations, you can customize paths:

1. **Enable custom paths**: Set `cursor_paths.custom_enabled` to `true`
2. **Set paths**: Specify paths for each file/directory in `cursor_paths`

```json
{
  "cursor_paths": {
    "custom_enabled": true,
    "settings": "~/custom/cursor/settings.json",
    "keybindings": "~/custom/cursor/keybindings.json",
    "snippets": "~/custom/cursor/snippets/",
    "extensions": "~/custom/cursor/extensions/",
    "workspaceStorage": "~/custom/cursor/workspaceStorage/"
  }
}
```

## macOS Automatic Sync Setup

For macOS users, the installation script will automatically create a launchd configuration file for startup automatic sync.

### Manual launchd Service Management

```bash
# Load service
launchctl load ~/Library/LaunchAgents/com.cursor.sync.plist

# Unload service
launchctl unload ~/Library/LaunchAgents/com.cursor.sync.plist

# Check service status
launchctl list | grep cursor
```

## Troubleshooting

### Common Issues

1. **Credentials file error**
   - Ensure `credentials.json` is in the project directory
   - Check if the file format is correct

2. **Cannot find Cursor settings**
   - Ensure Cursor is installed and has been run at least once
   - Check if the settings file path is correct

3. **Sync failure**
   - Check network connection
   - Re-run `python cursor_sync.py auth`
   - Check the `sync.log` file

4. **Path issues**
   - Run `python cursor_sync.py validate` to check path status
   - Confirm Cursor settings file permissions are correct
   - Check if custom path configuration is correct

### Reset Authentication

If you encounter authentication issues, delete the `token.json` file and re-authenticate:

```bash
rm token.json
python cursor_sync.py auth
```

## File Structure

```
cursor-cloud-sync/
├── cursor_sync.py          # Main sync logic
├── auto_sync.py            # Automatic sync script
├── setup.py                # Installation setup script
├── config.json             # Configuration file
├── requirements.txt        # Python package dependencies
├── README.md              # Documentation
├── credentials.json       # Google API credentials (add yourself)
├── token.json             # Authentication token (auto-generated)
└── sync.log               # Sync log file
```

## Security

- Do not commit `credentials.json` and `token.json` to version control
- Regularly check backup files in Google Drive
- Recommended to update Google API credentials regularly

To report security vulnerabilities, please see our [Security Policy](SECURITY.md).

## License

This project is licensed under the MIT License.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to:

- 🐛 [Report bugs](https://github.com/AIcclemon/cursor-cloud-sync/issues/new?template=bug_report.yml)
- 💡 [Request features](https://github.com/AIcclemon/cursor-cloud-sync/issues/new?template=feature_request.yml)
- ❓ [Ask questions](https://github.com/AIcclemon/cursor-cloud-sync/issues/new?template=question.yml)
- 🔧 Submit code changes

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## Changelog

### v1.0.0
- Initial release
- Basic sync functionality support
- macOS automatic sync support
- System notification integration
