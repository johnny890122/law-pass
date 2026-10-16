# Tasks: 多法律支持功能實作

## Overview
本任務清單實作多法律類型支持功能，使系統能夠處理專利法、商標法、著作權法等多種法律。所有現有專利法數據將遷移為 `type="patent-act"`，並確保系統邏輯正確過濾法律類型。

---

## Phase 1: 數據模型與遷移 (Data Model & Migration)

### Task 1.1: 更新數據模型定義
**File**: [`db/models.py`](../db/models.py)

- [ ] 在 `LawModel` 中添加 `type: str = "patent-act"` 欄位
- [ ] 在 `I18nMappingModel` 中添加 `type: str` 欄位
- [ ] 添加 `LAW_TYPES` 常量定義支持的法律類型
- [ ] 更新 `init_db()` 方法，添加新的索引：
  - [ ] `laws.create_index("type")`
  - [ ] `laws.create_index([("type", 1), ("lang", 1)])`
  - [ ] `laws.create_index([("type", 1), ("article_number_int", 1)])`
  - [ ] `i18n_mapping.create_index([("type", 1), ("article_number", 1)])`

**Validation**:
- 執行 `python -c "from db.models import LawModel; import dataclasses; print(dataclasses.fields(LawModel))"` 確認新欄位存在
- 確認 `type` 欄位有預設值 `"patent-act"`

---

### Task 1.2: 建立數據遷移腳本
**File**: `scripts/migrate_add_law_type.py` (新建)

- [ ] 建立遷移腳本檔案
- [ ] 實作 `migrate_laws_add_type()` 函數：
  - [ ] 查找所有沒有 `type` 欄位的 law 文檔
  - [ ] 批量更新為 `type="patent-act"`
  - [ ] 記錄更新數量並輸出
- [ ] 實作 `migrate_i18n_mapping_add_type()` 函數：
  - [ ] 查找所有沒有 `type` 欄位的 i18n_mapping 文檔
  - [ ] 批量更新為 `type="patent-act"`
  - [ ] 記錄更新數量並輸出
- [ ] 實作 `create_new_indexes()` 函數：
  - [ ] 建立上述所有新索引
  - [ ] 處理索引已存在的情況
- [ ] 實作 `validate_migration()` 函數：
  - [ ] 驗證所有 laws 都有 `type` 欄位
  - [ ] 驗證所有 i18n_mappings 都有 `type` 欄位
  - [ ] 統計各 type 的文檔數量
- [ ] 實作 `rollback_migration()` 函數（備用）：
  - [ ] 移除所有 `type` 欄位
  - [ ] 清除相關索引
- [ ] 添加主函數和 CLI 參數處理
- [ ] 添加詳細的日誌輸出

**Validation**:
- 在本地測試數據庫執行遷移
- 驗證遷移是冪等的（可以多次執行）
- 確認 rollback 功能正常運作
- 執行後確認 `db.laws.find({"type": {"$exists": false}}).count() == 0`

---

### Task 1.3: 執行數據遷移
**執行步驟**:

- [ ] 在本地環境先測試遷移：
  ```bash
  python scripts/migrate_add_law_type.py --dry-run
  ```
- [ ] 確認 dry-run 結果正確後執行實際遷移：
  ```bash
  python scripts/migrate_add_law_type.py --execute
  ```
- [ ] 驗證遷移結果：
  ```bash
  python scripts/migrate_add_law_type.py --validate
  ```
- [ ] 記錄遷移結果（更新的文檔數量）
- [ ] 備份當前數據庫狀態（在生產環境執行前）

**Production Migration**:
- [ ] 在 staging 環境測試完整流程
- [ ] 建立生產數據庫備份
- [ ] 在維護時段執行生產遷移
- [ ] 驗證生產環境遷移結果
- [ ] 監控遷移後系統運行狀態

---

## Phase 2: 核心服務層更新 (Core Services)

### Task 2.1: 更新認證服務添加法律類型管理
**File**: [`services/auth.py`](../services/auth.py)

- [ ] 添加 `LAW_TYPES` 常量導入
- [ ] 實作 `get_current_law_type() -> str` 函數：
  - [ ] 從 Flask session 獲取 `current_law_type`
  - [ ] 如果不存在，返回預設值 `"patent-act"`
- [ ] 實作 `set_current_law_type(law_type: str) -> bool` 函數：
  - [ ] 驗證 law_type 在 LAW_TYPES 中
  - [ ] 如果有效，儲存到 session
  - [ ] 返回操作結果
- [ ] 實作 `get_available_law_types() -> List[Dict]` 函數：
  - [ ] 查詢每個法律類型的法條數量
  - [ ] 返回格式：`[{type, name_zh, name_en, count_zh_tw, count_en}]`
- [ ] 添加單元測試

**Validation**:
- 測試 session 中有/無 law_type 的情況
- 測試無效 law_type 的處理
- 驗證預設值返回正確

---

### Task 2.2: 更新題目庫存服務
**File**: [`services/inventory.py`](../services/inventory.py)

- [ ] 在 `count_available_questions()` 方法添加 `law_type` 參數：
  - [ ] 參數預設值為 `None`（從 session 獲取）
  - [ ] 如果為 `None`，調用 `get_current_law_type()`
- [ ] 更新查詢邏輯，添加法律類型過濾：
  - [ ] 在獲取 laws 時添加 `{"type": law_type}` 過濾
  - [ ] 確保只計算該法律類型的題目
- [ ] 在 `get_questions_for_session()` 方法添加相同的過濾邏輯
- [ ] **移除** `trigger_generation()` 及所有非同步/背景出題邏輯 — 出題由管理員腳本負責，使用者不能觸發
- [ ] 更新所有相關的輔助方法

**Validation**:
- 測試只返回指定 law_type 的題目
- 測試不同 law_type 之間的題目完全隔離
- 驗證題目計數正確

---

### Task 2.3: 更新題目生成服務
**File**: [`services/question_gen.py`](../services/question_gen.py)

- [ ] 在生成題目前驗證 law_id 的法律類型：
  - [ ] 查詢 law 文檔
  - [ ] 確認其 `type` 欄位與當前 law_type 匹配
  - [ ] 如果不匹配，拋出 `ValueError`
- [ ] 在獲取最近題目時添加 law_type 過濾（通過 law_id 關聯）
- [ ] 確保生成的題目只參考同一法律類型的法條

**Validation**:
- 測試不能為錯誤的 law_type 生成題目
- 驗證題目去重邏輯在法律類型內正常運作

---

## Phase 3: API 路由更新 (API Routes)

### Task 3.1: 添加法律類型管理 API
**File**: `routes/law_types.py` (新建)

- [ ] 建立新的 Blueprint: `law_types_bp`
- [ ] 實作 `GET /api/law-types` 端點：
  - [ ] 調用 `get_available_law_types()`
  - [ ] 返回所有可用的法律類型及統計
  - [ ] 需要登入驗證 `@login_required`
- [ ] 實作 `GET /api/law-types/current` 端點：
  - [ ] 返回當前 session 中的 law_type
  - [ ] 返回格式：`{type, name_zh, name_en}`
- [ ] 實作 `POST /api/law-types/select` 端點：
  - [ ] 接收 `law_type` 參數
  - [ ] 調用 `set_current_law_type(law_type)`
  - [ ] 返回操作結果和新的 law_type
- [ ] 添加錯誤處理和輸入驗證
- [ ] 在 [`app.py`](../app.py) 中註冊新的 Blueprint

**Validation**:
- 測試獲取法律類型列表
- 測試切換法律類型
- 測試無效法律類型的錯誤處理
- 驗證需要登入才能訪問

---

### Task 3.2: 更新法條 API 路由
**File**: [`routes/laws.py`](../routes/laws.py)

- [ ] 在 `get_laws()` 函數開頭添加：
  ```python
  law_type = request.args.get('law_type') or get_current_law_type()
  query_filter['type'] = law_type
  ```
- [ ] 在 `get_law_detail()` 函數中驗證法條類型：
  - [ ] 獲取 law 文檔
  - [ ] 檢查其 `type` 是否與當前 law_type 匹配
  - [ ] 如果不匹配，返回 403 錯誤
