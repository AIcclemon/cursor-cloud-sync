#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor Configuration Sync Tool
Automatically sync Cursor editor settings to Google Drive
"""

import os
import json
import shutil
import time
import platform
from datetime import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import zipfile
import tempfile

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class CursorSyncManager:
    def __init__(self, credentials_path='credentials.json', token_path='token.json', config_path='config.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.config_path = config_path
        self.service = None
        self.cursor_config_paths = self._get_cursor_config_paths()
        
    def _get_cursor_config_paths(self):
        """Get Cursor configuration file paths"""
        # Try to read custom paths from configuration file
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    cursor_paths = config.get('cursor_paths', {})
                    
                    if cursor_paths.get('custom_enabled', False):
                        # Use custom paths
                        custom_paths = {}
                        for key in ['settings', 'keybindings', 'snippets', 'extensions', 'workspaceStorage']:
                            path = cursor_paths.get(key)
                            if path:
                                custom_paths[key] = os.path.expanduser(path)
                        
                        if custom_paths:
                            return custom_paths
        except Exception as e:
            print(f"Error reading configuration file: {e}")
        
        # Use default paths (based on operating system)
        return self._get_default_cursor_paths()
    
    def validate_paths(self):
        """Validate Cursor configuration file paths"""
        validation_results = {}
        
        for name, path in self.cursor_config_paths.items():
            validation_results[name] = {
                'path': path,
                'exists': os.path.exists(path),
                'readable': False,
                'writable': False,
                'is_file': False,
                'is_dir': False
            }
            
            if os.path.exists(path):
                validation_results[name]['readable'] = os.access(path, os.R_OK)
                validation_results[name]['is_file'] = os.path.isfile(path)
                validation_results[name]['is_dir'] = os.path.isdir(path)
                
                # Check write permissions
                if os.path.isfile(path):
                    validation_results[name]['writable'] = os.access(path, os.W_OK)
                elif os.path.isdir(path):
                    validation_results[name]['writable'] = os.access(path, os.W_OK)
                else:
                    # Check parent directory write permissions
                    parent_dir = os.path.dirname(path)
                    if os.path.exists(parent_dir):
                        validation_results[name]['writable'] = os.access(parent_dir, os.W_OK)
        
        return validation_results
    
    def print_path_validation(self):
        """Print path validation results"""
        validation_results = self.validate_paths()
        
        print("\nPath Validation Results:")
        print("=" * 50)
        
        for name, result in validation_results.items():
            status = "✓" if result['exists'] else "✗"
            print(f"{status} {name}: {result['path']}")
            
            if result['exists']:
                type_str = "File" if result['is_file'] else "Directory" if result['is_dir'] else "Unknown"
                read_str = "Readable" if result['readable'] else "Not readable"
                write_str = "Writable" if result['writable'] else "Not writable"
                print(f"   Type: {type_str}, Permissions: {read_str}, {write_str}")
            else:
                print(f"   Status: Does not exist")
            print()
        
        return validation_results
    
    def _get_default_cursor_paths(self):
        """Get default Cursor configuration file paths"""
        system = platform.system().lower()
        
        if system == 'darwin':  # macOS
            return {
                'settings': os.path.expanduser('~/Library/Application Support/Cursor/User/settings.json'),
                'keybindings': os.path.expanduser('~/Library/Application Support/Cursor/User/keybindings.json'),
                'snippets': os.path.expanduser('~/Library/Application Support/Cursor/User/snippets/'),
                'extensions': os.path.expanduser('~/Library/Application Support/Cursor/User/extensions/'),
                'workspaceStorage': os.path.expanduser('~/Library/Application Support/Cursor/User/workspaceStorage/')
            }
        elif system == 'linux':  # Linux
            return {
                'settings': os.path.expanduser('~/.config/Cursor/User/settings.json'),
                'keybindings': os.path.expanduser('~/.config/Cursor/User/keybindings.json'),
                'snippets': os.path.expanduser('~/.config/Cursor/User/snippets/'),
                'extensions': os.path.expanduser('~/.config/Cursor/User/extensions/'),
                'workspaceStorage': os.path.expanduser('~/.config/Cursor/User/workspaceStorage/')
            }
        elif system == 'windows':  # Windows
            return {
                'settings': os.path.expanduser('~/AppData/Roaming/Cursor/User/settings.json'),
                'keybindings': os.path.expanduser('~/AppData/Roaming/Cursor/User/keybindings.json'),
                'snippets': os.path.expanduser('~/AppData/Roaming/Cursor/User/snippets/'),
                'extensions': os.path.expanduser('~/AppData/Roaming/Cursor/User/extensions/'),
                'workspaceStorage': os.path.expanduser('~/AppData/Roaming/Cursor/User/workspaceStorage/')
            }
        else:
            raise Exception(f"Unsupported operating system: {system}")
    
    def authenticate(self):
        """Google Drive API authentication"""
        creds = None
        
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
        return True
    
    def create_backup_archive(self):
        """Create Cursor configuration backup file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'cursor_backup_{timestamp}.zip'
        
        # Use NamedTemporaryFile instead of TemporaryDirectory to avoid automatic file deletion
        temp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        backup_path = temp_file.name
        temp_file.close()  # Close file handle so zipfile can use it
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup configuration files
            for config_name, config_path in self.cursor_config_paths.items():
                if os.path.exists(config_path):
                    if os.path.isfile(config_path):
                        zipf.write(config_path, f'{config_name}/{os.path.basename(config_path)}')
                    elif os.path.isdir(config_path):
                        for root, dirs, files in os.walk(config_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.join(config_name, 
                                                     os.path.relpath(file_path, config_path))
                                zipf.write(file_path, arcname)
            
            # Add metadata
            metadata = {
                'timestamp': timestamp,
                'platform': os.name,
                'cursor_version': self._get_cursor_version()
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as meta_file:
                json.dump(metadata, meta_file, indent=2)
                zipf.write(meta_file.name, 'metadata.json')
                os.unlink(meta_file.name)
        
        return backup_path, backup_filename
    
    def _get_cursor_version(self):
        """Get Cursor version (if possible)"""
        try:
            # Try to get version information from settings file
            settings_path = self.cursor_config_paths.get('settings')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    return settings.get('version', 'unknown')
        except:
            pass
        return 'unknown'
    
    def upload_to_drive(self, file_path, custom_filename=None, folder_name='Cursor Backups'):
        """Upload backup file to Google Drive"""
        if not self.service:
            raise Exception("Please authenticate with Google Drive first")
        
        # Find or create folder
        folder_id = self._get_or_create_folder(folder_name)
        
        # Upload file - use custom filename or original filename
        display_name = custom_filename if custom_filename else os.path.basename(file_path)
        file_metadata = {
            'name': display_name,
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(file_path, resumable=True)
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"File uploaded to Google Drive, ID: {file.get('id')}")
        return file.get('id')
    
    def _get_or_create_folder(self, folder_name):
        """Get or create Google Drive folder"""
        # Search for existing folder
        results = self.service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            return folders[0]['id']
        
        # Create new folder
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = self.service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        
        print(f"Created folder: {folder_name}")
        return folder.get('id')
    
    def download_latest_backup(self, folder_name='Cursor Backups'):
        """Download the latest backup file"""
        if not self.service:
            raise Exception("Please authenticate with Google Drive first")
        
        folder_id = self._get_or_create_folder(folder_name)
        
        # Search for backup files
        results = self.service.files().list(
            q=f"parents='{folder_id}' and name contains 'cursor_backup'",
            orderBy='createdTime desc',
            fields='files(id, name, createdTime)'
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("No backup files found")
            return None
        
        latest_file = files[0]
        file_id = latest_file['id']
        filename = latest_file['name']
        
        # Download file
        request = self.service.files().get_media(fileId=file_id)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            downloader = MediaIoBaseDownload(temp_file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download progress: {int(status.progress() * 100)}%")
            
            print(f"Downloaded: {filename}")
            return temp_file.name
    
    def restore_from_backup(self, backup_path):
        """Restore settings from backup file"""
        if not os.path.exists(backup_path):
            raise Exception(f"Backup file does not exist: {backup_path}")
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            with tempfile.TemporaryDirectory() as temp_dir:
                zipf.extractall(temp_dir)
                
                # Restore each configuration file
                for config_name, config_path in self.cursor_config_paths.items():
                    backup_config_path = os.path.join(temp_dir, config_name)
                    
                    if os.path.exists(backup_config_path):
                        # Backup current settings
                        if os.path.exists(config_path):
                            backup_current = f"{config_path}.backup_{int(time.time())}"
                            if os.path.isfile(config_path):
                                shutil.copy2(config_path, backup_current)
                            else:
                                shutil.copytree(config_path, backup_current)
                        
                        # Restore settings
                        if os.path.isfile(backup_config_path):
                            os.makedirs(os.path.dirname(config_path), exist_ok=True)
                            shutil.copy2(backup_config_path, config_path)
                        elif os.path.isdir(backup_config_path):
                            if os.path.exists(config_path):
                                shutil.rmtree(config_path)
                            shutil.copytree(backup_config_path, config_path)
                        
                        print(f"Restored: {config_name}")
    
    def sync_up(self):
        """Sync to cloud"""
        print("Starting to sync Cursor settings to Google Drive...")
        
        # Create backup file
        backup_path, backup_filename = self.create_backup_archive()
        print(f"Created backup file: {backup_path}")
        
        # Upload to Google Drive (using correct filename)
        file_id = self.upload_to_drive(backup_path, backup_filename)
        
        # Clean up temporary file
        os.unlink(backup_path)
        
        print("Sync completed!")
        return file_id
    
    def sync_down(self):
        """Sync from cloud"""
        print("Starting to sync Cursor settings from Google Drive...")
        
        # Download latest backup
        backup_path = self.download_latest_backup()
        
        if backup_path:
            # Restore settings
            self.restore_from_backup(backup_path)
            
            # Clean up temporary file
            os.unlink(backup_path)
            
            print("Sync completed!")
        else:
            print("No backup files found")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cursor Configuration Sync Tool')
    parser.add_argument('action', choices=['up', 'down', 'auth', 'validate'], 
                       help='Action: up=upload, down=download, auth=authenticate, validate=validate paths')
    parser.add_argument('--credentials', default='credentials.json',
                       help='Google API credentials file path')
    parser.add_argument('--token', default='token.json',
                       help='Authentication token file path')
    
    args = parser.parse_args()
    
    sync_manager = CursorSyncManager(
        os.path.abspath(args.credentials), 
        os.path.abspath(args.token),
        os.path.abspath('config.json')
    )
    
    if args.action == 'auth':
        if sync_manager.authenticate():
            print("Authentication successful!")
        else:
            print("Authentication failed!")
    
    elif args.action == 'up':
        sync_manager.authenticate()
        sync_manager.sync_up()
    
    elif args.action == 'down':
        sync_manager.authenticate()
        sync_manager.sync_down()
    
    elif args.action == 'validate':
        sync_manager.print_path_validation()

if __name__ == '__main__':
    main()
