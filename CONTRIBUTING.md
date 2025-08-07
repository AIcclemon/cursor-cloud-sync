# Contributing to Cursor Cloud Sync

感謝您對 Cursor Cloud Sync 的貢獻興趣！我們歡迎所有形式的貢獻，包括錯誤報告、功能建議、代碼改進和文檔更新。

## 📋 如何貢獻

### 🐛 報告 Bug

如果您發現了 bug，請：

1. 檢查 [Issues](https://github.com/AIcclemon/cursor-cloud-sync/issues) 確認問題尚未被報告
2. 創建新的 issue，包含：
   - 清楚的標題和描述
   - 重現步驟
   - 預期行為 vs 實際行為
   - 您的環境資訊（OS、Python 版本等）
   - 相關的錯誤訊息或截圖

### 💡 建議新功能

我們歡迎新功能建議！請：

1. 檢查 [Issues](https://github.com/AIcclemon/cursor-cloud-sync/issues) 確認建議尚未提出
2. 創建 feature request issue，說明：
   - 功能的詳細描述
   - 為什麼這個功能有用
   - 可能的實現方法

### 🔧 提交代碼

#### 開發環境設置

1. **Fork 本專案** 到您的 GitHub 帳戶
2. **Clone 您的 fork**：
   ```bash
   git clone https://github.com/your-username/cursor-cloud-sync.git
   cd cursor-cloud-sync
   ```
3. **建立開發環境**：
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或 venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
4. **建立分支**：
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### 代碼風格

- 使用 Python 3.6+ 語法
- 遵循 PEP 8 代碼風格
- 添加適當的註釋和文檔字符串
- 保持代碼簡潔易讀

#### 測試

在提交前請確保：

- 測試您的更改在不同作業系統上運作（如可能）
- 運行基本功能測試：
  ```bash
  python cursor_sync.py validate
  python cursor_sync.py --help
  python auto_sync.py --help
  ```
- 確保沒有破壞現有功能

#### 提交 Pull Request

1. **確保您的代碼是最新的**：
   ```bash
   git fetch upstream
   git rebase upstream/master
   ```
2. **推送到您的 fork**：
   ```bash
   git push origin feature/your-feature-name
   ```
3. **創建 Pull Request**，包含：
   - 清楚的標題和描述
   - 更改的詳細說明
   - 相關的 issue 編號（如果有）
   - 測試結果（如適用）

## 📝 文檔貢獻

文檔改進同樣重要！您可以：

- 修正 README.md 中的錯誤或不清楚的地方
- 添加使用範例
- 改進 API 文檔
- 翻譯文檔到其他語言

## 🎯 開發重點

我們特別歡迎在以下領域的貢獻：

- **跨平台兼容性**：改進對不同作業系統的支援
- **錯誤處理**：更好的錯誤訊息和恢復機制
- **效能優化**：減少同步時間和資源使用
- **用戶體驗**：更好的 CLI 界面和回饋
- **測試覆蓋**：添加單元測試和整合測試
- **文檔**：使用指南、故障排除、FAQ

## 🚫 不接受的貢獻

- 破壞現有 API 的更改（除非有充分理由）
- 添加不必要的依賴
- 沒有遵循項目風格的代碼
- 缺乏適當測試的功能更改

## 📞 需要幫助？

如果您有任何問題或需要幫助：

- 創建 [Discussion](https://github.com/AIcclemon/cursor-cloud-sync/discussions)
- 在相關 issue 中留言
- 查看現有的 [Issues](https://github.com/AIcclemon/cursor-cloud-sync/issues) 和 [Pull Requests](https://github.com/AIcclemon/cursor-cloud-sync/pulls)

## 📜 授權

通過向本專案貢獻，您同意您的貢獻將使用與本專案相同的 [MIT License](LICENSE) 授權。

## 🙏 致謝

感謝所有貢獻者幫助改進 Cursor Cloud Sync！

---

**記住**：每個貢獻都很重要，無論大小。我們重視您的時間和努力！