# Kubernetes (K8s) 學習指南

## 什麼是 Kubernetes？

Kubernetes（簡稱 K8s，因為 k 和 s 之間有 8 個字母）是一個容器編排平台。簡單說：當你有很多 Docker container 要管理時，K8s 幫你自動化部署、擴展、和維運。

### 為什麼需要 K8s？

沒有 K8s 的世界：
- 手動在不同機器上啟動 container
- 某台機器掛了，要手動把服務搬到另一台
- 流量突然變大，要手動加機器、加 container
- 更新版本要一台一台處理

有 K8s 的世界：
- 告訴 K8s「我要跑 3 個 nginx」，它自動分配到不同機器
- 機器掛了，K8s 自動在別的機器重新啟動 container
- 設定自動擴展，流量大就自動加 container
- 滾動更新，零停機切版本

---

## 核心架構

```
┌─────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                  │
│                                                       │
│  ┌─────────────────────────────────────────────────┐ │
│  │              Control Plane (Master)               │ │
│  │                                                   │ │
│  │  ┌──────────┐ ┌───────────┐ ┌────────────────┐  │ │
│  │  │API Server│ │  Scheduler│ │Controller Manager│  │ │
│  │  └──────────┘ └───────────┘ └────────────────┘  │ │
│  │  ┌──────┐                                        │ │
│  │  │ etcd │  (儲存所有叢集狀態)                      │ │
│  │  └──────┘                                        │ │
│  └─────────────────────────────────────────────────┘ │
│                                                       │
│  ┌───────────────┐  ┌───────────────┐               │
│  │   Worker Node  │  │   Worker Node  │  ...         │
│  │                 │  │                 │              │
│  │ ┌───────────┐  │  │ ┌───────────┐  │              │
│  │ │  kubelet  │  │  │ │  kubelet  │  │              │
│  │ │kube-proxy │  │  │ │kube-proxy │  │              │
│  │ │           │  │  │ │           │  │              │
│  │ │ ┌─Pod──┐  │  │  │ ┌─Pod──┐  │  │              │
│  │ │ │Container│ │  │ │ │Container│ │  │              │
│  │ │ └───────┘  │  │  │ └───────┘  │  │              │
│  │ └───────────┘  │  │ └───────────┘  │              │
│  └───────────────┘  └───────────────┘               │
└─────────────────────────────────────────────────────┘
```

### Control Plane 組件

| 組件 | 功能 |
|------|------|
| **API Server** | 叢集的前門，所有操作都透過它（kubectl 就是呼叫它） |
| **etcd** | 分散式鍵值資料庫，儲存整個叢集的狀態 |
| **Scheduler** | 決定 Pod 要放在哪個 Node 上 |
| **Controller Manager** | 確保實際狀態 = 期望狀態（例如維持 3 個副本） |

### Worker Node 組件

| 組件 | 功能 |
|------|------|
| **kubelet** | 確保 Pod 在 Node 上正確運行 |
| **kube-proxy** | 處理 Node 上的網路規則 |
| **Container Runtime** | 跑 container 的引擎（containerd, CRI-O） |

---

## 核心概念

### Pod
- K8s 最小的部署單位
- 一個 Pod 裡面可以有一個或多個 container
- 同一個 Pod 裡的 container 共享網路和儲存
- 通常一個 Pod 跑一個主要應用

### Deployment
- 管理 Pod 的控制器
- 定義要跑幾個副本（replicas）
- 處理滾動更新和回滾

### Service
- 為一組 Pod 提供固定的網路入口
- Pod 的 IP 會變，但 Service 的 IP 不變
- 內建負載均衡

### Namespace
- 叢集內的虛擬隔離（像資料夾）
- 不同團隊或環境（dev/staging/prod）可以用不同 namespace

---

## kubectl 基本指令

### 安裝 kubectl

```bash
# macOS
brew install kubectl

# RHEL/CentOS
sudo dnf install kubectl

# 確認版本
kubectl version --client
```

### 叢集資訊

```bash
# 查看叢集資訊
kubectl cluster-info

# 查看所有 node
kubectl get nodes

# 查看 node 詳細資訊
kubectl describe node <node-name>

# 查看目前的 context
kubectl config current-context

# 切換 context
kubectl config use-context my-cluster
```

### 基本 CRUD 操作