- [ ] 在 `toggle_law_star()` 函數中添加類型驗證
- [ ] 在 `get_law_chapters()` 函數中添加 law_type 過濾
- [ ] 在 `get_law_questions()` 函數中：
  - [ ] 驗證 law 的類型
  - [ ] 確保只返回該法律類型的題目
- [ ] 更新所有相關統計查詢，添加 law_type 過濾

**Validation**:
- 測試法條列表只顯示指定類型
- 測試訪問錯誤類型的法條返回 403
- 測試統計數據按法律類型正確隔離

---

### Task 3.3: 更新測驗 API 路由
**File**: [`routes/quiz.py`](../routes/quiz.py)

- [ ] 在 `check_available_questions()` 端點添加：
  - [ ] 從參數或 session 獲取 `law_type`
  - [ ] 傳遞給 `count_available_questions()`
- [ ] 在 `create_quiz_session()` 端點添加：
  - [ ] 從參數或 session 獲取 `law_type`
  - [ ] 傳遞給 `get_questions_for_session()`
  - [ ] 在 session 記錄中儲存 `law_type`
  - [ ] 若可用題目 `< n`，直接回傳 400 錯誤："題目數量不足，請聯繫管理員生成更多題目。"
- [ ] **移除** 所有背景/非同步出題觸發邏輯
- [ ] 確保所有題目查詢都經過 law 的類型過濾

**Validation**:
- 測試測驗只包含指定法律類型的題目
- 測試背景生成只為當前法律類型生成題目
- 驗證不同法律類型的進度完全獨立

---

### Task 3.4: 更新前端路由
**File**: [`routes/frontend.py`](../routes/frontend.py)

- [ ] 在 `dashboard()` 函數中：
  - [ ] 獲取當前 law_type
  - [ ] 篩選該類型的法條 IDs
  - [ ] 統計數據只計算該法律類型
  - [ ] 傳遞 law_type 到模板
- [ ] 在 `laws_page()` 函數中傳遞當前 law_type
- [ ] 在 `law_detail_page()` 函數中驗證法條類型

**Validation**:
- 測試儀表板統計按法律類型正確顯示
- 測試切換法律類型後數據更新

---

## Phase 4: 前端界面更新 (Frontend UI)

### Task 4.1: 添加法律類型選擇器組件
**Files**: 
- [`templates/base.html`](../templates/base.html)
- [`static/js/main.js`](../static/js/main.js)

- [ ] 在導航欄添加法律類型下拉選單：
  - [ ] 顯示當前選中的法律類型
  - [ ] 列出所有可用的法律類型
  - [ ] 每個選項顯示中文名稱和法條數量
- [ ] 實作 JavaScript 切換邏輯：
  - [ ] 調用 `POST /api/law-types/select`
  - [ ] 成功後重新加載頁面或更新數據
  - [ ] 顯示切換成功的提示訊息
- [ ] 添加 CSS 樣式使其美觀並響應式

**Validation**:
- 測試在各個頁面都能看到選擇器
- 測試選擇器切換後頁面數據更新
- 測試移動端顯示正常

---

### Task 4.2: 更新法條瀏覽頁面
**File**: [`templates/laws.html`](../templates/laws.html)

- [ ] 顯示當前選中的法律類型名稱
- [ ] 添加法律類型篩選提示文字
- [ ] 確保搜尋功能在當前法律類型內進行
- [ ] 更新空狀態提示（如果該法律類型沒有法條）

**Validation**:
- 測試只顯示當前法律類型的法條
- 測試搜尋在正確的範圍內

---

### Task 4.3: 更新儀表板頁面
**File**: [`templates/dashboard.html`](../templates/dashboard.html)

- [ ] 顯示當前學習的法律類型
- [ ] 添加明顯的法律類型標識
- [ ] 統計數據標註為當前法律類型的進度
- [ ] 提示用戶可以在導航欄切換法律類型

**Validation**:
- 測試儀表板顯示正確的法律類型
- 測試統計數據正確

---

### Task 4.4: 更新測驗配置頁面
**File**: [`templates/quiz_config.html`](../templates/quiz_config.html)

- [ ] 顯示將為哪個法律類型生成題目
- [ ] 添加法律類型標籤或提示
- [ ] 確保可用題目數量查詢包含 law_type

**Validation**:
- 測試配置頁面顯示正確的法律類型
- 測試可用題目數量計算正確

---

### Task 4.5: 更新樣式設計
**File**: [`static/css/style.css`](../static/css/style.css)

- [ ] 添加法律類型選擇器的樣式
- [ ] 為不同法律類型設計不同的主題色（可選）
- [ ] 添加法律類型標籤 badge 樣式
- [ ] 確保所有新組件響應式設計

**Validation**:
- 測試在不同螢幕尺寸下顯示正常
- 測試深色/淺色模式兼容（如果有）

---

## Phase 5: 初始化與管理腳本 (Initialization Scripts)

### Task 5.1: 更新現有初始化腳本
**Files**: 
- [`scripts/init_db.py`](../scripts/init_db.py)
- [`scripts/init_remote_laws.py`](../scripts/init_remote_laws.py)

- [ ] 確保插入法條時包含 `type="patent-act"`
- [ ] 更新 i18n mapping 插入邏輯包含 `type`
- [ ] 驗證腳本執行後數據格式正確

**Validation**:
- 在乾淨的數據庫執行初始化
- 確認所有法條都有 type 欄位

---

### Task 5.2: 建立新法律類型初始化範本
**File**: `scripts/init_new_law_type_template.py` (新建)

- [ ] 建立範本腳本，包含：
  - [ ] 法律類型參數配置
  - [ ] 中英文法條解析與插入
  - [ ] i18n mapping 建立
  - [ ] 索引驗證
  - [ ] 數據驗證
- [ ] 添加詳細的使用說明註解
- [ ] 建立對應的 README 文檔

**Validation**:
- 使用範本建立測試法律類型
- 驗證所有數據結構正確

---

## Phase 6: 測試覆蓋 (Testing Coverage)

### Task 6.1: 單元測試
**File**: `test/test_multi_law_support.py` (新建)

- [ ] 測試數據模型：
  - [ ] LawModel 預設 type 值
  - [ ] I18nMappingModel type 欄位
- [ ] 測試 auth service：
  - [ ] `get_current_law_type()` 各種情況
  - [ ] `set_current_law_type()` 驗證邏輯
  - [ ] `get_available_law_types()` 返回格式
- [ ] 測試 inventory service：
  - [ ] 法律類型過濾邏輯
  - [ ] 題目計數按類型隔離
- [ ] 執行測試：`pytest test/test_multi_law_support.py -v`

---

### Task 6.2: 整合測試
**File**: `test/test_multi_law_integration.py` (新建)

- [ ] 測試完整流程：
  - [ ] 初始化兩種法律類型
  - [ ] 切換法律類型
  - [ ] 驗證法條列表過濾
  - [ ] 驗證題目生成隔離
  - [ ] 驗證統計數據隔離
- [ ] 測試 API 端點：
  - [ ] 法律類型管理 API
  - [ ] 法條 API 過濾
  - [ ] 測驗 API 過濾
- [ ] 執行測試：`pytest test/test_multi_law_integration.py -v`

---

### Task 6.3: 遷移測試
**File**: `test/test_migration_law_type.py` (新建)

- [ ] 測試遷移腳本：
  - [ ] 在測試數據庫執行遷移
  - [ ] 驗證所有文檔更新
  - [ ] 測試冪等性（多次執行）
  - [ ] 測試 rollback 功能
- [ ] 測試數據完整性：
  - [ ] 驗證沒有孤兒題目
  - [ ] 驗證 i18n mapping 完整
- [ ] 執行測試：`pytest test/test_migration_law_type.py -v`

---

### Task 6.4: E2E 測試
**File**: [`test/test_integration_e2e.py`](../test/test_integration_e2e.py) (更新)

- [ ] 添加多法律支持的 E2E 測試場景：
  - [ ] 用戶登入後選擇法律類型
  - [ ] 瀏覽該法律類型的法條
  - [ ] 開始該法律類型的測驗
  - [ ] 切換到另一個法律類型
  - [ ] 驗證數據完全隔離
