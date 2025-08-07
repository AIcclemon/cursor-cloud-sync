#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定腳本
協助用戶設定 Cursor 同步環境
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def install_requirements():
    """安裝所需的 Python 套件"""
    print("正在安裝所需套件...")
    try:
        # 檢查是否在虛擬環境中
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if in_venv:
            # 在虛擬環境中，不使用 --user 參數
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        else:
            # 不在虛擬環境中，使用 --user 參數
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', '-r', 'requirements.txt'])
        
        print("✓ 套件安裝完成")
        return True
    except subprocess.CalledProcessError:
        print("✗ 套件安裝失敗")
        return False

def setup_google_credentials():
    """設定 Google API 憑證"""
    print("\n設定 Google Drive API 憑證...")
    print("請按照以下步驟操作：")
    print("1. 前往 Google Cloud Console: https://console.cloud.google.com/")
    print("2. 建立新專案或選擇現有專案")
    print("3. 啟用 Google Drive API")
    print("4. 建立憑證 (OAuth 2.0 客戶端 ID)")
    print("5. 選擇應用程式類型為 '桌面應用程式'")
    print("6. 下載憑證檔案並重新命名為 'credentials.json'")
    print("7. 將 credentials.json 放在此專案目錄中")
    
    credentials_path = 'credentials.json'
    
    while not os.path.exists(credentials_path):
        input("\n按 Enter 鍵繼續檢查 credentials.json 是否存在...")
        if not os.path.exists(credentials_path):
            print(f"找不到 {credentials_path}，請確認檔案位置正確")
    
    print("✓ 找到憑證檔案")
    return True

def create_launchd_plist():
    """建立 macOS launchd 設定檔案"""
    print("\n建立自動同步設定...")
    
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
    
    print(f"✓ 已建立 launchd 設定檔: {plist_path}")
    
    # 詢問是否要啟用自動同步
    enable_auto = input("\n是否要啟用自動同步？(y/N): ").lower().strip()
    
    if enable_auto == 'y' or enable_auto == 'yes':
        try:
            subprocess.run(['launchctl', 'load', plist_path], check=True)
            print("✓ 自動同步已啟用")
            
            # 修改 config.json 中的 auto_sync 設定
            config_path = 'config.json'
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                config['sync_settings']['auto_sync'] = True
                
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print("✓ 已更新設定檔")
        except subprocess.CalledProcessError:
            print("✗ 啟用自動同步失敗")
    
    return True

def test_cursor_paths():
    """測試 Cursor 設定路徑"""
    print("\n檢查 Cursor 設定檔路徑...")
    
    from cursor_sync import CursorSyncManager
    
    sync_manager = CursorSyncManager()
    found_paths = []
    
    for name, path in sync_manager.cursor_config_paths.items():
        if os.path.exists(path):
            found_paths.append((name, path))
            print(f"✓ {name}: {path}")
        else:
            print(f"✗ {name}: {path} (不存在)")
    
    if found_paths:
        print(f"\n找到 {len(found_paths)} 個設定檔案/目錄")
        return True
    else:
        print("\n未找到 Cursor 設定檔案")
        print("請確認 Cursor 已安裝並至少執行過一次")
        return False

def main():
    print("Cursor Cloud Sync 安裝程式")
    print("=" * 40)
    
    # 檢查 Python 版本
    if sys.version_info < (3, 6):
        print("需要 Python 3.6 或更新版本")
        sys.exit(1)
    
    # 安裝套件
    if not install_requirements():
        sys.exit(1)
    
    # 設定 Google 憑證
    if not setup_google_credentials():
        sys.exit(1)
    
    # 測試 Cursor 路徑
    if not test_cursor_paths():
        print("\n警告: 未找到 Cursor 設定檔案")
        print("請確認 Cursor 已安裝並至少執行過一次")
    
    # 建立 launchd 設定
    if sys.platform == 'darwin':  # macOS
        create_launchd_plist()
    
    print("\n" + "=" * 40)
    print("設定完成！")
    print("\n使用方法:")
    print("1. 手動同步: python cursor_sync.py up")
    print("2. 下載設定: python cursor_sync.py down")
    print("3. 重新認證: python cursor_sync.py auth")
    print("4. 驗證路徑: python cursor_sync.py validate")
    print("5. 執行一次同步: python auto_sync.py --once")
    print("6. 開始自動同步: python auto_sync.py")
    
    print("\n注意事項:")
    print("- 首次使用需要進行 Google 認證")
    print("- 設定檔案會被打包上傳到 Google Drive")
    print("- 可以在 config.json 中調整同步設定")

if __name__ == '__main__':
    main()
