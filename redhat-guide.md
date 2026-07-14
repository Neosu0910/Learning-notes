# Red Hat Enterprise Linux (RHEL) 學習指南

## 什麼是 Red Hat？

Red Hat 是一家專注於企業級開源軟體的公司（已被 IBM 收購）。他們的核心產品是 **RHEL (Red Hat Enterprise Linux)**，是企業伺服器最常用的 Linux 發行版之一。

### 為什麼企業選 RHEL？
- **穩定性**：每個版本支援 10 年，不會像 Ubuntu 那樣頻繁更新
- **商業支援**：出問題有 Red Hat 工程師幫你
- **安全性**：有 SELinux、定期安全補丁
- **認證生態**：很多商用軟體只認證在 RHEL 上跑

### RHEL vs CentOS vs Rocky Linux vs Fedora

| 發行版 | 定位 | 費用 | 說明 |
|--------|------|------|------|
| RHEL | 企業生產環境 | 付費訂閱 | 有官方支援 |
| CentOS Stream | RHEL 上游測試版 | 免費 | 比 RHEL 早一步的版本 |
| Rocky Linux | RHEL 相容替代品 | 免費 | CentOS 停止後的替代 |
| AlmaLinux | RHEL 相容替代品 | 免費 | 另一個 CentOS 替代 |
| Fedora | 最新技術試驗場 | 免費 | 桌面/開發用，更新快 |

---

## 套件管理：DNF / YUM

RHEL 系列使用 RPM（Red Hat Package Manager）格式的套件，透過 `dnf`（或舊版 `yum`）來管理。

### 基本操作

```bash
# 安裝套件
sudo dnf install nginx

# 移除套件
sudo dnf remove nginx

# 更新所有套件
sudo dnf update

# 更新特定套件
sudo dnf update nginx

# 搜尋套件
dnf search "web server"

# 查看套件資訊
dnf info nginx

# 列出已安裝的套件
dnf list installed

# 列出可用的套件
dnf list available

# 查看某個檔案屬於哪個套件
dnf provides /usr/sbin/nginx
```

### 套件群組

```bash
# 列出可用的套件群組
dnf group list

# 安裝整組套件（例如開發工具）
sudo dnf group install "Development Tools"

# 查看群組包含哪些套件
dnf group info "Development Tools"
```

### Repository 管理

```bash
# 列出所有 repo
dnf repolist
dnf repolist all    # 包含停用的

# 啟用/停用 repo
sudo dnf config-manager --enable epel
sudo dnf config-manager --disable epel

# 新增 EPEL repo（Extra Packages for Enterprise Linux）
sudo dnf install epel-release
```

---

## SELinux（Security-Enhanced Linux）

SELinux 是 RHEL 的強制存取控制（MAC）系統，用來限制程序能存取哪些資源。這是 RHEL 和其他發行版最大的差異之一。

### 三種模式

| 模式 | 說明 | 指令 |
|------|------|------|
| Enforcing | 強制執行，違規會被阻擋 | `setenforce 1` |
| Permissive | 只記錄違規，不阻擋 | `setenforce 0` |
| Disabled | 完全關閉 | 修改 `/etc/selinux/config` |

### 常用指令

```bash
# 查看目前模式
getenforce
sestatus

# 暫時切換模式（重開機會恢復）
sudo setenforce 0    # 切到 permissive
sudo setenforce 1    # 切到 enforcing

# 永久修改（需重開機）
sudo vi /etc/selinux/config
# 改 SELINUX=permissive 或 SELINUX=enforcing

# 查看檔案的 SELinux context
ls -Z /var/www/html/

# 查看程序的 SELinux context
ps -eZ | grep nginx

# 修改檔案的 context（常見問題：新檔案 context 不對導致存取被擋）
sudo chcon -t httpd_sys_content_t /var/www/html/index.html

# 還原預設 context
sudo restorecon -Rv /var/www/html/

# 查看 SELinux 的 boolean（開關）
getsebool -a | grep httpd

# 修改 boolean
sudo setsebool -P httpd_can_network_connect on
```

### 常見 SELinux 問題排除

```bash
# 查看 SELinux 拒絕的 log
sudo ausearch -m avc -ts recent

# 用 audit2why 分析原因
sudo ausearch -m avc -ts recent | audit2why

# 用 audit2allow 產生允許規則
sudo ausearch -m avc -ts recent | audit2allow -M mypolicy
sudo semodule -i mypolicy.pp
```

---

## Firewalld 防火牆

RHEL 預設使用 `firewalld`（而不是 iptables）。

```bash
# 查看狀態
sudo firewall-cmd --state

# 查看目前規則
sudo firewall-cmd --list-all

# 查看所有 zone
sudo firewall-cmd --get-zones
sudo firewall-cmd --get-active-zones

# 開放 port（暫時，重啟後消失）
sudo firewall-cmd --add-port=8080/tcp

# 開放 port（永久）
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload

# 開放服務（永久）
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --add-service=https --permanent
sudo firewall-cmd --reload

# 移除規則
sudo firewall-cmd --remove-port=8080/tcp --permanent
sudo firewall-cmd --reload

# 列出可用的服務名稱
sudo firewall-cmd --get-services
```

---

## 系統管理

### systemd 服務管理

```bash
# RHEL 9 全面使用 systemd
systemctl start/stop/restart/status nginx
systemctl enable/disable nginx

# 查看啟動失敗的服務
systemctl --failed

# 查看服務的完整設定
systemctl cat nginx

# 編輯服務設定（建立 override）
sudo systemctl edit nginx

# 重新載入 systemd 設定
sudo systemctl daemon-reload
```

### 建立自訂 service