- [ ] 執行測試：`pytest test/test_integration_e2e.py -v`

---

## Phase 7: 文檔與部署 (Documentation & Deployment)

### Task 7.1: 更新技術文檔
**Files**:
- [`README.md`](../README.md)
- `docs/MULTI_LAW_GUIDE.md` (新建)

- [ ] 更新 README：
  - [ ] 添加多法律支持說明
  - [ ] 更新功能列表
  - [ ] 更新架構圖
- [ ] 建立多法律支持指南：
  - [ ] 架構說明
  - [ ] 數據遷移步驟
  - [ ] 如何添加新法律類型
  - [ ] 故障排除指南

---

### Task 7.2: 建立遷移執行計劃
**File**: `docs/MIGRATION_PLAN_LAW_TYPE.md` (新建)

- [ ] 撰寫遷移計劃：
  - [ ] Pre-flight 檢查清單
  - [ ] 備份策略
  - [ ] 執行步驟
  - [ ] 驗證檢查點
  - [ ] Rollback 程序
  - [ ] 監控指標
- [ ] 建立遷移時間表
- [ ] 準備回報模板

---

### Task 7.3: 準備部署
**Checklist**:

- [ ] 在 staging 環境完整測試
- [ ] 驗證所有測試通過
- [ ] 準備數據庫備份腳本
- [ ] 準備監控告警
- [ ] 通知團隊成員遷移計劃
- [ ] 準備緊急回滾計劃

---

### Task 7.4: 執行生產部署
**Steps**:

- [ ] 建立生產數據庫完整備份
- [ ] 在維護時段執行遷移：
  1. [ ] 停止影響數據的服務（可選）
  2. [ ] 執行 `migrate_add_law_type.py --execute`
  3. [ ] 驗證遷移結果
  4. [ ] 部署新版本程式碼
  5. [ ] 驗證系統功能正常
  6. [ ] 監控錯誤日誌
- [ ] 執行煙霧測試（smoke test）
- [ ] 記錄部署結果

---

### Task 7.5: 監控與驗證
**Post-deployment**:

- [ ] 監控系統 24-48 小時
- [ ] 檢查錯誤日誌無異常
- [ ] 驗證用戶回饋
- [ ] 性能指標對比
- [ ] 記錄遇到的問題與解決方案

---

## Phase 8: 未來增強 (Future Enhancements)

### Task 8.1: 權限控制（可選）
- [ ] 設計用戶法律類型權限系統
- [ ] 實作權限檢查中間件
- [ ] 添加管理界面分配權限

### Task 8.2: 批量操作工具
- [ ] 建立法律類型批量管理工具
- [ ] 實作法律類型匯出/匯入功能
- [ ] 建立數據驗證工具

### Task 8.3: 性能優化
- [ ] 實作法律類型元數據緩存
- [ ] 優化跨法律類型的查詢
- [ ] 添加查詢性能監控

---

## 完成檢查清單 (Completion Checklist)

### 代碼質量
- [ ] 所有代碼通過 lint 檢查
- [ ] 所有測試通過（單元、整合、E2E）
- [ ] 代碼覆蓋率 > 80%
- [ ] 無重大技術債務

### 功能完整性
- [ ] 所有現有功能正常運作
- [ ] 法律類型切換功能完整
- [ ] 數據完全隔離無洩漏
- [ ] 用戶體驗流暢

### 數據完整性
- [ ] 所有現有數據遷移成功
- [ ] 無數據丟失
- [ ] 無孤兒記錄
- [ ] i18n mapping 完整

### 文檔完整性
- [ ] 技術文檔完整
- [ ] API 文檔更新
- [ ] 遷移文檔完整
- [ ] 故障排除指南完整

### 部署準備
- [ ] Staging 環境驗證通過
- [ ] 備份策略已測試
- [ ] Rollback 程序已驗證
- [ ] 監控告警已設置

---

## 風險與緩解策略

### 風險 1: 數據遷移失敗
**緩解**:
- 在測試環境多次演練
- 準備詳細的 rollback 腳本
- 遷移前完整備份

### 風險 2: 性能下降
**緩解**:
- 建立適當的索引
- 性能測試與基準對比
- 監控查詢執行時間

### 風險 3: 現有功能破壞
**緩解**:
- 完整的回歸測試
- 漸進式部署
- 特性開關控制

### 風險 4: 用戶體驗混亂
**緩解**:
- 清晰的 UI 指示
- 預設為專利法（現有用戶無感知）
- 提供使用指南

---

## 預估時間

- **Phase 1**: 數據模型與遷移 - 2-3 天
- **Phase 2**: 核心服務層更新 - 2-3 天
- **Phase 3**: API 路由更新 - 3-4 天
- **Phase 4**: 前端界面更新 - 2-3 天
- **Phase 5**: 初始化與管理腳本 - 1-2 天
- **Phase 6**: 測試覆蓋 - 3-4 天
- **Phase 7**: 文檔與部署 - 2-3 天
- **Phase 8**: 未來增強 - 依需求

**總計**: 約 15-22 個工作天

---

## 注意事項

1. **向後兼容**: 所有變更必須確保現有專利法功能完全正常
2. **數據安全**: 任何數據庫操作前必須備份
3. **測試優先**: 先寫測試再實作功能
4. **漸進部署**: 可以先部署後端，再部署前端
5. **監控重點**: 重點監控查詢性能和錯誤率
6. **用戶溝通**: 重大更新前通知用戶

---

## Phase 9: 專利審查基準支持 (Patent Examination Guidelines Support)

### Task 9.1: 更新 LAW_TYPES 常量
**File**: [`db/models.py`](../db/models.py)

- [x] 在 `LAW_TYPES` 字典中添加 `"patent-examination"` 定義：
  ```python
  "patent-examination": {
      "name_zh": "專利審查基準",
      "name_en": "Patent Examination Guidelines",
      "code": "patent-examination"
  }
  ```

**Validation**:
- 確認常量定義正確
- 驗證系統能識別新的法律類型

---

### Task 9.2: 建立審查基準初始化腳本
**File**: `scripts/init_examination_guidelines.py` (新建)

- [ ] 建立初始化腳本檔案
- [ ] 實作主要功能：
  - [ ] 使用 `glob` 掃描 `knowledge/examination/*/*.json` 所有 JSON 檔案
  - [ ] 逐一讀取並解析 JSON 內容
  - [ ] 為每個條文設定 `type = "patent-examination"`
  - [ ] 確保 `lang = "zh-TW"` 欄位存在
  - [ ] 使用 `LawModel` 驗證資料結構
  - [ ] 使用複合鍵 `(article_number, lang, type)` 進行 upsert
  - [ ] 統計插入和更新數量
- [ ] 添加命令列參數支持：
  - [ ] `--local`: 插入到本地資料庫
  - [ ] `--remote`: 插入到遠端資料庫
  - [ ] `--both`: 同時插入到兩個資料庫
  - [ ] `--dry-run`: 測試模式，不實際寫入
- [ ] 添加詳細的日誌輸出
- [ ] 添加錯誤處理（檔案不存在、JSON 格式錯誤等）

**Validation**:
- 在本地測試資料庫執行腳本
- 驗證所有 54 個 JSON 檔案都被正確處理
- 確認資料庫中的法條有正確的 `type` 和 `lang` 欄位
- 執行 `db.laws.find({type: "patent-examination"}).count()` 驗證總數

---

### Task 9.3: 測試審查基準資料
**File**: `test/test_examination_guidelines.py` (新建)

- [ ] 建立測試檔案
- [ ] 測試資料載入：
  - [ ] 驗證所有審查基準條文正確插入
  - [ ] 檢查資料結構完整性
  - [ ] 確認 `type = "patent-examination"`
  - [ ] 確認章節層級正確
- [ ] 測試查詢功能：
  - [ ] 依法律類型過濾查詢
  - [ ] 依章節過濾查詢
  - [ ] 搜尋功能測試
  - [ ] 排序功能測試（使用 article_number_int）
- [ ] 執行測試：`pytest test/test_examination_guidelines.py -v`

---

### Task 9.4: 驗證與現有系統整合
**Checklist**:

