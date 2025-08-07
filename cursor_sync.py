#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor 設定同步工具
自動同步 Cursor 編輯器設定到 Google Drive
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
        """獲取 Cursor 設定檔路徑"""
        # 嘗試從配置檔案讀取自定義路徑
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    cursor_paths = config.get('cursor_paths', {})
                    
                    if cursor_paths.get('custom_enabled', False):
                        # 使用自定義路徑
                        custom_paths = {}
                        for key in ['settings', 'keybindings', 'snippets', 'extensions', 'workspaceStorage']:
                            path = cursor_paths.get(key)
                            if path:
                                custom_paths[key] = os.path.expanduser(path)
                        
                        if custom_paths:
                            return custom_paths
        except Exception as e:
            print(f"讀取配置檔案時發生錯誤: {e}")
        
        # 使用預設路徑（根據作業系統）
        return self._get_default_cursor_paths()
    
    def validate_paths(self):
        """驗證 Cursor 設定檔路徑"""
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
                
                # 檢查寫入權限
                if os.path.isfile(path):
                    validation_results[name]['writable'] = os.access(path, os.W_OK)
                elif os.path.isdir(path):
                    validation_results[name]['writable'] = os.access(path, os.W_OK)
                else:
                    # 檢查父目錄的寫入權限
                    parent_dir = os.path.dirname(path)
                    if os.path.exists(parent_dir):
                        validation_results[name]['writable'] = os.access(parent_dir, os.W_OK)
        
        return validation_results
    
    def print_path_validation(self):
        """打印路徑驗證結果"""
        validation_results = self.validate_paths()
        
        print("\n路徑驗證結果:")
        print("=" * 50)
        
        for name, result in validation_results.items():
            status = "✓" if result['exists'] else "✗"
            print(f"{status} {name}: {result['path']}")
            
            if result['exists']:
                type_str = "檔案" if result['is_file'] else "目錄" if result['is_dir'] else "未知"
                read_str = "可讀" if result['readable'] else "不可讀"
                write_str = "可寫" if result['writable'] else "不可寫"
                print(f"   類型: {type_str}, 權限: {read_str}, {write_str}")
            else:
                print(f"   狀態: 不存在")
            print()
        
        return validation_results
    
    def _get_default_cursor_paths(self):
        """獲取預設的 Cursor 設定檔路徑"""
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
            raise Exception(f"不支援的作業系統: {system}")
    
    def authenticate(self):
        """Google Drive API 認證"""
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
        """建立 Cursor 設定備份檔案"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'cursor_backup_{timestamp}.zip'
        
        # 使用 NamedTemporaryFile 而不是 TemporaryDirectory，避免檔案被自動刪除
        temp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
        backup_path = temp_file.name
        temp_file.close()  # 關閉檔案控制代碼，讓 zipfile 可以使用
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 備份設定檔
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
            
            # 添加元資料
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
        """獲取 Cursor 版本（如果可能）"""
        try:
            # 嘗試從設定檔中獲取版本資訊
            settings_path = self.cursor_config_paths.get('settings')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    return settings.get('version', 'unknown')
        except:
            pass
        return 'unknown'
    
    def upload_to_drive(self, file_path, custom_filename=None, folder_name='Cursor Backups'):
        """上傳備份檔案到 Google Drive"""
        if not self.service:
            raise Exception("請先進行 Google Drive 認證")
        
        # 查找或建立資料夾
        folder_id = self._get_or_create_folder(folder_name)
        
        # 上傳檔案 - 使用自定義檔名或原始檔名
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
        
        print(f"檔案已上傳到 Google Drive，ID: {file.get('id')}")
        return file.get('id')
    
    def _get_or_create_folder(self, folder_name):
        """獲取或建立 Google Drive 資料夾"""
        # 搜尋現有資料夾
        results = self.service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            return folders[0]['id']
        
        # 建立新資料夾
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = self.service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        
        print(f"已建立資料夾: {folder_name}")
        return folder.get('id')
    
    def download_latest_backup(self, folder_name='Cursor Backups'):
        """下載最新的備份檔案"""
        if not self.service:
            raise Exception("請先進行 Google Drive 認證")
        
        folder_id = self._get_or_create_folder(folder_name)
        
        # 搜尋備份檔案
        results = self.service.files().list(
            q=f"parents='{folder_id}' and name contains 'cursor_backup'",
            orderBy='createdTime desc',
            fields='files(id, name, createdTime)'
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            print("沒有找到備份檔案")
            return None
        
        latest_file = files[0]
        file_id = latest_file['id']
        filename = latest_file['name']
        
        # 下載檔案
        request = self.service.files().get_media(fileId=file_id)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            downloader = MediaIoBaseDownload(temp_file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"下載進度: {int(status.progress() * 100)}%")
            
            print(f"已下載: {filename}")
            return temp_file.name
    
    def restore_from_backup(self, backup_path):
        """從備份檔案恢復設定"""
        if not os.path.exists(backup_path):
            raise Exception(f"備份檔案不存在: {backup_path}")
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            with tempfile.TemporaryDirectory() as temp_dir:
                zipf.extractall(temp_dir)
                
                # 恢復各個設定檔
                for config_name, config_path in self.cursor_config_paths.items():
                    backup_config_path = os.path.join(temp_dir, config_name)
                    
                    if os.path.exists(backup_config_path):
                        # 備份當前設定
                        if os.path.exists(config_path):
                            backup_current = f"{config_path}.backup_{int(time.time())}"
                            if os.path.isfile(config_path):
                                shutil.copy2(config_path, backup_current)
                            else:
                                shutil.copytree(config_path, backup_current)
                        
                        # 恢復設定
                        if os.path.isfile(backup_config_path):
                            os.makedirs(os.path.dirname(config_path), exist_ok=True)
                            shutil.copy2(backup_config_path, config_path)
                        elif os.path.isdir(backup_config_path):
                            if os.path.exists(config_path):
                                shutil.rmtree(config_path)
                            shutil.copytree(backup_config_path, config_path)
                        
                        print(f"已恢復: {config_name}")
    
    def sync_up(self):
        """同步到雲端"""
        print("開始同步 Cursor 設定到 Google Drive...")
        
        # 建立備份檔案
        backup_path, backup_filename = self.create_backup_archive()
        print(f"已建立備份檔案: {backup_path}")
        
        # 上傳到 Google Drive （使用正確的檔名）
        file_id = self.upload_to_drive(backup_path, backup_filename)
        
        # 清理臨時檔案
        os.unlink(backup_path)
        
        print("同步完成！")
        return file_id
    
    def sync_down(self):
        """從雲端同步"""
        print("開始從 Google Drive 同步 Cursor 設定...")
        
        # 下載最新備份
        backup_path = self.download_latest_backup()
        
        if backup_path:
            # 恢復設定
            self.restore_from_backup(backup_path)
            
            # 清理臨時檔案
            os.unlink(backup_path)
            
            print("同步完成！")
        else:
            print("沒有找到備份檔案")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cursor 設定同步工具')
    parser.add_argument('action', choices=['up', 'down', 'auth', 'validate'], 
                       help='動作: up=上傳, down=下載, auth=認證, validate=驗證路徑')
    parser.add_argument('--credentials', default='credentials.json',
                       help='Google API 憑證檔案路徑')
    parser.add_argument('--token', default='token.json',
                       help='認證 token 檔案路徑')
    
    args = parser.parse_args()
    
    sync_manager = CursorSyncManager(
        os.path.abspath(args.credentials), 
        os.path.abspath(args.token),
        os.path.abspath('config.json')
    )
    
    if args.action == 'auth':
        if sync_manager.authenticate():
            print("認證成功！")
        else:
            print("認證失敗！")
    
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