```bash
# 取得資源
kubectl get pods                    # 列出 pods
kubectl get pods -o wide            # 更多資訊（IP、Node）
kubectl get pods -A                 # 所有 namespace
kubectl get deployments
kubectl get services
kubectl get all                     # 列出所有資源

# 查看詳細資訊
kubectl describe pod <pod-name>
kubectl describe deployment <name>

# 建立資源
kubectl apply -f deployment.yaml

# 刪除資源
kubectl delete pod <pod-name>
kubectl delete -f deployment.yaml

# 查看 log
kubectl logs <pod-name>
kubectl logs <pod-name> -f          # 即時追蹤
kubectl logs <pod-name> -c <container>  # 多容器 Pod

# 進入 Pod 內部
kubectl exec -it <pod-name> -- /bin/bash
kubectl exec -it <pod-name> -- sh

# 看 Pod 內的環境變數
kubectl exec <pod-name> -- env
```

---

## YAML 設定檔

K8s 的一切都用 YAML 定義。基本結構：

```yaml
apiVersion: v1/apps/v1/...    # API 版本
kind: Pod/Deployment/Service   # 資源類型
metadata:                      # 識別資訊
  name: my-app
  labels:
    app: my-app
spec:                          # 規格定義（你要什麼）
  ...
```

### Pod 範例

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-nginx
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

### Deployment 範例

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  replicas: 3                    # 要跑 3 個副本
  selector:
    matchLabels:
      app: my-app                # 用 label 選擇管理哪些 Pod
  template:                      # Pod 模板
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: DB_HOST
          value: "db.example.com"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
```

### Service 範例

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  type: ClusterIP              # 只在叢集內部可存取
  selector:
    app: my-app                # 把流量導到有這個 label 的 Pod
  ports:
  - port: 80                   # Service 的 port
    targetPort: 8080           # Pod 的 port
```

### Service 類型

| 類型 | 說明 | 使用時機 |
|------|------|----------|
| **ClusterIP** | 只有叢集內部可存取 | 微服務之間的通訊 |
| **NodePort** | 每個 Node 開一個 port 對外 | 開發測試 |
| **LoadBalancer** | 建立雲端負載均衡器 | 生產環境對外服務 |
| **ExternalName** | 映射到外部 DNS | 存取外部服務 |

---

## ConfigMap 與 Secret

### ConfigMap — 存放設定

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_URL: "postgres://db:5432/mydb"
  LOG_LEVEL: "info"
  config.json: |
    {
      "feature_flags": {
        "new_ui": true
      }
    }
```

### Secret — 存放敏感資訊

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  # 值需要 base64 編碼
  DB_PASSWORD: cGFzc3dvcmQxMjM=    # echo -n "password123" | base64
  API_KEY: bXlzZWNyZXRrZXk=
```

### 在 Pod 中使用

```yaml
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    envFrom:
    - configMapRef:
        name: app-config
    - secretRef:
        name: app-secrets
    # 或個別引用
    env:
    - name: DB_PASS
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: DB_PASSWORD
```

---

## 儲存（Volumes）

### 常見 Volume 類型

| 類型 | 說明 |
|------|------|
| `emptyDir` | Pod 內 container 間共享的暫存空間 |
| `hostPath` | 掛載 Node 上的目錄（開發用） |
| `PersistentVolume (PV)` | 獨立於 Pod 生命週期的持久儲存 |
| `PersistentVolumeClaim (PVC)` | 使用者對 PV 的請求 |

### PVC 範例

```yaml
# 請求 10GB 的儲存空間
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-data
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: gp2    # AWS EBS
---
# 在 Pod 中使用
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    volumeMounts:
    - name: data
      mountPath: /app/data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: my-data
```

---

## Ingress — 對外流量管理

Ingress 讓你用 HTTP/HTTPS 規則管理外部流量怎麼進入叢集。

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
  tls:
  - hosts:
    - app.example.com
    secretName: tls-secret
```

---

## 健康檢查（Probes）

```yaml
spec:
  containers:
  - name: my-app
    image: my-app:1.0
    # 存活探測：失敗會重啟 container
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 5
    # 就緒探測：失敗會從 Service 移除（不接收流量）
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 3
    # 啟動探測：給慢啟動的應用更多時間
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
```

---

## 自動擴展（HPA）

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

```bash
# 用指令建立 HPA
kubectl autoscale deployment my-app --min=2 --max=10 --cpu-percent=70