- [ ] 驗證審查基準條文可在法條瀏覽頁面顯示
- [ ] 測試法律類型切換器能正確切換到審查基準
- [ ] 確認審查基準條文可以生成題目
- [ ] 驗證進度追蹤在審查基準下正常運作
- [ ] 測試搜尋功能在審查基準範圍內正確運作
- [ ] 確認統計數據按法律類型正確隔離

---

### Task 9.5: 更新文檔
**Files**:
- [`README.md`](../README.md)
- `docs/EXAMINATION_GUIDELINES_SETUP.md` (新建)

- [ ] 更新 README：
  - [ ] 在支援的法律類型列表中添加審查基準
  - [ ] 更新功能說明
- [ ] 建立審查基準設定指南：
  - [ ] 資料來源說明
  - [ ] 初始化步驟
  - [ ] 資料結構說明
  - [ ] 常見問題處理

---

### Task 9.6: 執行生產部署（可選）
**Steps**:

- [ ] 在 staging 環境測試審查基準初始化
- [ ] 建立生產資料庫備份
- [ ] 執行 `init_examination_guidelines.py --remote`
- [ ] 驗證生產環境資料正確
- [ ] 監控系統運行狀態
- [ ] 記錄部署結果

---

## Phase 10: 訴願法支持 (Administrative Appeal Act Support)

### Task 10.1: 更新 LAW_TYPES 常量
**File**: [`db/models.py`](../db/models.py)

- [ ] 在 `LAW_TYPES` 字典中添加 `"administrative-appeal"` 定義：
  ```python
  "administrative-appeal": {
      "name_zh": "訴願法",
      "name_en": "Administrative Appeal Act",
      "code": "administrative-appeal"
  }
  ```

**Validation**:
- 確認常量定義正確
- 驗證系統能識別新的法律類型

---

### Task 10.2: 建立訴願法解析腳本
**File**: `scripts/parse_administrative_appeal.py` (新建)

- [ ] 建立解析腳本檔案
- [ ] 實作主要解析函數 `parse_administrative_appeal_md()`:
  - [ ] 讀取 markdown 文件 (`knowledge/administrative_appeal_zh.md`)
  - [ ] 識別章標題（前綴3個空格 + "第 X 章"）
  - [ ] 識別節標題（前綴6個空格 + "第 X 節"）
  - [ ] 識別條號（"第 X 條"）
  - [ ] 提取條文內容（處理多段落，移除數字前綴如 "1   ", "2   "）
  - [ ] 生成 `article_number_int` 用於排序（從條號提取數字）
  - [ ] 組合完整章節路徑（章 + 節，如 "第一章 總則 / 第一節 訴願事件"）
- [ ] 實作輔助函數:
  - [ ] `extract_article_number()`: 從條號提取數字
  - [ ] `format_chapter_path()`: 格式化章節完整路徑
- [ ] 添加錯誤處理（文件不存在、格式錯誤等）
- [ ] 添加命令列支持 `--test` 參數用於測試
- [ ] 添加詳細日誌輸出

**Validation**:
- 解析完成後應有 101 條法條
- 驗證章節結構正確（5章）
- 確認條文內容完整無遺漏
- 抽查前10條、中10條、後10條內容正確性
- 運行: `python scripts/parse_administrative_appeal.py --test`

---

### Task 10.3: 建立訴願法初始化腳本
**File**: `scripts/init_administrative_appeal.py` (新建)

- [ ] 建立初始化腳本檔案
- [ ] 實作主要功能：
  - [ ] 調用解析函數獲取法條資料
  - [ ] 為每個條文設定 `type = "administrative-appeal"`
  - [ ] 確保 `lang = "zh-TW"` 欄位存在
  - [ ] 使用 `LawModel` 驗證資料結構
  - [ ] 使用複合鍵 `(article_number, lang, type)` 進行 upsert
  - [ ] 統計插入和更新數量
  - [ ] 輸出詳細的操作結果
- [ ] 添加命令列參數支持：
  - [ ] `--target`: 選擇資料庫 (local/remote/both)
  - [ ] `--dry-run`: 測試模式，不實際寫入
  - [ ] `--verbose`: 詳細輸出模式
- [ ] 添加詳細的日誌輸出
- [ ] 添加錯誤處理和記錄機制

**Validation**:
- 在本地測試資料庫執行腳本
- 驗證所有 101 條法條都被正確插入
- 確認資料庫中的法條有正確的 `type` 和 `lang` 欄位
- 執行 `db.laws.find({type: "administrative-appeal"}).count()` 驗證總數為 101
- 檢查章節分布是否正確

---

### Task 10.4: 建立訴願法驗證腳本
**File**: `scripts/verify_administrative_appeal.py` (新建)

- [ ] 建立驗證腳本檔案
- [ ] 實作驗證功能：
  - [ ] 驗證條文總數 (應為 101 條)
  - [ ] 驗證章節分布 (應有 5 章)
  - [ ] 檢查必要欄位完整性 (article_number, article_number_int, content, chapter, type, lang)
  - [ ] 驗證 `article_number_int` 範圍 (1-101)
  - [ ] 檢查內容不為空
  - [ ] 統計各章條文數量
  - [ ] 驗證所有條文 `type = "administrative-appeal"`
- [ ] 生成詳細的驗證報告
- [ ] 如有問題，輸出具體錯誤資訊和問題條文列表
- [ ] 添加命令列參數 `--target` 支持

**Validation**:
- 執行驗證腳本應通過所有檢查
- 運行: `python scripts/verify_administrative_appeal.py`
- 確認輸出報告清晰易讀

---

### Task 10.5: 測試訴願法資料整合
**File**: `test/test_administrative_appeal.py` (新建)

- [ ] 建立測試檔案
- [ ] 測試解析功能：
  - [ ] 測試 markdown 解析正確性
  - [ ] 測試章節識別（3空格章、6空格節）
  - [ ] 測試條文內容提取（移除數字標記）
  - [ ] 測試 `article_number_int` 生成
  - [ ] 測試章節路徑格式化
- [ ] 測試資料載入：
  - [ ] 驗證所有訴願法條文正確插入
  - [ ] 檢查資料結構完整性
  - [ ] 確認 `type = "administrative-appeal"`
  - [ ] 確認章節層級正確
  - [ ] 驗證條文數量 = 101
- [ ] 測試查詢功能：
  - [ ] 依法律類型過濾查詢
  - [ ] 依章節過濾查詢
  - [ ] 搜尋功能測試（搜尋"訴願"、"行政處分"等關鍵字）
  - [ ] 排序功能測試（使用 article_number_int）
- [ ] 執行測試：`pytest test/test_administrative_appeal.py -v`

---

### Task 10.6: 驗證與現有系統整合
**Checklist**:

- [ ] 驗證訴願法條文可在法條瀏覽頁面顯示
- [ ] 測試法律類型切換器能正確切換到訴願法
- [ ] 確認訴願法下拉選項顯示 "訴願法 (101)"
- [ ] 確認訴願法條文可以生成題目
- [ ] 驗證進度追蹤在訴願法下正常運作
- [ ] 測試搜尋功能在訴願法範圍內正確運作
- [ ] 確認統計數據按法律類型正確隔離
- [ ] 驗證章節過濾功能正常（5個章節）
- [ ] 測試法條詳情頁面顯示正確
- [ ] 測試星標功能在訴願法下正常
- [ ] 驗證訴願法與其他法律類型完全隔離

---

### Task 10.7: 更新文檔
**Files**:
- [`README.md`](../README.md)
- [`docs/requirements.md`](requirements.md)
- [`docs/design.md`](design.md)

- [ ] 更新 README：
  - [ ] 在支援的法律類型列表中添加訴願法
  - [ ] 更新功能說明
  - [ ] 添加訴願法初始化指令範例
  - [ ] 更新系統截圖（如有）
- [ ] 確認 requirements.md 已更新（已完成）
- [ ] 確認 design.md 已更新（已完成）
- [ ] 建立或更新 CHANGELOG（記錄訴願法新增）

---

### Task 10.8: 執行生產部署（可選）
**Steps**:

- [ ] 在 staging 環境測試訴願法初始化
- [ ] 建立生產資料庫備份
- [ ] 執行 `python scripts/init_administrative_appeal.py --target remote`
- [ ] 執行驗證: `python scripts/verify_administrative_appeal.py --target remote`
- [ ] 驗證生產環境資料正確
- [ ] 測試生產環境法律類型切換正常
- [ ] 監控系統運行狀態
- [ ] 記錄部署結果和時間
- [ ] 通知團隊成員新法律類型可用

---

### 完成檢查清單 (Administrative Appeal Completion Checklist)

#### 資料完整性
- [ ] 所有 101 條訴願法條文成功載入
- [ ] 訴願法條文總數正確 (101 條)
- [ ] 所有條文有正確的 `type = "administrative-appeal"`
- [ ] 章節層級結構完整 (5章)
- [ ] 所有條文內容不為空
- [ ] article_number_int 範圍正確 (1-101)

#### 功能完整性
- [ ] 法律類型選擇器包含訴願法
- [ ] 可切換到訴願法並正確顯示101條條文
- [ ] 搜尋功能在訴願法範圍內正常
- [ ] 可為訴願法條文生成題目
- [ ] 進度追蹤與訴願法正確關聯
- [ ] 章節過濾正常顯示5個章節

#### 測試覆蓋
- [ ] 解析腳本測試通過
- [ ] 初始化腳本測試通過
- [ ] 驗證腳本測試通過
- [ ] 單元測試通過
- [ ] 系統整合測試通過

#### 文檔完整性
- [ ] requirements.md 已更新
- [ ] design.md 已更新
- [ ] README.md 已更新
- [ ] 實施計劃文檔存在

---

### 預估工時

- **Task 10.1**: LAW_TYPES 更新 - 0.5 小時
- **Task 10.2**: 解析腳本開發 - 4-6 小時
- **Task 10.3**: 初始化腳本開發 - 2-3 小時
- **Task 10.4**: 驗證腳本開發 - 1-2 小時
- **Task 10.5**: 測試開發 - 2-3 小時
- **Task 10.6**: 系統整合驗證 - 2-3 小時
- **Task 10.7**: 文檔更新 - 1-2 小時
- **Task 10.8**: 生產部署 - 1-2 小時

**總計**: 約 14-22 小時（2-3 個工作日）

---

### 風險與緩解

#### 風險 1: Markdown 格式解析錯誤
**緩解策略**:
- 先手動檢查文件格式一致性
- 編寫健壯的解析邏輯處理邊界情況
- 人工抽查解析結果

#### 風險 2: 條文內容提取不完整
**緩解策略**:
- 比對原始文件與解析結果
- 使用驗證腳本自動檢查
- 確保多段落條文正確處理

#### 風險 3: 系統整合問題
**緩解策略**:
- 遵循現有多法律支持架構
- 完整的整合測試
- 漸進式部署和驗證

---

## 完成檢查清單更新 (Updated Completion Checklist)

### 資料完整性（新增）
- [ ] 所有 54 個審查基準 JSON 檔案成功載入
- [ ] 審查基準條文總數正確（預期數百條）
- [ ] 所有條文有正確的 `type = "patent-examination"`
- [ ] 章節層級結構完整

---

## Phase 11: 行政訴訟法支持 (Administrative Litigation Act Support)

**目標**: 新增行政訴訟法作為系統支持的法律類型，完成資料解析、導入和驗證。

**依據**: 遵循 [`docs/NEW_LAW_TYPE_SOP.md`](NEW_LAW_TYPE_SOP.md) 標準作業流程

---

### Task 11.1: 更新 LAW_TYPES 常量
**File**: `db/models.py`

- [ ] 在 `LAW_TYPES` 字典中添加 `"administrative-litigation"` 定義：
  ```python
  "administrative-litigation": {
      "name_zh": "行政訴訟法",
      "name_en": "Administrative Litigation Act",
      "code": "administrative-litigation"
  }
  ```
- [ ] 執行驗證確認 LAW_TYPES 更新成功：
  ```bash
  python -c "from db.models import LAW_TYPES; print('administrative-litigation' in LAW_TYPES)"
  # 應輸出: True
  ```

**驗收標準**:
- LAW_TYPES 包含新的行政訴訟法定義
- API `/api/law-types` 能正確回傳新法律類型

---

### Task 11.2: 建立行政訴訟法解析腳本
**File**: `scripts/parse_administrative_litigation.py` (新建)

- [ ] 建立解析腳本檔案
- [ ] 實作主要解析函數 `parse_administrative_litigation_md()`:
  - [ ] 讀取 markdown 文件 (`knowledge/administrative_litigation_zh.md`)
  - [ ] 識別編標題（"第 X 編"，無前綴空格）
  - [ ] 識別章標題（前綴3個空格 + "第 X 章"）
  - [ ] 識別節標題（前綴6個空格 + "第 X 節"）
  - [ ] 提取條號（支援附加條號如 "第 3-1 條", "第 307-1 條"）
  - [ ] 組合完整章節路徑（編/章/節）
  - [ ] 生成 `article_number_int`（取主要數字）
- [ ] 實作輔助函數：
  - [ ] `extract_article_number()`: 提取條號和數字
  - [ ] `format_chapter_path()`: 格式化三層級章節路徑
- [ ] 添加命令列參數支持：
  - [ ] `--test`: 測試模式，只顯示統計
  - [ ] `--output`: 輸出 JSON 檔案路徑
- [ ] 實作錯誤處理和日誌輸出

**驗收標準**:
- 成功解析約 308 條行政訴訟法條文
- 章節層級結構正確（9編）
- 正確處理附加條號（3-1, 307-1 等）
- 抽查前10條、中10條、後10條內容正確性
- 運行: `python scripts/parse_administrative_litigation.py --test`

---

### Task 11.3: 建立行政訴訟法初始化腳本
**File**: `scripts/init_administrative_litigation.py` (新建)

- [ ] 建立初始化腳本檔案
- [ ] 實作主要初始化函數 `init_administrative_litigation()`:
  - [ ] 調用解析函數獲取法條資料
  - [ ] 為每個條文設定 `type = "administrative-litigation"`
  - [ ] 確保 `lang = "zh-TW"` 欄位存在
  - [ ] 使用 `LawModel` 驗證資料結構
  - [ ] 使用複合鍵 `(article_number, lang, type)` 進行 upsert
  - [ ] 統計插入和更新數量
- [ ] 添加命令列參數：
  - [ ] `--target`: 選擇目標資料庫 (local/remote/both)
  - [ ] `--dry-run`: 測試模式，不實際寫入
  - [ ] `--verbose`: 顯示詳細日誌
- [ ] 實作錯誤處理和回滾機制

**驗收標準**:
- Dry-run 模式正常運作
- 成功插入約 308 條法條到 local 資料庫
- 每條法條包含所有必要欄位
- 確認資料庫中的法條有正確的 `type` 和 `lang` 欄位
- 執行 `db.laws.find({type: "administrative-litigation"}).count()` 驗證總數約為 308
- 檢查編/章/節分布是否正確

**測試命令**:
```bash
# Dry run
python scripts/init_administrative_litigation.py --target local --dry-run --verbose

# 實際執行
python scripts/init_administrative_litigation.py --target local --verbose
```

---

### Task 11.4: 建立行政訴訟法驗證腳本
**File**: `scripts/verify_administrative_litigation.py` (新建)

- [ ] 建立驗證腳本檔案
- [ ] 實作驗證函數 `verify_administrative_litigation()`:
  - [ ] 檢查總條數（約 308 條）
  - [ ] 檢查編數（9 編）
  - [ ] 驗證必要欄位完整性（6個欄位）
  - [ ] 檢查內容不為空
  - [ ] 驗證 `article_number_int` 範圍
  - [ ] 統計各編條文數量
  - [ ] 驗證所有條文 `type = "administrative-litigation"`
  - [ ] 檢查無重複條文
- [ ] 生成詳細的驗證報告
- [ ] 添加支援 `--target` 參數（local/remote）

**驗收標準**:
- 所有驗證檢查通過（7/7）
- 執行驗證腳本應通過所有檢查
- 運行: `python scripts/verify_administrative_litigation.py`
- 確認輸出報告清晰易讀

