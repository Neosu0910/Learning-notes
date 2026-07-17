# 學習筆記：External-DNS 升級（理解 K8s 元件升級的流程）

## 這是什麼？

External-DNS 是一個跑在 K8s 裡的元件，功能是：當你在 K8s 裡建了一個服務，它會自動去 DNS（像 Route53）幫你建對應的 DNS 紀錄。

白話說：你部署一個 API，external-dns 會自動幫你設定 `api.example.com → 對應的 IP`，不用手動去 Route53 建。

## 我學到什麼？

### 1. K8s 元件升級不是只換版本號

升級一個元件通常涉及兩件事：
- **RBAC 權限**：新版本可能需要存取新的 K8s 資源，要先給權限
- **Image 版本**：才是真的換新版

如果只換 image 不加權限，Pod 會啟動失敗（Permission Denied）。

**正確順序：先加權限 → 再換版本。**

### 2. RBAC 是什麼？

RBAC = Role-Based Access Control。K8s 裡每個 Pod 不是想做什麼就能做什麼，你要透過 ClusterRole 明確授權。

例如 external-dns v0.18.0 需要讀取 `endpointslices` 和 `namespaces`，就要在 ClusterRole 裡加上這些資源的 `get/list/watch` 權限。

### 3. 升級的安全網：回滾

K8s 升級有個好處：回滾很容易。`kubectl set image` 換回舊版 image 就好，而且新加的 RBAC 權限不會影響舊版運作（多了權限不會壞，少了才會）。

### 4. 為什麼需要升級？

這次升級是因為要從 Ingress 換成 Gateway API。Gateway API 是 K8s 的新一代流量入口標準，external-dns 要 v0.18.0 以上才認得 Gateway API 的資源。

## 核心指令備忘

```bash
# 匯出現有設定（升級前一定要備份）
kubectl get clusterrole external-dns -o yaml > backup.yaml
kubectl get deployment external-dns -n kube-system -o yaml > backup-deploy.yaml

# 改完 RBAC 後套用
kubectl apply -f external-dns-clusterrole.yaml

# 升級 image
kubectl set image deployment/external-dns -n kube-system \
  external-dns=registry.k8s.io/external-dns/external-dns:v0.18.0

# 確認升級成功
kubectl get pods -n kube-system -l app.kubernetes.io/name=external-dns
kubectl logs -f deployment/external-dns -n kube-system

# 出事了就回滾
kubectl set image deployment/external-dns -n kube-system \
  external-dns=registry.k8s.io/external-dns/external-dns:v0.13.6
```

## 延伸：這個模式會反覆出現

以後升級任何 K8s 元件（cert-manager、ingress controller、monitoring stack）都是類似流程：
1. 看 release notes，確認有沒有 breaking changes
2. 備份現有設定
3. 更新 RBAC / CRD（如果需要）
4. 更新 image
5. 驗證 + 準備回滾方案