# 查看 HPA 狀態
kubectl get hpa
```

---

## 常用 kubectl 操作

### 部署相關

```bash
# 部署應用
kubectl apply -f deployment.yaml

# 查看 rollout 狀態
kubectl rollout status deployment/my-app

# 查看 rollout 歷史
kubectl rollout history deployment/my-app

# 回滾到上一個版本
kubectl rollout undo deployment/my-app

# 回滾到指定版本
kubectl rollout undo deployment/my-app --to-revision=2

# 暫停/恢復 rollout
kubectl rollout pause deployment/my-app
kubectl rollout resume deployment/my-app

# 擴展副本數
kubectl scale deployment my-app --replicas=5
```

### 除錯

```bash
# 查看 Pod 事件
kubectl describe pod <pod-name>

# 查看 Pod log
kubectl logs <pod-name> --previous    # 看上一次（crash 前）的 log

# 進入 Pod 執行指令
kubectl exec -it <pod-name> -- /bin/bash

# 啟動一個除錯用的 Pod
kubectl run debug --rm -it --image=busybox -- sh
kubectl run debug --rm -it --image=nicolaka/netshoot -- bash

# Port forward（把 Pod 的 port 映射到本機）
kubectl port-forward pod/my-app 8080:8080
kubectl port-forward svc/my-service 8080:80

# 查看資源使用量
kubectl top nodes
kubectl top pods
```

### Namespace 操作

```bash
# 列出 namespace
kubectl get namespaces

# 建立 namespace
kubectl create namespace staging

# 在特定 namespace 操作
kubectl get pods -n staging
kubectl apply -f deploy.yaml -n staging

# 切換預設 namespace
kubectl config set-context --current --namespace=staging
```

---

## 實際部署流程範例

```bash
# 1. 建立 namespace
kubectl create namespace production

# 2. 建立 ConfigMap
kubectl create configmap app-config \
  --from-literal=DB_HOST=db.example.com \
  --from-literal=LOG_LEVEL=info \
  -n production

# 3. 建立 Secret
kubectl create secret generic app-secrets \
  --from-literal=DB_PASSWORD=supersecret \
  -n production

# 4. 部署應用
kubectl apply -f deployment.yaml -n production

# 5. 建立 Service
kubectl apply -f service.yaml -n production

# 6. 確認狀態
kubectl get all -n production
```

---

## OpenShift vs 純 Kubernetes

Red Hat OpenShift 是基於 K8s 的企業平台，加了很多東西：

| 功能 | K8s | OpenShift |
|------|-----|-----------|
| Container Registry | 需自己裝 | 內建 |
| CI/CD | 需自己裝 | 內建（Tekton） |
| Web Console | Dashboard（基本） | 完整管理介面 |
| 安全性 | 需自己設定 | 預設更嚴格（SCC） |
| Route | 用 Ingress | 有自己的 Route 資源 |
| 認證 | 基本 RBAC | 整合 OAuth、LDAP |
| CLI | kubectl | oc（相容 kubectl） |

### oc 指令（OpenShift CLI）

```bash
# 登入
oc login https://api.cluster.example.com:6443

# oc 大部分和 kubectl 一樣
oc get pods
oc describe deployment my-app
oc logs my-pod

# OpenShift 特有
oc new-project my-project        # 建立 project（= namespace + 更多）
oc new-app nginx                 # 快速建立應用
oc expose svc/my-app             # 建立 Route（對外 URL）
oc start-build my-app            # 觸發建置
```

---

## 學習路徑建議

1. **先學 Docker** — 搞懂 container 是什麼
2. **理解 Pod、Deployment、Service** — K8s 的三個基本元件
3. **練習 kubectl** — 建立、刪除、除錯
4. **學 YAML 寫法** — 看得懂、寫得出部署檔
5. **ConfigMap / Secret** — 管理設定與密碼
6. **Ingress** — 對外服務路由
7. **Persistent Volume** — 資料持久化
8. **HPA / Resource limits** — 資源管理與自動擴展
9. **RBAC** — 權限控管
10. **Helm** — 套件管理工具（像 K8s 的 apt/yum）

### 本機練習環境

```bash
# minikube — 單節點 K8s
brew install minikube
minikube start

# kind — 用 Docker 跑 K8s（輕量）
brew install kind
kind create cluster

# k3s — 輕量級 K8s（適合 VM 練習）
curl -sfL https://get.k3s.io | sh -
```