---

### Task 11.5: 系統整合驗證

**前端驗證**:
- [ ] 啟動應用: `flask run`
- [ ] 確認法律類型選擇器包含「行政訴訟法」
- [ ] 切換到行政訴訟法，確認條文列表正確顯示
- [ ] 測試搜尋功能在行政訴訟法範圍內正常
- [ ] 測試章節過濾顯示 9 個編
- [ ] 測試分頁功能正常

**API 驗證**:
- [ ] 測試 `GET /api/law-types` 包含行政訴訟法
- [ ] 測試 `GET /laws?type=administrative-litigation` 回傳正確數據
- [ ] 測試 `GET /laws/<law_id>` 回傳行政訴訟法條文詳情

**資料庫驗證**:
- [ ] 確認索引正常（三欄位複合索引）
- [ ] 執行查詢效能測試
- [ ] 驗證資料一致性

---

### Task 11.6: 文檔更新

- [x] 更新 `docs/requirements.md`（Section 9.12, 9.13）
- [x] 更新 `docs/design.md`（LAW_TYPES + Section 9.12）
- [x] 更新 `docs/tasks.md`（此 Phase 11）
- [ ] 更新 `README.md`（如需要）
- [ ] 建立 `docs/ADMINISTRATIVE_LITIGATION_IMPLEMENTATION_PLAN.md`（可選）

---

### Task 11.7: 生產環境部署（可選）

**前置作業**:
- [ ] 完成所有本地測試
- [ ] 建立生產資料庫備份
- [ ] 準備回滾方案

**部署步驟**:
- [ ] 執行 `python scripts/init_administrative_litigation.py --target remote --verbose`
- [ ] 執行驗證: `python scripts/verify_administrative_litigation.py --target remote`
- [ ] 驗證生產環境資料正確
- [ ] 測試生產環境法律類型切換正常
- [ ] 監控系統運行狀態
- [ ] 記錄部署結果和時間
- [ ] 通知團隊成員新法律類型可用

---

### 完成檢查清單 (Administrative Litigation Completion Checklist)

#### 資料完整性
- [ ] 所有約 308 條行政訴訟法條文成功載入
- [ ] 條文總數正確（約 308 條，含附加條號）
- [ ] 所有條文有正確的 `type = "administrative-litigation"`
- [ ] 章節層級結構完整（9編，三層級：編/章/節）
- [ ] 所有條文內容不為空
- [ ] article_number_int 範圍正確（1-308）
- [ ] 附加條號處理正確（如 3-1, 307-1）

#### 功能完整性
- [ ] 法律類型選擇器包含行政訴訟法
- [ ] 可切換到行政訴訟法並正確顯示約 308 條條文
- [ ] 搜尋功能在行政訴訟法範圍內正常
- [ ] 可為行政訴訟法條文生成題目
- [ ] 進度追蹤與行政訴訟法正確關聯
- [ ] 章節過濾正常顯示 9 個編

#### 測試覆蓋
- [ ] 解析腳本測試通過
- [ ] 初始化腳本測試通過
- [ ] 驗證腳本測試通過
- [ ] 系統整合測試通過

#### 文檔完整性
- [x] requirements.md 已更新
- [x] design.md 已更新
- [x] tasks.md 已更新
- [ ] 實施計劃文檔存在（可選）

---

### 預估工時

- **Task 11.1**: LAW_TYPES 更新 - 0.5 小時
- **Task 11.2**: 解析腳本開發 - 4-6 小時
- **Task 11.3**: 初始化腳本開發 - 2-3 小時
- **Task 11.4**: 驗證腳本開發 - 1-2 小時
- **Task 11.5**: 系統整合驗證 - 2-3 小時
- **Task 11.6**: 文檔更新 - 1-2 小時
- **Task 11.7**: 生產部署 - 1-2 小時

**總計**: 約 12-19 小時（1.5-2.5 個工作日）

---

### 風險與緩解

#### 風險 1: 附加條號解析錯誤
**緩解策略**:
- 特別處理附加條號格式（3-1, 307-1）
- 測試邊界情況
- 人工抽查附加條號解析結果

#### 風險 2: 三層級章節路徑複雜度
**緩解策略**:
- 清晰的編/章/節識別邏輯
- 測試各種章節組合
- 驗證章節路徑格式正確

#### 風險 3: 大量條文（308 條）處理
**緩解策略**:
- 批次處理和進度顯示
- 錯誤處理和重試機制
- 分段驗證確保資料完整性

---

## Phase 12: 支援法條忽略功能 (Law Article Ignore Support)

### Task 11.1: 數據模型與 API 路由設定
**文件**: 
- `db/models.py`
- `routes/laws.py`

- [ ] 在 `db/models.py` 增加 `UserLawIgnoreModel` 和 `user_law_ignores` 集合的 indexes (`[("user_id", 1), ("law_id", 1)]`, uniqueness=True)
- [ ] 實作 `PUT /laws/<law_id>/ignore` API:
  - [ ] 切換法條的 ignore 狀態（針對當前登入者）
  - [ ] 若被設定為忽略，從 `user_law_stars_collection` 移除對應的 star (可選，確保邏輯上合情理，或者兩者可並存，此處由實作者決定)
  - [ ] 回傳新的 ignore 狀態
- [ ] 在 `GET /laws` API 中回傳是否已被忽略（在 response payload 中附上 `is_ignored: boolean` 類似 `is_starred`）

### Task 11.2: 庫存(Inventory)與題目生成服務更新
**文件**:
- `services/inventory.py`
- `routes/quiz.py`

- [ ] `services/inventory.py` 中的所有可用題目計算和拉取題目的查詢，都必須排除該使用者設定為忽略的 `law_id`：
  - [ ] `count_available_questions()`
  - [ ] `get_questions_for_session()`
  - [ ] *注意*: MongoDB 的 `$nin` 查詢可以處理此需求，可以先拉出所有被忽略的法律 ID 陣列後再做過濾。
- [ ] 背景出題邏輯 (`trigger_generation`) 中也應該考量忽略清單（若 AI 隨機挑選未出過題的法條出題時，應跳過被忽略的法條）。

### Task 11.3: 前端 UI 實作
**文件**:
- `static/css/style.css`
- `templates/laws.html`
- `templates/law_detail.html`
- `static/js/main.js` 或頁面內的 `<script>`

- [ ] 在 `laws.html` 的法條列表與單一法條卡片上，在「星星 (Star)」按鈕旁加入一鍵「忽略 (Ignore/Eye-slash/Minus)」按鈕
- [ ] 在 `law_detail.html` 中實作一樣的「忽略」按鈕
- [ ] CSS: 為設定為「已忽略」的法條與按鈕設計樣式 (例如：灰色化、加上刪除線，或是不同顏色的 icon)
- [ ] JS: 綁定 `/laws/<law_id>/ignore` 的 AJAX 呼叫並即時更新 UI 狀態
- [ ] 測試使用者流程：忽略一個法條後，去開 quiz session，該法條的題目是否不會再出現。

---

## Phase N: 全部題庫頁面 (Question Bank Browser)

### Task N.1: 後端 API — 取得全部題目
**File**: [`routes/laws.py`](../routes/laws.py)

- [ ] 在 `questions_bp` 新增 `GET /api/questions/all` endpoint
- [ ] 接收 query params: `page`, `per_page`, `type`, `lang`, `law_type`
- [ ] 查詢流程：
  1. 取得 session 的 `law_type`（可被 query param 覆蓋）
  2. 根據 `law_type` 找到對應的所有 `law_id`（`laws_collection.find({"type": law_type, "lang": lang})`）
  3. 以 `law_id` list 為 filter 查詢 `questions_collection`（`{"law_id": {"$in": [...]}, "is_deleted": False, "lang": lang}`）
  4. 加上 `type` filter（如有）
  5. 分頁：`skip` + `limit`
  6. 為每題附加 `law_info`（article_number、chapter）、`is_starred`、`last_score`（來自 `user_progress`，無則 `null`）
- [ ] 回傳 `{ questions, total, page, per_page, total_pages }`

