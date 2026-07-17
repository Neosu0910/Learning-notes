# 學習筆記：從 Ingress 遷移到 Gateway API

## 先搞懂大方向：流量怎麼進到 K8s？

外面的使用者要連到你 K8s 裡面跑的服務，需要一個「入口」。這個入口的演進：

```
舊方式：Ingress + Ingress Controller（如 nginx）
新方式：Gateway API + 實作（如 Istio）
```

Gateway API 是 K8s 社群推出的新標準，目標是取代 Ingress。

## 為什麼要換？Ingress 的三個問題

### 1. Annotation Hell（註解地獄）
Ingress 本身的功能很少，進階功能（限流、IP 白名單、session affinity）全靠 annotation 實現。問題是每家的 annotation 都不一樣，換一個 controller 全部要重寫。

### 2. 沒有角色分離
Ingress 就一個 YAML 搞定所有事。但實際上「管 Load Balancer 的人」和「管 App 路由的人」通常不是同一組人。

### 3. 擴充性差
想加功能只能加 annotation，沒有結構化的方式。

## Gateway API 怎麼解決這些問題？

Gateway API 把事情拆成三層：

```
GatewayClass → 由雲端/平台團隊管理（選用哪個實作，如 Istio）
    ↓
Gateway → 由基礎設施團隊管理（設定 listener、port、TLS）
    ↓
HTTPRoute → 由應用團隊管理（設定路由規則、對應的 backend）
```

這樣角色分離就清楚了。

## 核心概念

### GatewayClass
類似「選擇你要用哪個品牌的路由器」。Istio、Envoy Gateway、Cilium 都有各自的 GatewayClass。

### Gateway
定義「入口在哪裡、聽哪些 port 和 hostname」。一個 Gateway 可以被很多 HTTPRoute 共用。

### HTTPRoute
定義「什麼 URL 走哪個 backend service」。這是應用開發者最常碰的東西。

## 常見路由模式

### 多域名共用 Gateway
```yaml
# api.example.com → api-service
# admin.example.com → admin-service
# 各自一個 HTTPRoute，指向同一個 Gateway
```

### 根據 path 分流
```yaml
# /api/v1 → api-v1-service
# /api/v2 → api-v2-service
# /healthz → healthcheck-service
```

## 為什麼選 Istio 當實作？

- 壓測穩定性最好
- 功能最完整（Gateway API 標準功能 + Istio 自己的 VirtualService、DestinationRule）
- 之後要做 Service Mesh（mTLS、tracing）不用換底層

## Nginx Annotation 怎麼對應到新世界？

| 功能 | 舊：nginx annotation | 新：Gateway API / Istio |
|------|---------------------|------------------------|
| Session Affinity | `affinity: cookie` | Istio DestinationRule |
| IP 白名單 | `whitelist-source-range` | Istio AuthorizationPolicy |
| Body Size 限制 | `proxy-body-size` | Istio EnvoyFilter |
| 限流 | `rate-limit` | Istio EnvoyFilter |
| URL 改寫 | `rewrite-target` | HTTPRoute urlRewrite（標準） |
| HTTPS 強制跳轉 | `ssl-redirect` | Gateway listener 設定（標準） |

重點觀察：基本的路由功能已經標準化了，但進階功能仍然依賴各家實作。Istio 用自己的 CRD 來補足這些缺口。

## 遷移的思路

1. 盤點現有所有 Ingress 資源和用到的 annotation
2. 用 `ingress2gateway` 工具先做基本轉換（host、path、TLS）
3. 人工處理 annotation 對應的功能（用 Istio 的方式實作）
4. 在測試環境驗證
5. 切流量

## 在 AWS EKS 上的注意事項

Gateway 建出來會自動產生一個 LoadBalancer Service，但需要加 AWS 的 annotation 才能正確觸發 NLB 建立。這跟 Ingress-nginx 時代是類似的。

## References

- [Gateway API 官網](https://gateway-api.sigs.k8s.io/)
- [Istio Gateway API 指南](https://istio.io/latest/docs/tasks/traffic-management/ingress/gateway-api/)
- [ingress2gateway 工具](https://github.com/kubernetes-sigs/ingress2gateway)
