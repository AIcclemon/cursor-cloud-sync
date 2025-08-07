#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Script
Helps users set up Cursor sync environment
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("Installing required packages...")
    try:
        # Check if in virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if in_venv:
            # In virtual environment, don't use --user flag
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        else:
            # Not in virtual environment, use --user flag
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', '-r', 'requirements.txt'])
        
        print("✓ Package installation complete")
        return True
    except subprocess.CalledProcessError:
        print("✗ Package installation failed")
        return False

def setup_google_credentials():
    """Setup Google API credentials"""
    print("\nSetting up Google Drive API credentials...")
    print("Please follow these steps:")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Google Drive API")
    print("4. Create credentials (OAuth 2.0 Client ID)")
    print("5. Select application type as 'Desktop application'")
    print("6. Download the credentials file and rename it to 'credentials.json'")
    print("7. Place credentials.json in this project directory")
    
    credentials_path = 'credentials.json'
    
    while not os.path.exists(credentials_path):
        input("\nPress Enter to continue checking if credentials.json exists...")
        if not os.path.exists(credentials_path):
            print(f"Cannot find {credentials_path}, please verify the file location is correct")
    
    print("✓ Found credentials file")
    return True

def create_launchd_plist():
    """Create macOS launchd configuration file"""
    print("\nCreating automatic sync configuration...")
    
    current_dir = os.getcwd()
    python_path = sys.executable
    script_path = os.path.join(current_dir, 'auto_sync.py')
    
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cursor.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
        <string>--once</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{current_dir}</string>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>{current_dir}/sync.log</string>
    <key>StandardErrorPath</key>
    <string>{current_dir}/sync.log</string>
</dict>
</plist>"""
    
    plist_path = os.path.expanduser('~/Library/LaunchAgents/com.cursor.sync.plist')
    
    # 建立目錄
    os.makedirs(os.path.dirname(plist_path), exist_ok=True)
    
    # 寫入 plist 檔案
    with open(plist_path, 'w') as f:
        f.write(plist_content)
    
    print(f"✓ Created launchd configuration file: {plist_path}")
    
    # Ask if user wants to enable automatic sync
    enable_auto = input("\nDo you want to enable automatic sync? (y/N): ").lower().strip()
    
    if enable_auto == 'y' or enable_auto == 'yes':
        try:
            subprocess.run(['launchctl', 'load', plist_path], check=True)
            print("✓ Automatic sync enabled")
            
            # Update auto_sync setting in config.json
            config_path = 'config.json'
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                config['sync_settings']['auto_sync'] = True
                
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print("✓ Configuration file updated")
        except subprocess.CalledProcessError:
            print("✗ Failed to enable automatic sync")
    
    return True

def test_cursor_paths():
    """Test Cursor settings paths"""
    print("\nChecking Cursor settings file paths...")
    
    from cursor_sync import CursorSyncManager
    
    sync_manager = CursorSyncManager()
    found_paths = []
    
    for name, path in sync_manager.cursor_config_paths.items():
        if os.path.exists(path):
            found_paths.append((name, path))
            print(f"✓ {name}: {path}")
        else:
            print(f"✗ {name}: {path} (does not exist)")
    
    if found_paths:
        print(f"\nFound {len(found_paths)} configuration files/directories")
        return True
    else:
        print("\nNo Cursor configuration files found")
        print("Please ensure Cursor is installed and has been run at least once")
        return False

def main():
    print("Cursor Cloud Sync Installation")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("Python 3.6 or newer required")
        sys.exit(1)
    
    # Install packages
    if not install_requirements():
        sys.exit(1)
    
    # Setup Google credentials
    if not setup_google_credentials():
        sys.exit(1)
    
    # Test Cursor paths
    if not test_cursor_paths():
        print("\nWarning: No Cursor configuration files found")
        print("Please ensure Cursor is installed and has been run at least once")
    
    # Create launchd configuration
    if sys.platform == 'darwin':  # macOS
        create_launchd_plist()
    
    print("\n" + "=" * 40)
    print("Setup complete!")
    print("\nUsage:")
    print("1. Manual sync: python cursor_sync.py up")
    print("2. Download settings: python cursor_sync.py down")
    print("3. Re-authenticate: python cursor_sync.py auth")
    print("4. Validate paths: python cursor_sync.py validate")
    print("5. Run sync once: python auto_sync.py --once")
    print("6. Start automatic sync: python auto_sync.py")
    
    print("\nImportant notes:")
    print("- First-time use requires Google authentication")
    print("- Configuration files will be packaged and uploaded to Google Drive")
    print("- You can adjust sync settings in config.json")

if __name__ == '__main__':
    main()