### Task N.2: 前端路由
**File**: [`routes/frontend.py`](../routes/frontend.py)

- [ ] 新增 `GET /question-bank` 路由，render `question_bank.html`

### Task N.3: 建立 `question_bank.html` 模板
**File**: `templates/question_bank.html`

- [ ] 繼承 `base.html`
- [ ] 複製 `my_questions.html` 的結構與樣式（card、tab-nav CSS、question-card CSS、pagination）
- [ ] 移除 starred/wrong tabs；改為顯示單一「全部題庫」標題
- [ ] 保留題型篩選按鈕（全部 / 選擇題 / 問答題）
- [ ] JS `loadQuestions()` 呼叫 `/api/questions/all` 而非 `/api/questions/my-questions`
- [ ] 顯示 `last_score` 或「未作答」badge（未作答用灰色 badge）
- [ ] 保留 star toggle（呼叫現有 `/api/quiz/questions/:id/star`）
- [ ] 保留 law-link 點擊跳轉

### Task N.4: 導航連結
**File**: [`templates/base.html`](../templates/base.html)

- [ ] 在 `<nav class="nav">` 中的「法條瀏覽」連結後面加入「題庫」連結（`href="/question-bank"`）
- [ ] 加上 active 狀態：`{% if request.path == '/question-bank' %}active{% endif %}`

---

## 參考資料

- [`requirements.md`](requirements.md) - 功能需求文檔
- [`design.md`](design.md) - 系統設計文檔
- [`db/models.py`](../db/models.py) - 數據模型定義
- [`services/auth.py`](../services/auth.py) - 認證服務
- [`routes/laws.py`](../routes/laws.py) - 法條路由
- `knowledge/examination/` - 審查基準資料來源目錄

---

## Phase 13: 個人進度頁面 — 我的進度 (Personal Progress Page) [REQ-012]

**Goal**: Add a `/progress` page showing five study metrics and daily trend charts, backed by a new `user_daily_stats` collection that is upserted on every answer submission.

**Design reference**: `docs/design.md` § 11

---

### Task 13.1: Add `UserDailyStatsModel` and collection to `db/models.py`

**File**: `db/models.py`

- [ ] TASK-13.1.1: Import `List` from `typing` if not already present (it is, confirm no change needed).
- [ ] TASK-13.1.2: Add `UserDailyStatsModel` dataclass after `UserLawStatsModel`:
  ```python
  @dataclass
  class UserDailyStatsModel:
      user_id: str
      date: str              # "YYYY-MM-DD"
      questions_answered: int = 0
      total_score: float = 0.0
      laws_covered: List[str] = field(default_factory=list)
      mastered_count: int = 0
  ```
- [ ] TASK-13.1.3: In `Database._initialize()`, add `self.user_daily_stats_collection = self.db['user_daily_stats']`.
- [ ] TASK-13.1.4: In `Database.init_db()`, add two indexes for the new collection:
  - `create_index([("user_id", 1), ("date", 1)], unique=True)` — composite unique key.
  - `create_index([("user_id", 1), ("date", -1)])` — for descending date-range queries.
- [ ] TASK-13.1.5: At module level, expose `user_daily_stats_collection = db.user_daily_stats_collection`.

**Validation**: `python -c "from db.models import user_daily_stats_collection; print('ok')"` prints `ok` without error.

---

### Task 13.2: Create `services/progress.py` — progress query and upsert logic

**File**: `services/progress.py` (new file)

- [ ] TASK-13.2.1: Implement `upsert_daily_stats(user_id: ObjectId, law_id: str, score: float) -> None`:
  - Compute `today = datetime.utcnow().strftime("%Y-%m-%d")`.
  - Count `mastered_count` via `user_progress_collection.count_documents({"user_id": user_id, "correct_streak": {"$gte": 3}})`.
  - Call `user_daily_stats_collection.update_one({"user_id": user_id, "date": today}, {"$inc": {"questions_answered": 1, "total_score": score}, "$addToSet": {"laws_covered": law_id}, "$set": {"mastered_count": mastered_count}}, upsert=True)`.

- [ ] TASK-13.2.2: Implement `get_progress_summary(user_id: str, range_days: int | None) -> dict`:
  - Build MongoDB date filter: if `range_days` is not `None`, compute `cutoff = (datetime.utcnow() - timedelta(days=range_days)).strftime("%Y-%m-%d")` and filter `date >= cutoff`.
  - Fetch and sort all matching `user_daily_stats` records for the user ascending by `date`.
  - Compute **streak**: starting from today's date string, step backward one day at a time; count consecutive days that have a record with `questions_answered > 0`; stop at first gap.
  - Sum `questions_answered` and `total_score` across fetched records.
  - Compute `avg_score_rate`: `(total_score / questions_answered * 100)` if `questions_answered > 0`, else `0.0`.
  - Compute `laws_covered`: union all `laws_covered` lists from fetched records, return `len(set(...))`.
  - Take `mastered_count` from the record with the latest `date`; default `0` if no records.
  - Call `_fill_date_gaps(records, range_days)` to produce a continuous date series.
  - Return `{"streak": int, "questions_answered": int, "mastered_count": int, "avg_score_rate": float, "laws_covered": int, "daily_records": list}`.

- [ ] TASK-13.2.3: Implement private helper `_fill_date_gaps(records: list, range_days: int | None) -> list`:
  - Determine the start date: `today - range_days + 1` days if `range_days` is set; else the earliest record's date.
  - Build a dict `{date: record}` from the fetched records.
  - Iterate each calendar day from start to today; if a day has no record, insert `{"date": date_str, "questions_answered": 0, "avg_score_rate": 0.0}`.
  - Return the filled list sorted ascending by date.

- [ ] TASK-13.2.4: Implement `get_daily_chart_data(daily_records: list) -> dict`:
  - Extract parallel arrays `labels`, `questions_data`, and `score_data` from the filled records.
  - `score_data[i]` = `round(record["avg_score_rate"], 1)` (already computed per-record: `total_score / questions_answered * 100` or `0.0`).
  - Return `{"labels": [...], "questions_data": [...], "score_data": [...]}`.

**Validation**: Write a quick unit test or `python -c` smoke test confirming `get_progress_summary` returns the correct keys with an empty DB (all zeros).

---

### Task 13.3: Hook `upsert_daily_stats` into answer submission — `routes/quiz.py`

**File**: `routes/quiz.py`

- [ ] TASK-13.3.1: Add import at top of file: `from services.progress import upsert_daily_stats`.
- [ ] TASK-13.3.2: In `submit_answer()`, after the `user_law_stats` upsert block (after line ~398) and before building the response, add:
  ```python
  # Update daily stats for progress page [REQ-012-005]
  try:
      upsert_daily_stats(user_id, law_id, score)
  except Exception as e:
      logger.warning(f"Failed to upsert daily stats: {e}")
      # Non-fatal: do not fail the answer submission
  ```
- [ ] TASK-13.3.3: Confirm `law_id` is already in scope at that point in the function (it is — set earlier as `law_id = question['law_id']`). No additional extraction needed.

**Validation**: Submit a test answer via the UI or `curl`; check `db.user_daily_stats.find()` shows a document for today with `questions_answered: 1`.

---

### Task 13.4: Add `GET /progress` route — `routes/frontend.py`

**File**: `routes/frontend.py`

- [ ] TASK-13.4.1: Add imports at top: `from flask import request` (if not present) and `from services.progress import get_progress_summary, get_daily_chart_data`.
- [ ] TASK-13.4.2: Add imports: `from services.auth import get_current_user` (already imported via `login_required` decorator, confirm).
- [ ] TASK-13.4.3: Add `GET /progress` route handler:
  ```python
  @frontend_bp.route('/progress')
  @login_required
  def progress_page():
      user_id = get_current_user()
      range_param = request.args.get('range', '7')
      if range_param == 'all':
          range_days = None
      else:
          try:
              range_days = int(range_param)
              if range_days not in (7, 30):
                  range_days = 7
                  range_param = '7'
          except ValueError:
              range_days = 7
              range_param = '7'

      summary = get_progress_summary(user_id, range_days)
      chart_data = get_daily_chart_data(summary['daily_records'])
      return render_template(
          'progress.html',
          summary=summary,
          chart_data=chart_data,
          selected_range=range_param
      )
  ```

