# admin.py 現況與可執行項目

## 現況

### API 功能面

這支 API 是 Service Gateway 的管理後台入口，採用 passthrough 代理模式，共有 19 個 endpoint，分四個管理域：

| 管理域 | Endpoint 數量 | 代理目標 |
|--------|-------------|---------|
| Agent 管理 | 5 個 | Agent Card Service |
| MCP Server 管理 | 5 個 | MCP Gateway |
| 回饋查詢 | 1 個 | Memory Service |
| 設定管理 | 4 個 | Config Service |
| Prompt 管理 | 4 個 | Config Service |

### 文件面

- 對話相關 API（`/chat`、`/conversations`）有完整的 API 規格文件
- `admin.py` 管理的所有 endpoint 沒有對應的 API 規格文件，只有 `README.md` 裡的流程圖

### 測試面

| 測試層 | 覆蓋狀況 |
|--------|---------|
| Router 層 | agents ✅、mcp-servers ✅、feedbacks ❌、configs ❌、prompts ❌ |
| Service 層（agentcard）| 完整，含邊界情境 ✅ |
| Service 層（config）| 完整，含邊界情境 ✅ |
| Service 層（mcp-gateway）| 存在但未驗證 |
| Service 層（memory-admin）| 存在但未驗證 |

### 程式碼面

- `GET /admin/agents` 的 query params 沒有 `Query(description=...)` 標注，OpenAPI 文件缺說明
- 每個 endpoint 都建立新的 `AsyncHttpClient`，沒有共享 connection pool
- fixture teardown 用 `clear()` 而非只刪自己的 key

---

## 可以執行的改進項目

### 測試補足（低風險，直接可做）

- 補 `GET /admin/feedbacks` 的 router 層測試，加入成功、502、504、缺 traceparent 四個情境
- 補 `GET /admin/configs`、`POST /admin/configs`、`PUT /admin/configs/{key}` 的 router 層測試
- 補 `GET /admin/prompts`、`PUT /admin/prompts/{agent_key}/{node_name}`、`POST /admin/prompts` 的 router 層測試
- 補 `DELETE /admin/mcp-servers/{id}/access-policies/{agent_id}` 的 router 層測試
- 把 `app.dependency_overrides.clear()` 改成 `del app.dependency_overrides[對應的 key]`

### 程式碼一致性（低風險）

- 把 `GET /admin/agents` 的 query params 補上 `Annotated[..., Query(description="...")]`，和同檔案其他 endpoint 對齊

---

## 需要討論才能動的項目

- **HTTP client 的生命週期**：是否要改成從 `app.state` 取共享 client，需要確認設計意圖
- **admin API 文件**：是否要補 API 規格文件，需要確認這是文件債還是刻意不寫

---

## 優先建議

如果時間只夠做一件事，**第 5 點（fixture teardown）** 是最值得提出來的，因為它是一個「現在沒問題、但埋了地雷」的情況，正好可以展示你在看測試時不只看有沒有測，還在看測試本身的品質。