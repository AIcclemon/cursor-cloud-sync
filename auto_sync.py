#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Sync Script
Periodically sync Cursor settings to Google Drive
"""

import os
import json
import logging
import time
from datetime import datetime
from cursor_sync import CursorSyncManager

class AutoSyncManager:
    def __init__(self, config_path='config.json'):
        self.config_path = os.path.abspath(config_path)
        self.config = self._load_config()
        self._setup_logging()
        
    def _load_config(self):
        """Load configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Configuration file {self.config_path} does not exist, using default settings")
            return {
                "sync_settings": {
                    "auto_sync": False,
                    "sync_interval_minutes": 60,
                    "backup_folder_name": "Cursor Backups",
                    "max_backups": 10,
                    "include_extensions": True,
                    "include_workspace_storage": False
                },
                "notification_settings": {
                    "enable_notifications": True,
                    "success_notification": True,
                    "error_notification": True
                },
                "paths": {
                    "credentials_file": os.path.abspath("credentials.json"),
                    "token_file": os.path.abspath("token.json"),
                    "log_file": os.path.abspath("sync.log")
                }
            }
    
    def _setup_logging(self):
        """Setup logging"""
        log_file = self.config['paths']['log_file']
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _send_notification(self, title, message):
        """Send system notification"""
        if not self.config['notification_settings']['enable_notifications']:
            return
        
        try:
            # macOS notification
            os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
        except:
            pass
    
    def _cleanup_old_backups(self, sync_manager):
        """Clean up old backup files"""
        max_backups = self.config['sync_settings']['max_backups']
        folder_name = self.config['sync_settings']['backup_folder_name']
        
        try:
            folder_id = sync_manager._get_or_create_folder(folder_name)
            
            # Search for all backup files
            results = sync_manager.service.files().list(
                q=f"parents='{folder_id}' and name contains 'cursor_backup'",
                orderBy='createdTime desc',
                fields='files(id, name, createdTime)'
            ).execute()
            
            files = results.get('files', [])
            
            # If exceeding maximum backup count, delete old backups
            if len(files) > max_backups:
                files_to_delete = files[max_backups:]
                for file_to_delete in files_to_delete:
                    sync_manager.service.files().delete(fileId=file_to_delete['id']).execute()
                    self.logger.info(f"Deleted old backup: {file_to_delete['name']}")
        
        except Exception as e:
            self.logger.error(f"Error occurred while cleaning up old backups: {str(e)}")
    
    def sync_once(self):
        """Execute sync once"""
        try:
            credentials_file = self.config['paths']['credentials_file']
            token_file = self.config['paths']['token_file']
            
            sync_manager = CursorSyncManager(credentials_file, token_file)
            
            # Check if credentials file exists
            if not os.path.exists(credentials_file):
                self.logger.error(f"Credentials file {credentials_file} does not exist")
                return False
            
            # Authentication
            sync_manager.authenticate()
            
            # Execute sync
            file_id = sync_manager.sync_up()
            
            # Clean up old backups
            self._cleanup_old_backups(sync_manager)
            
            self.logger.info("Sync completed successfully")
            
            if self.config['notification_settings']['success_notification']:
                self._send_notification("Cursor Sync", "Settings successfully synced to Google Drive")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Sync failed: {str(e)}")
            
            if self.config['notification_settings']['error_notification']:
                self._send_notification("Cursor Sync Error", f"Sync failed: {str(e)}")
            
            return False
    
    def start_auto_sync(self):
        """Start automatic sync"""
        if not self.config['sync_settings']['auto_sync']:
            self.logger.info("Automatic sync is disabled")
            return
        
        interval = self.config['sync_settings']['sync_interval_minutes'] * 60
        
        self.logger.info(f"Starting automatic sync, interval: {interval/60} minutes")
        
        while True:
            try:
                self.sync_once()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.logger.info("Automatic sync stopped")
                break
            except Exception as e:
                self.logger.error(f"Automatic sync error occurred: {str(e)}")
                time.sleep(interval)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cursor Automatic Sync Tool')
    parser.add_argument('--config', default='config.json',
                       help='Configuration file path')
    parser.add_argument('--once', action='store_true',
                       help='Execute sync only once')
    
    args = parser.parse_args()
    
    auto_sync = AutoSyncManager(args.config)
    
    if args.once:
        auto_sync.sync_once()
    else:
        auto_sync.start_auto_sync()

if __name__ == '__main__':
    main()
