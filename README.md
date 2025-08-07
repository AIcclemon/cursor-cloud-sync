# Cursor Cloud Sync

自動同步 Cursor 編輯器設定到 Google Drive 的 Python 工具。

## 功能特點

- 🔄 自動同步 Cursor 設定到 Google Drive
- 📦 完整備份設定檔案、快捷鍵、代碼片段等
- 🔒 安全的 OAuth 2.0 認證
- 🕒 定期自動同步（可設定間隔）
- 🔔 macOS 系統通知支援
- 🗂️ 自動清理舊備份檔案
- 📱 跨平台支援 (macOS, Linux, Windows)

## 支援的設定檔案

- `settings.json` - 主要設定
- `keybindings.json` - 快捷鍵設定
- `snippets/` - 代碼片段
- `extensions/` - 擴充功能設定
- `workspaceStorage/` - 工作區設定

## 安裝

1. 確保您有 Python 3.6 或更新版本
2. 執行安裝腳本：

```bash
python setup.py
```

安裝腳本將會：
- 安裝所需的 Python 套件
- 引導您設定 Google Drive API 憑證
- 檢查 Cursor 設定檔路徑
- 設定自動同步 (macOS)

## Google Drive API 設定

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Drive API
4. 建立憑證 (OAuth 2.0 客戶端 ID)
5. 選擇應用程式類型為「桌面應用程式」
6. 下載憑證檔案並重新命名為 `credentials.json`
7. 將 `credentials.json` 放在專案目錄中

## 使用方法

### 基本命令

```bash
# 首次認證
python cursor_sync.py auth

# 上傳設定到 Google Drive
python cursor_sync.py up

# 從 Google Drive 下載設定
python cursor_sync.py down

# 驗證 Cursor 設定檔路徑
python cursor_sync.py validate
```

### 自動同步

```bash
# 執行一次同步
python auto_sync.py --once

# 開始自動同步 (持續執行)
python auto_sync.py
```

### 自定義設定

您可以修改 `config.json` 來自訂同步設定：

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

### 自定義 Cursor 路徑

如果您的 Cursor 設定檔案位於非標準位置，可以自定義路徑：

1. **啟用自定義路徑**: 將 `cursor_paths.custom_enabled` 設為 `true`
2. **設定路徑**: 在 `cursor_paths` 中指定各個檔案/目錄的路徑

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

## macOS 自動同步設定

對於 macOS 用戶，安裝腳本會自動建立 launchd 設定檔案，實現開機自動同步。

### 手動管理 launchd 服務

```bash
# 載入服務
launchctl load ~/Library/LaunchAgents/com.cursor.sync.plist

# 卸載服務
launchctl unload ~/Library/LaunchAgents/com.cursor.sync.plist

# 檢查服務狀態
launchctl list | grep cursor
```

## 故障排除

### 常見問題

1. **憑證檔案錯誤**
   - 確保 `credentials.json` 在專案目錄中
   - 檢查檔案格式是否正確

2. **找不到 Cursor 設定**
   - 確保 Cursor 已安裝並至少執行過一次
   - 檢查設定檔路徑是否正確

3. **同步失敗**
   - 檢查網路連接
   - 重新執行 `python cursor_sync.py auth`
   - 查看 `sync.log` 記錄檔

4. **路徑問題**
   - 執行 `python cursor_sync.py validate` 檢查路徑狀態
   - 確認 Cursor 設定檔案權限正確
   - 檢查自定義路徑配置是否正確

### 重設認證

如果遇到認證問題，可以刪除 `token.json` 檔案並重新認證：

```bash
rm token.json
python cursor_sync.py auth
```

## 檔案結構

```
cursor-cloud-sync/
├── cursor_sync.py          # 主要同步邏輯
├── auto_sync.py            # 自動同步腳本
├── setup.py                # 安裝設定腳本
├── config.json             # 設定檔案
├── requirements.txt        # Python 套件依賴
├── README.md              # 說明文件
├── credentials.json       # Google API 憑證 (需要自行添加)
├── token.json             # 認證 token (自動生成)
└── sync.log               # 同步記錄檔
```

## Security

- 不要將 `credentials.json` 和 `token.json` 提交到版本控制
- 定期檢查 Google Drive 中的備份檔案
- 建議定期更新 Google API 憑證

To report security vulnerabilities, please see our [Security Policy](SECURITY.md).

## 授權

此專案使用 MIT 授權。

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to:

- 🐛 [Report bugs](https://github.com/AIcclemon/cursor-cloud-sync/issues/new?template=bug_report.yml)
- 💡 [Request features](https://github.com/AIcclemon/cursor-cloud-sync/issues/new?template=feature_request.yml)
- ❓ [Ask questions](https://github.com/AIcclemon/cursor-cloud-sync/issues/new?template=question.yml)
- 🔧 Submit code changes

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## 更新日誌

### v1.0.0
- 初始版本
- 支援基本同步功能
- macOS 自動同步支援
- 系統通知整合
