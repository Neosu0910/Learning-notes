# Linux 指令學習指南

## 什麼是 Linux？

Linux 是一個開源的作業系統核心（Kernel），搭配各種工具組成完整的作業系統（稱為 Distribution / 發行版）。伺服器領域幾乎都是 Linux，學會 Linux 指令等於拿到伺服器管理的入場券。

---

## 基本概念

### Shell 是什麼？
Shell 是你和 Linux 系統溝通的介面。你輸入指令，Shell 負責解讀並執行。最常見的 Shell 是 `bash`（Red Hat 預設）和 `zsh`（macOS 預設）。

### 檔案系統結構
Linux 的一切都是檔案，目錄結構從根目錄 `/` 開始：

```
/           ← 根目錄（最上層）
├── /home   ← 使用者的家目錄
├── /etc    ← 系統設定檔
├── /var    ← 變動資料（log、cache）
├── /tmp    ← 暫存檔案
├── /usr    ← 使用者程式與函式庫
├── /bin    ← 基本指令（ls, cp, mv...）
├── /sbin   ← 系統管理指令（需 root）
├── /opt    ← 第三方軟體安裝位置
├── /proc   ← 虛擬檔案系統（系統運行資訊）
└── /dev    ← 裝置檔案（硬碟、USB...）
```

---

## 檔案與目錄操作

### 導航

| 指令 | 功能 | 範例 |
|------|------|------|
| `pwd` | 顯示目前所在目錄 | `pwd` → `/home/neo` |
| `cd` | 切換目錄 | `cd /var/log` |
| `cd ..` | 回上一層 | `cd ..` |
| `cd ~` | 回家目錄 | `cd ~` |
| `cd -` | 回到上一次的目錄 | `cd -` |

### 列出檔案

| 指令 | 功能 | 範例 |
|------|------|------|
| `ls` | 列出目錄內容 | `ls` |
| `ls -l` | 詳細列表（權限、大小、時間） | `ls -l` |
| `ls -la` | 包含隱藏檔 | `ls -la` |
| `ls -lh` | 人類可讀的檔案大小 | `ls -lh` |
| `ls -R` | 遞迴列出子目錄 | `ls -R /etc` |

### 建立與刪除

| 指令 | 功能 | 範例 |
|------|------|------|
| `mkdir` | 建立目錄 | `mkdir projects` |
| `mkdir -p` | 建立多層目錄 | `mkdir -p a/b/c` |
| `touch` | 建立空檔案 | `touch hello.txt` |
| `rm` | 刪除檔案 | `rm hello.txt` |
| `rm -r` | 刪除目錄（遞迴） | `rm -r projects` |
| `rm -rf` | 強制刪除（不詢問） | `rm -rf /tmp/test` |
| `rmdir` | 刪除空目錄 | `rmdir empty_dir` |

### 複製與移動

| 指令 | 功能 | 範例 |
|------|------|------|
| `cp` | 複製檔案 | `cp a.txt b.txt` |
| `cp -r` | 複製目錄 | `cp -r dir1 dir2` |
| `mv` | 移動 / 重新命名 | `mv old.txt new.txt` |

---

## 檔案內容查看

| 指令 | 功能 | 適用情境 |
|------|------|----------|
| `cat` | 顯示整個檔案 | 短檔案 |
| `less` | 分頁瀏覽（可上下捲動） | 長檔案 |
| `more` | 分頁瀏覽（只能往下） | 長檔案 |
| `head` | 顯示前 N 行 | `head -20 file.log` |
| `tail` | 顯示後 N 行 | `tail -20 file.log` |
| `tail -f` | 即時追蹤檔案更新 | 看 log 用 |
| `wc` | 計算行數/字數/字元數 | `wc -l file.txt` |

---

## 搜尋

### find — 找檔案
```bash
# 在 /home 底下找所有 .txt 檔案
find /home -name "*.txt"

# 找 7 天內修改過的檔案
find /var/log -mtime -7

# 找大於 100MB 的檔案
find / -size +100M

# 找到後刪除
find /tmp -name "*.tmp" -delete
```

### grep — 在檔案內容中搜尋
```bash
# 在 file.txt 中搜尋 "error"
grep "error" file.txt

# 忽略大小寫
grep -i "error" file.txt

# 遞迴搜尋整個目錄
grep -r "TODO" /home/neo/projects

# 顯示行號
grep -n "error" file.txt

# 反向搜尋（顯示不包含 "error" 的行）
grep -v "error" file.txt
```