```bash
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/run.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now myapp
```

### 日誌管理（journald）

```bash
# 查看系統日誌
journalctl

# 查看特定服務的 log
journalctl -u nginx

# 即時追蹤
journalctl -u nginx -f

# 查看今天的 log
journalctl --since today

# 查看開機 log
journalctl -b

# 查看上次開機 log
journalctl -b -1

# 查看指定時間範圍
journalctl --since "2024-01-01" --until "2024-01-02"

# 只看錯誤
journalctl -p err
```

---

## 網路設定（NetworkManager）

RHEL 使用 NetworkManager 管理網路，CLI 工具是 `nmcli`。

```bash
# 查看連線狀態
nmcli general status
nmcli connection show
nmcli device status

# 查看特定介面的詳細設定
nmcli connection show "ens192"

# 設定靜態 IP
sudo nmcli connection modify "ens192" \
  ipv4.addresses 192.168.1.100/24 \
  ipv4.gateway 192.168.1.1 \
  ipv4.dns "8.8.8.8,8.8.4.4" \
  ipv4.method manual

# 套用設定
sudo nmcli connection up "ens192"

# 改回 DHCP
sudo nmcli connection modify "ens192" ipv4.method auto
sudo nmcli connection up "ens192"

# 新增連線
sudo nmcli connection add type ethernet con-name "my-eth" ifname ens192

# 查看 DNS 設定
cat /etc/resolv.conf
nmcli device show | grep DNS
```

---

## 儲存管理（LVM）

LVM（Logical Volume Manager）讓你可以彈性管理磁碟空間，不需要重新分割。

### 概念

```
Physical Volume (PV)  →  實體硬碟或分割區
       ↓
Volume Group (VG)     →  把多個 PV 合成一個池子
       ↓
Logical Volume (LV)   →  從池子中切出來的邏輯分區
       ↓
Filesystem            →  在 LV 上建立檔案系統（ext4, xfs）
```

### 常用操作

```bash
# 查看現有 LVM 結構
pvs          # Physical Volumes
vgs          # Volume Groups
lvs          # Logical Volumes

# 建立 PV
sudo pvcreate /dev/sdb

# 建立 VG
sudo vgcreate data_vg /dev/sdb

# 建立 LV（10GB）
sudo lvcreate -L 10G -n app_lv data_vg

# 格式化
sudo mkfs.xfs /dev/data_vg/app_lv

# 掛載
sudo mkdir /app
sudo mount /dev/data_vg/app_lv /app

# 加到 /etc/fstab 開機自動掛載
echo '/dev/data_vg/app_lv /app xfs defaults 0 0' | sudo tee -a /etc/fstab

# 擴展 LV
sudo lvextend -L +5G /dev/data_vg/app_lv
sudo xfs_growfs /app    # XFS 用這個擴展檔案系統
# 或
sudo resize2fs /dev/data_vg/app_lv    # ext4 用這個
```

---

## 使用者與安全

### sudo 設定

```bash
# 編輯 sudoers（永遠用 visudo）
sudo visudo

# 讓使用者可以用 sudo
neo ALL=(ALL) ALL

# 讓使用者 sudo 不需密碼
neo ALL=(ALL) NOPASSWD: ALL

# 讓群組可以 sudo
%devops ALL=(ALL) ALL
```

### SSH 安全加固

```bash
# /etc/ssh/sshd_config 常見設定
PermitRootLogin no              # 禁止 root SSH 登入
PasswordAuthentication no       # 只允許 key 登入
Port 2222                       # 改 port（可選）
AllowUsers neo admin            # 只允許特定使用者

# 修改後重啟
sudo systemctl restart sshd
```

---

## RHEL 訂閱管理

```bash
# 註冊系統
sudo subscription-manager register --username=your_username

# 附加訂閱
sudo subscription-manager attach --auto

# 查看訂閱狀態
sudo subscription-manager status
sudo subscription-manager list --consumed

# 列出可用 repo
sudo subscription-manager repos --list

# 啟用特定 repo
sudo subscription-manager repos --enable=rhel-9-for-x86_64-appstream-rpms
```

---

## 重要設定檔位置

| 檔案 | 用途 |
|------|------|
| `/etc/hostname` | 主機名稱 |
| `/etc/hosts` | 本地 DNS 對應 |
| `/etc/resolv.conf` | DNS 設定 |
| `/etc/fstab` | 開機自動掛載 |
| `/etc/passwd` | 使用者帳號 |
| `/etc/shadow` | 使用者密碼（加密） |
| `/etc/group` | 群組資訊 |
| `/etc/sudoers` | sudo 權限設定 |
| `/etc/ssh/sshd_config` | SSH 服務設定 |
| `/etc/selinux/config` | SELinux 設定 |
| `/etc/firewalld/` | 防火牆設定 |
| `/etc/yum.repos.d/` | 套件庫設定 |
| `/var/log/messages` | 系統日誌 |
| `/var/log/secure` | 認證相關日誌 |

---

## RHCSA 認證簡介

**RHCSA（Red Hat Certified System Administrator）** 是 Red Hat 的入門級認證，證明你有能力管理 RHEL 系統。

### 考試重點
- 使用者/群組管理
- 檔案權限與 ACL
- SELinux 設定
- 防火牆設定
- LVM 管理
- 系統服務管理（systemd）
- 排程工作（cron, at）
- 網路設定
- NFS/Autofs 掛載
- Container 基礎（podman）

### 學習建議
1. 裝一台 RHEL 或 Rocky Linux VM 實際操作
2. 每個指令都要親手打過，不要只看
3. 練習在限時內完成任務（考試 2.5 小時）