**Validation**: `GET /progress` returns HTTP 200 with rendered HTML; `GET /progress?range=30` and `GET /progress?range=all` also return 200.

---

### Task 13.5: Create `templates/progress.html`

**File**: `templates/progress.html` (new file)

- [ ] TASK-13.5.1: Extend `base.html` (`{% extends "base.html" %}`).
- [ ] TASK-13.5.2: Add `{% block title %}我的進度{% endblock %}`.
- [ ] TASK-13.5.3: Build the **time range selector** — three `<a>` links:
  - `<a href="/progress?range=7" class="range-btn {% if selected_range == '7' %}active{% endif %}">最近 7 天</a>`
  - `<a href="/progress?range=30" class="range-btn {% if selected_range == '30' %}active{% endif %}">最近 30 天</a>`
  - `<a href="/progress?range=all" class="range-btn {% if selected_range == 'all' %}active{% endif %}">全部時間</a>`
- [ ] TASK-13.5.4: Build the **five metric cards** row using `summary` template variable:
  - 連續練習天數: `{{ summary.streak }}` 天
  - 作答題數: `{{ summary.questions_answered }}` 題
  - 掌握題數: `{{ summary.mastered_count }}` 題
  - 平均得分率: `{{ "%.1f"|format(summary.avg_score_rate) }}%`
  - 覆蓋法條數: `{{ summary.laws_covered }}` 條
- [ ] TASK-13.5.5: Add two `<canvas>` elements: `id="chart-questions"` and `id="chart-score"`, each with a descriptive heading above them ("每日作答題數" and "每日平均得分率").
- [ ] TASK-13.5.6: Add Chart.js CDN script tag before the chart init block: `<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>`.
- [ ] TASK-13.5.7: Add a `<script>` block that reads `{{ chart_data | tojson }}` into a JS variable and renders both charts:
  - Bar chart on `#chart-questions` using `chartData.labels` and `chartData.questions_data`.
  - Line chart on `#chart-score` using `chartData.labels` and `chartData.score_data`.
  - Both charts use `responsive: true` and sensible axis labels.
- [ ] TASK-13.5.8: Ensure the page displays a friendly empty state message ("目前尚無練習記錄") when `summary.questions_answered == 0`, hiding the chart canvases in that case.

**Validation**: Visit `/progress` in the browser; all five cards render; both charts render without console errors; the empty state shows when the user has no data.

---

### Task 13.6: Add "我的進度" nav link — `templates/base.html`

**File**: `templates/base.html`

- [ ] TASK-13.6.1: Locate the `<nav class="nav">` element and find the existing nav links (首頁, 法條瀏覽, 題庫).
- [ ] TASK-13.6.2: Append a new link after the existing ones:
  ```html
  <a href="/progress" class="nav-link {% if request.path == '/progress' %}active{% endif %}">我的進度</a>
  ```
- [ ] TASK-13.6.3: Confirm `request` is available in the Jinja2 context (it is by default in Flask templates). No additional context injection needed.

**Validation**: The "我的進度" link appears in the navbar on all pages; it renders as `active` when on `/progress` and inactive on all other pages.

---

### Task 13.7: Add CSS styles for the progress page — `static/css/style.css`

**File**: `static/css/style.css`

- [ ] TASK-13.7.1: Add `.progress-page` container styles (max-width, padding — consistent with other page containers).
- [ ] TASK-13.7.2: Add `.range-selector` wrapper and `.range-btn` styles:
  - Default: outlined button appearance matching the console design system.
  - `.range-btn.active`: filled/highlighted state to indicate the selected range.
- [ ] TASK-13.7.3: Add `.metric-cards` grid: `display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem;` on desktop.
- [ ] TASK-13.7.4: Add `.metric-card` styles: card background, border-radius, padding, centered text.
- [ ] TASK-13.7.5: Add `.metric-value` (large, bold number) and `.metric-label` (small, muted label) typography styles.
- [ ] TASK-13.7.6: Add `.chart-container` wrapper with a defined `max-height` to prevent charts from being excessively tall.
- [ ] TASK-13.7.7: Add responsive breakpoint (`max-width: 640px`): collapse `.metric-cards` to `grid-template-columns: repeat(2, 1fr)` with the fifth card spanning full width (`grid-column: 1 / -1`).

**Validation**: Progress page metric cards display in a 5-column row on desktop and 2-column grid on mobile (320–640px); charts are capped in height and don't overflow.

---

### Task 13.8: Write unit tests for `services/progress.py`

**File**: `test/test_progress_service.py` (new file)

- [ ] TASK-13.8.1: Test `_fill_date_gaps` with a 7-day range and 3 records — confirm output has exactly 7 entries, gaps filled with zeros.
- [ ] TASK-13.8.2: Test `get_daily_chart_data` — confirm `labels`, `questions_data`, `score_data` arrays are all the same length.
- [ ] TASK-13.8.3: Test `get_progress_summary` with an empty `user_daily_stats` collection — all metric values should be `0` or `0.0`.
- [ ] TASK-13.8.4: Test streak calculation: given records for 3 consecutive days ending today, streak should be `3`; inserting a gap (yesterday missing) should reset streak to `1` (today only).
- [ ] TASK-13.8.5: Test `avg_score_rate` calculation: 2 answers with scores `0.5` and `1.0` → `avg_score_rate == 75.0`.
- [ ] TASK-13.8.6: Test `laws_covered` deduplication: the same `law_id` appearing in two days' records is counted once.
- [ ] Run: `pytest test/test_progress_service.py -v`

---

### Task 13.9: Integration smoke test

**Checklist** (manual or scripted):

- [ ] TASK-13.9.1: Log in as a test user; confirm `/progress` loads without error.
- [ ] TASK-13.9.2: Submit 3 answers in a quiz session; revisit `/progress?range=7`; confirm `questions_answered` incremented to `3`.
- [ ] TASK-13.9.3: Confirm `avg_score_rate` reflects the actual scores of those 3 answers (within floating-point rounding).
- [ ] TASK-13.9.4: Confirm `laws_covered` reflects the distinct law articles of the answered questions.
- [ ] TASK-13.9.5: Confirm `mastered_count` updates after a question reaches `correct_streak >= 3`.
- [ ] TASK-13.9.6: Switch time range to "全部時間" and confirm cumulative totals are higher than or equal to the 7-day view.
- [ ] TASK-13.9.7: Verify on a 375px-wide viewport that metric cards are in a 2-column grid and charts are readable.
- [ ] TASK-13.9.8: Confirm the "我的進度" nav link is active when on `/progress` and inactive on all other pages.

---

### Completion Checklist — Phase 13

#### Data integrity

- [ ] Every answer submission creates or updates a `user_daily_stats` document for the correct `(user_id, date)`.
- [ ] `laws_covered` never contains duplicate `law_id` entries within a single day's record.
- [ ] `mastered_count` in the daily record reflects `correct_streak >= 3` at the time of submission.

#### Feature completeness

- [ ] All five metrics display correctly for 7-day, 30-day, and all-time ranges.
- [ ] Streak correctly resets on a gap day.
- [ ] Both charts render with correct data; days with no activity show as `0`.
- [ ] Page gracefully shows empty state when no data exists.

#### Code quality

- [ ] `upsert_daily_stats` is wrapped in a `try/except` in `routes/quiz.py` — a failure must not prevent the answer response from being returned.
- [ ] No `user_id` or any other identity information is accepted from the query string on the `/progress` route — always sourced from `session`.

#### Estimated effort

- Task 13.1 (db model): ~0.5 h
- Task 13.2 (progress service): ~3 h
- Task 13.3 (quiz.py hook): ~0.5 h
- Task 13.4 (frontend route): ~0.5 h
- Task 13.5 (progress.html template): ~3 h
- Task 13.6 (base.html nav link): ~0.25 h
- Task 13.7 (CSS): ~1.5 h
- Task 13.8 (unit tests): ~2 h
- Task 13.9 (integration smoke): ~1 h

**Total**: ~12.25 hours (~1.5 working days)