---

## 權限管理

### 理解權限字串
```
-rwxr-xr--  1  neo  devops  4096  Jul 14 10:00  script.sh
│├──┤├──┤├──┤
│ │    │    │
│ │    │    └── 其他人(other): r-- (只讀)
│ │    └────── 群組(group): r-x (讀+執行)
│ └─────────── 擁有者(user): rwx (讀+寫+執行)
└───────────── 檔案類型: - 普通檔案, d 目錄, l 連結
```

### chmod — 改權限
```bash
# 數字表示法: r=4, w=2, x=1
chmod 755 script.sh    # user:rwx, group:r-x, other:r-x
chmod 644 config.txt   # user:rw-, group:r--, other:r--
chmod 600 secret.key   # user:rw-, group:---, other:---

# 符號表示法
chmod u+x script.sh    # 給擁有者加上執行權限
chmod g-w file.txt     # 移除群組的寫入權限
chmod o-rwx secret     # 移除其他人所有權限
chmod a+r public.html  # 所有人加上讀取權限
```

### chown — 改擁有者
```bash
chown neo file.txt           # 改擁有者為 neo
chown neo:devops file.txt    # 改擁有者和群組
chown -R neo:devops /app     # 遞迴改整個目錄
```

---

## 使用者與群組

| 指令 | 功能 | 範例 |
|------|------|------|
| `whoami` | 目前登入的使用者 | `whoami` |
| `id` | 顯示 UID、GID、群組 | `id neo` |
| `useradd` | 新增使用者 | `sudo useradd neo` |
| `passwd` | 設定密碼 | `sudo passwd neo` |
| `usermod` | 修改使用者 | `sudo usermod -aG docker neo` |
| `userdel` | 刪除使用者 | `sudo userdel neo` |
| `groupadd` | 新增群組 | `sudo groupadd devops` |
| `groups` | 查看使用者所屬群組 | `groups neo` |

---

## 程序管理

| 指令 | 功能 | 範例 |
|------|------|------|
| `ps` | 列出程序 | `ps aux` |
| `ps aux` | 列出所有程序（詳細） | `ps aux \| grep nginx` |
| `top` | 即時監控程序 | `top` |
| `htop` | 更好看的 top | `htop` |
| `kill` | 終止程序 | `kill 1234` |
| `kill -9` | 強制終止 | `kill -9 1234` |
| `killall` | 以名稱終止程序 | `killall nginx` |
| `bg` | 將程序放到背景執行 | `bg` |
| `fg` | 將背景程序拉回前景 | `fg` |
| `jobs` | 列出背景工作 | `jobs` |
| `nohup` | 讓程序不隨終端關閉而結束 | `nohup ./script.sh &` |

---

## 網路相關

| 指令 | 功能 | 範例 |
|------|------|------|
| `ip addr` | 查看 IP 位址 | `ip addr` |
| `ip route` | 查看路由表 | `ip route` |
| `ping` | 測試網路連通性 | `ping google.com` |
| `curl` | 發送 HTTP 請求 | `curl https://api.example.com` |
| `wget` | 下載檔案 | `wget https://example.com/file.tar.gz` |
| `ss` | 查看網路連線（取代 netstat） | `ss -tulnp` |
| `netstat` | 查看網路連線（舊） | `netstat -tulnp` |
| `traceroute` | 追蹤封包路徑 | `traceroute google.com` |
| `dig` | DNS 查詢 | `dig example.com` |
| `nslookup` | DNS 查詢（互動式） | `nslookup example.com` |
| `hostname` | 查看/設定主機名稱 | `hostname` |

---

## 磁碟與儲存

| 指令 | 功能 | 範例 |
|------|------|------|
| `df -h` | 查看磁碟使用量 | `df -h` |
| `du -sh` | 查看目錄/檔案大小 | `du -sh /var/log` |
| `du -sh *` | 列出當前目錄各項大小 | `du -sh *` |
| `lsblk` | 列出區塊裝置 | `lsblk` |
| `mount` | 掛載檔案系統 | `mount /dev/sdb1 /mnt/data` |
| `umount` | 卸載 | `umount /mnt/data` |
| `fdisk` | 磁碟分割 | `fdisk /dev/sdb` |

---

## 壓縮與打包

