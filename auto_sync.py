#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動化同步腳本
定期將 Cursor 設定同步到 Google Drive
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
        """載入設定檔"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"設定檔 {self.config_path} 不存在，使用預設設定")
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
        """設定記錄"""
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
        """發送系統通知"""
        if not self.config['notification_settings']['enable_notifications']:
            return
        
        try:
            # macOS 通知
            os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
        except:
            pass
    
    def _cleanup_old_backups(self, sync_manager):
        """清理舊的備份檔案"""
        max_backups = self.config['sync_settings']['max_backups']
        folder_name = self.config['sync_settings']['backup_folder_name']
        
        try:
            folder_id = sync_manager._get_or_create_folder(folder_name)
            
            # 搜尋所有備份檔案
            results = sync_manager.service.files().list(
                q=f"parents='{folder_id}' and name contains 'cursor_backup'",
                orderBy='createdTime desc',
                fields='files(id, name, createdTime)'
            ).execute()
            
            files = results.get('files', [])
            
            # 如果超過最大備份數量，刪除舊的備份
            if len(files) > max_backups:
                files_to_delete = files[max_backups:]
                for file_to_delete in files_to_delete:
                    sync_manager.service.files().delete(fileId=file_to_delete['id']).execute()
                    self.logger.info(f"已刪除舊備份: {file_to_delete['name']}")
        
        except Exception as e:
            self.logger.error(f"清理舊備份時發生錯誤: {str(e)}")
    
    def sync_once(self):
        """執行一次同步"""
        try:
            credentials_file = self.config['paths']['credentials_file']
            token_file = self.config['paths']['token_file']
            
            sync_manager = CursorSyncManager(credentials_file, token_file)
            
            # 檢查憑證檔案是否存在
            if not os.path.exists(credentials_file):
                self.logger.error(f"憑證檔案 {credentials_file} 不存在")
                return False
            
            # 認證
            sync_manager.authenticate()
            
            # 執行同步
            file_id = sync_manager.sync_up()
            
            # 清理舊備份
            self._cleanup_old_backups(sync_manager)
            
            self.logger.info("同步成功完成")
            
            if self.config['notification_settings']['success_notification']:
                self._send_notification("Cursor 同步", "設定已成功同步到 Google Drive")
            
            return True
            
        except Exception as e:
            self.logger.error(f"同步失敗: {str(e)}")
            
            if self.config['notification_settings']['error_notification']:
                self._send_notification("Cursor 同步錯誤", f"同步失敗: {str(e)}")
            
            return False
    
    def start_auto_sync(self):
        """開始自動同步"""
        if not self.config['sync_settings']['auto_sync']:
            self.logger.info("自動同步已關閉")
            return
        
        interval = self.config['sync_settings']['sync_interval_minutes'] * 60
        
        self.logger.info(f"開始自動同步，間隔: {interval/60} 分鐘")
        
        while True:
            try:
                self.sync_once()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.logger.info("自動同步已停止")
                break
            except Exception as e:
                self.logger.error(f"自動同步發生錯誤: {str(e)}")
                time.sleep(interval)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cursor 自動同步工具')
    parser.add_argument('--config', default='config.json',
                       help='設定檔路徑')
    parser.add_argument('--once', action='store_true',
                       help='只執行一次同步')
    
    args = parser.parse_args()
    
    auto_sync = AutoSyncManager(args.config)
    
    if args.once:
        auto_sync.sync_once()
    else:
        auto_sync.start_auto_sync()

if __name__ == '__main__':
    main()