```bash
# tar — 打包（不壓縮）
tar cf archive.tar files/

# tar + gzip 壓縮
tar czf archive.tar.gz files/

# 解壓縮 tar.gz
tar xzf archive.tar.gz

# 解壓縮到指定目錄
tar xzf archive.tar.gz -C /opt/

# zip
zip -r archive.zip directory/
unzip archive.zip
```

---

## Pipe 與重導向

```bash
# | (pipe) — 把前一個指令的輸出傳給下一個指令
ps aux | grep nginx
cat access.log | sort | uniq -c | sort -rn | head -10

# > — 輸出重導向（覆蓋）
echo "hello" > file.txt

# >> — 輸出重導向（附加）
echo "world" >> file.txt

# < — 輸入重導向
sort < unsorted.txt

# 2> — 錯誤輸出重導向
find / -name "*.conf" 2> /dev/null

# &> — 標準輸出 + 錯誤輸出都重導向
command &> output.log
```

---

## 系統服務管理（systemd）

```bash
# 啟動/停止/重啟服務
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx

# 查看服務狀態
sudo systemctl status nginx

# 設定開機自動啟動
sudo systemctl enable nginx
sudo systemctl disable nginx

# 重新載入設定（不重啟）
sudo systemctl reload nginx

# 列出所有服務
systemctl list-units --type=service

# 查看服務的 log
journalctl -u nginx
journalctl -u nginx -f    # 即時追蹤
journalctl -u nginx --since "1 hour ago"
```

---

## 環境變數

```bash
# 查看所有環境變數
env

# 查看特定變數
echo $PATH
echo $HOME

# 設定變數（只在當前 session 有效）
export MY_VAR="hello"

# 永久設定（加到 ~/.bashrc 或 ~/.bash_profile）
echo 'export MY_VAR="hello"' >> ~/.bashrc
source ~/.bashrc

# PATH 變數 — 系統去哪裡找執行檔
export PATH=$PATH:/opt/myapp/bin
```

---

## 文字處理工具

```bash
# sort — 排序
sort file.txt
sort -n numbers.txt    # 數字排序
sort -r file.txt       # 反向排序

# uniq — 去重（需先排序）
sort file.txt | uniq
sort file.txt | uniq -c    # 計數

# cut — 切割欄位
cut -d':' -f1 /etc/passwd    # 用 : 分隔，取第 1 欄

# awk — 強大的文字處理
awk '{print $1}' file.txt              # 印出每行第一欄
awk -F: '{print $1, $3}' /etc/passwd   # 用 : 分隔

# sed — 文字替換
sed 's/old/new/g' file.txt             # 全部替換
sed -i 's/old/new/g' file.txt          # 直接修改檔案
```

---

## SSH 遠端連線

```bash
# 基本連線
ssh user@192.168.1.100
ssh -p 2222 user@server.com    # 指定 port

# 產生 SSH key
ssh-keygen -t ed25519 -C "neo@company.com"

# 複製公鑰到遠端（之後免密碼登入）
ssh-copy-id user@server.com

# SCP — 透過 SSH 複製檔案
scp file.txt user@server:/home/user/
scp -r directory/ user@server:/home/user/
scp user@server:/var/log/app.log ./

# SSH config（~/.ssh/config）簡化連線
# Host myserver
#     HostName 192.168.1.100
#     User neo
#     Port 22
#     IdentityFile ~/.ssh/id_ed25519
# 之後只需要: ssh myserver
```

---

## 實用組合技

```bash
# 找出佔用最多空間的前 10 個目錄
du -sh /* 2>/dev/null | sort -rh | head -10

# 查看哪個 port 被誰佔用
ss -tulnp | grep :80

# 即時監控 log 並 highlight 關鍵字
tail -f /var/log/syslog | grep --color "error"

# 批次重新命名
for f in *.txt; do mv "$f" "${f%.txt}.md"; done

# 查看系統資訊
uname -a           # 核心版本
cat /etc/os-release  # 發行版資訊
free -h            # 記憶體使用量
uptime             # 開機時間與負載
```

---

## 下一步學習建議

1. 先熟練基本操作（cd, ls, cat, grep, find）
2. 練習權限管理（chmod, chown）— 工作中天天會用
3. 學會 systemd 管理服務
4. 練習 pipe 組合多個指令
5. 接著學 → Red Hat（`redhat-guide.md`）和 K8s（`k8s-guide.md`）
