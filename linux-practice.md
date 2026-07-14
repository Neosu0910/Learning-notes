# Linux 練習題（從零開始）

> 假設你什麼都不會，一步一步跟著做。每個練習都有明確的步驟和預期結果。
> 建議在 VM（VirtualBox + Rocky Linux）或雲端機器上練習。

---

## Level 0：認識你的系統

### 練習 0-1：我在哪裡？

```bash
# 試試看這些指令，觀察輸出

# 我是誰？
whoami

# 我在哪個目錄？
pwd

# 這是什麼系統？
uname -a

# 這是什麼發行版？
cat /etc/os-release

# 現在幾點？
date

# 系統開了多久？
uptime
```

**預期結果：** 你應該能看到你的使用者名稱、目前所在路徑、系統核心版本、發行版資訊。

---

## Level 1：基本導航

### 練習 1-1：到處走走

```bash
# 回到家目錄
cd ~

# 確認在哪
pwd
# 預期輸出: /home/你的使用者名稱

# 去根目錄看看
cd /

# 列出根目錄下有什麼
ls

# 去 /tmp（暫存資料夾，可以亂搞）
cd /tmp

# 回家
cd ~

# 回到上一次去的地方（/tmp）
cd -

# 又回家
cd -
```

### 練習 1-2：列出檔案的不同方式

```bash
cd ~

# 基本列表
ls

# 詳細列表（看到權限、大小、時間）
ls -l

# 包含隱藏檔（. 開頭的）
ls -la

# 人類看得懂的大小（KB, MB）
ls -lh

# 看 /etc 底下有什麼
ls /etc

# 只看目錄
ls -d */
```

**問自己：** `ls -l` 輸出的每個欄位分別代表什麼？

---

## Level 2：建立與刪除

### 練習 2-1：建立你的練習場

```bash
# 回家目錄
cd ~

# 建立練習目錄
mkdir practice

# 進去
cd practice

# 建立多層目錄
mkdir -p projects/web/frontend
mkdir -p projects/web/backend
mkdir -p projects/mobile

# 看看結構
ls -R projects
# 預期：
# projects:
# mobile  web
# projects/web:
# backend  frontend
```

### 練習 2-2：建立和操作檔案

```bash
cd ~/practice

# 建立空檔案
touch hello.txt
touch notes.txt
touch projects/web/frontend/index.html

# 確認有建立成功
ls -la

# 寫入內容到檔案
echo "Hello Linux!" > hello.txt

# 看看內容
cat hello.txt
# 預期輸出: Hello Linux!

# 附加內容（不覆蓋）
echo "This is my second line" >> hello.txt

# 再看一次
cat hello.txt
# 預期輸出:
# Hello Linux!
# This is my second line

# 複製檔案
cp hello.txt hello_backup.txt

# 移動（重新命名）
mv notes.txt my_notes.txt

# 確認
ls
# 預期: hello.txt  hello_backup.txt  my_notes.txt  projects
```

### 練習 2-3：刪除（小心！）

```bash
cd ~/practice

# 刪除單一檔案
rm hello_backup.txt

# 確認
ls
# hello_backup.txt 應該不見了

# 建立一些暫時的東西
mkdir temp_dir
touch temp_dir/file1.txt
touch temp_dir/file2.txt

# 刪除目錄（要加 -r）
rm -r temp_dir

# 確認
ls
# temp_dir 應該不見了
```

**⚠️ 注意：** `rm` 刪除的東西不會進垃圾桶，是真的刪掉了！永遠不要用 `rm -rf /`。

---

## Level 3：檔案內容操作

### 練習 3-1：查看檔案內容

```bash
cd ~/practice

# 先建立一個有很多行的檔案
for i in $(seq 1 100); do echo "Line $i: This is a sample line" >> long_file.txt; done

# 看整個檔案（會很多）
cat long_file.txt

# 只看前 5 行
head -5 long_file.txt

# 只看後 5 行
tail -5 long_file.txt

# 分頁看（按 q 離開，空白下一頁，b 上一頁）
less long_file.txt

# 計算有幾行
wc -l long_file.txt
# 預期: 100 long_file.txt
```

### 練習 3-2：搜尋內容

```bash
cd ~/practice

# 建立一個 log 檔案
cat > app.log << 'EOF'
2024-01-01 10:00:00 INFO Server started
2024-01-01 10:01:00 INFO User login: neo
2024-01-01 10:02:00 WARNING High memory usage
2024-01-01 10:03:00 ERROR Database connection failed
2024-01-01 10:04:00 INFO Retry connection...
2024-01-01 10:05:00 ERROR Database timeout
2024-01-01 10:06:00 INFO Database reconnected
2024-01-01 10:07:00 WARNING Disk space low
2024-01-01 10:08:00 INFO User logout: neo
EOF

# 找出所有 ERROR 行
grep "ERROR" app.log
# 預期: 顯示兩行 ERROR

# 找出所有 WARNING 和 ERROR
grep -E "WARNING|ERROR" app.log

# 顯示行號
grep -n "ERROR" app.log

# 計算有幾個 ERROR
grep -c "ERROR" app.log
# 預期: 2

# 不區分大小寫搜尋
grep -i "error" app.log

# 顯示 ERROR 那一行以及前後各 1 行（context）
grep -B1 -A1 "ERROR" app.log
```

---

## Level 4：權限管理

### 練習 4-1：理解權限

```bash
cd ~/practice

# 建立一個 script
echo '#!/bin/bash' > myscript.sh
echo 'echo "Hello from script!"' >> myscript.sh

# 看它的權限
ls -l myscript.sh
# 預期類似: -rw-r--r--  (沒有 x，不能執行)

# 試著執行它
./myscript.sh
# 預期: Permission denied

# 加上執行權限
chmod +x myscript.sh

# 再看權限
ls -l myscript.sh
# 預期類似: -rwxr-xr-x  (有 x 了)

# 現在可以執行了
./myscript.sh
# 預期: Hello from script!
```

### 練習 4-2：練習 chmod 數字表示法

```bash
cd ~/practice

touch secret.txt
echo "This is confidential" > secret.txt

# 設定只有自己能讀寫
chmod 600 secret.txt
ls -l secret.txt
# 預期: -rw-------

# 設定自己讀寫執行，群組和其他人只能讀
chmod 744 secret.txt
ls -l secret.txt
# 預期: -rwxr--r--

# 設定所有人都能讀寫執行（通常不建議）
chmod 777 secret.txt
ls -l secret.txt
# 預期: -rwxrwxrwx

# 恢復合理的權限
chmod 644 secret.txt
ls -l secret.txt
# 預期: -rw-r--r--
```

**記憶口訣：**
- r=4, w=2, x=1
- 7=rwx, 6=rw-, 5=r-x, 4=r--, 0=---
- 644 = 一般檔案, 755 = 可執行檔/目錄, 600 = 私密檔案

---

## Level 5：Pipe 與重導向

### 練習 5-1：Pipe 串接指令

```bash
cd ~/practice

# 列出 /etc 底下的檔案，找出包含 "conf" 的
ls /etc | grep conf

# 計算 /etc 底下有幾個 .conf 檔
ls /etc | grep "\.conf" | wc -l

# 從 app.log 找出 ERROR，排序
grep "ERROR" app.log | sort

# 列出系統上的使用者名稱（從 /etc/passwd 取第一欄）
cat /etc/passwd | cut -d: -f1

# 計算有幾個使用者
cat /etc/passwd | cut -d: -f1 | wc -l

# 找出佔用最多空間的前 5 個項目（在 /usr）
du -sh /usr/* 2>/dev/null | sort -rh | head -5
```

### 練習 5-2：重導向

```bash
cd ~/practice

# 標準輸出寫入檔案（覆蓋）
echo "first line" > output.txt
cat output.txt
# 預期: first line

# 標準輸出附加到檔案
echo "second line" >> output.txt
cat output.txt
# 預期:
# first line
# second line

# 把指令結果存到檔案
ls -la /etc > etc_listing.txt
head -10 etc_listing.txt

# 錯誤輸出重導向（把錯誤訊息丟掉）
find / -name "*.conf" 2>/dev/null | head -10

# 標準輸出和錯誤分開存
find / -name "*.conf" > found.txt 2> errors.txt
# found.txt 有結果，errors.txt 有 "Permission denied" 之類的
```

---

## Level 6：程序管理

### 練習 6-1：查看程序

```bash
# 查看所有程序
ps aux

# 只看自己的程序
ps ux

# 找特定程序（例如 sshd）
ps aux | grep sshd

# 用 top 即時監控（按 q 離開）
top

# 查看 PID 1（系統第一個程序）
ps -p 1
```

### 練習 6-2：背景程序

```bash
cd ~/practice

# 建立一個會跑很久的 script
cat > long_task.sh << 'EOF'
#!/bin/bash
for i in $(seq 1 60); do
    echo "Working... $i/60"
    sleep 1
done
echo "Done!"
EOF
chmod +x long_task.sh

# 在前景執行（會佔住終端）
# 按 Ctrl+C 中斷

# 放到背景執行
./long_task.sh > task_output.txt &
# 會顯示 [1] 12345（job 編號和 PID）

# 查看背景工作
jobs

# 查看它的輸出
tail -f task_output.txt
# 按 Ctrl+C 停止 tail（不會停掉背景程序）

# 把背景程序拉回前景
fg %1

# 按 Ctrl+C 停掉它
```

---

## Level 7：系統服務（systemd）

### 練習 7-1：管理服務

```bash
# 查看 sshd 服務狀態
sudo systemctl status sshd

# 列出所有在執行的服務
systemctl list-units --type=service --state=running

# 查看某個服務的 log
journalctl -u sshd --no-pager | tail -20

# 查看開機相關的 log
journalctl -b | head -50
```

### 練習 7-2：建立自己的服務

```bash
# 先建立一個簡單的應用
sudo cat > /opt/hello-server.sh << 'EOF'
#!/bin/bash
while true; do
    echo "$(date) - Hello Server is running" >> /var/log/hello-server.log
    sleep 10
done
EOF
sudo chmod +x /opt/hello-server.sh

# 建立 service 檔案
sudo cat > /etc/systemd/system/hello-server.service << 'EOF'
[Unit]
Description=My Hello Server
After=network.target

[Service]
Type=simple
ExecStart=/opt/hello-server.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 載入新的 service 設定
sudo systemctl daemon-reload

# 啟動
sudo systemctl start hello-server

# 查看狀態
sudo systemctl status hello-server

# 看 log
tail -f /var/log/hello-server.log

# 設定開機自動啟動
sudo systemctl enable hello-server

# 停止
sudo systemctl stop hello-server

# 清理（練習完刪掉）
sudo systemctl disable hello-server
sudo rm /etc/systemd/system/hello-server.service
sudo rm /opt/hello-server.sh
sudo rm /var/log/hello-server.log
sudo systemctl daemon-reload
```

---

## Level 8：網路操作

### 練習 8-1：網路資訊

```bash
# 查看 IP 位址
ip addr

# 查看路由表
ip route

# 測試網路連通性
ping -c 4 google.com
# -c 4 表示只 ping 4 次

# DNS 查詢
dig google.com
nslookup google.com

# 查看哪些 port 在監聽
ss -tulnp

# 下載檔案
curl -O https://raw.githubusercontent.com/torvalds/linux/master/README
# 或
wget https://raw.githubusercontent.com/torvalds/linux/master/README

# 測試 HTTP
curl -I https://google.com    # 只看 header
curl https://httpbin.org/ip   # 看你的對外 IP
```

### 練習 8-2：網路除錯

```bash
# 追蹤封包路徑
traceroute google.com

# 查看連線狀態
ss -s    # 連線摘要

# 查看特定 port 是否有人監聽
ss -tlnp | grep :22    # 看 SSH
ss -tlnp | grep :80    # 看 HTTP

# 測試特定 port 是否可連通
# 方法 1: curl
curl -v telnet://192.168.1.1:22

# 方法 2: 直接用 bash
echo > /dev/tcp/google.com/443 && echo "Port open" || echo "Port closed"
```

---

## Level 9：磁碟管理

### 練習 9-1：查看磁碟資訊

```bash
# 磁碟使用量（human readable）
df -h

# 各目錄大小
du -sh /var/*

# 區塊裝置列表
lsblk

# 詳細磁碟資訊
sudo fdisk -l

# 找出最大的檔案（前 10 大）
sudo find / -type f -exec du -h {} + 2>/dev/null | sort -rh | head -10
```

---

## Level 10：綜合實戰題

### 實戰 10-1：Log 分析

```bash
cd ~/practice

# 建立模擬的 access log
cat > access.log << 'EOF'
192.168.1.100 - - [01/Jan/2024:10:00:00] "GET /index.html HTTP/1.1" 200
192.168.1.101 - - [01/Jan/2024:10:00:01] "GET /about.html HTTP/1.1" 200
192.168.1.100 - - [01/Jan/2024:10:00:02] "POST /login HTTP/1.1" 401
192.168.1.102 - - [01/Jan/2024:10:00:03] "GET /index.html HTTP/1.1" 200
192.168.1.100 - - [01/Jan/2024:10:00:04] "POST /login HTTP/1.1" 200
192.168.1.103 - - [01/Jan/2024:10:00:05] "GET /admin HTTP/1.1" 403
192.168.1.100 - - [01/Jan/2024:10:00:06] "GET /dashboard HTTP/1.1" 200
192.168.1.101 - - [01/Jan/2024:10:00:07] "GET /index.html HTTP/1.1" 200
192.168.1.104 - - [01/Jan/2024:10:00:08] "GET /notfound HTTP/1.1" 404
192.168.1.100 - - [01/Jan/2024:10:00:09] "POST /api/data HTTP/1.1" 500
EOF

# 題目：
# 1. 找出所有非 200 的請求
grep -v '" 200$' access.log

# 2. 統計每個 IP 出現幾次
awk '{print $1}' access.log | sort | uniq -c | sort -rn

# 3. 找出最常被存取的頁面
awk '{print $7}' access.log | sort | uniq -c | sort -rn

# 4. 找出所有 POST 請求
grep "POST" access.log

# 5. 統計各 HTTP status code 的數量
awk '{print $NF}' access.log | sort | uniq -c | sort -rn
```

### 實戰 10-2：使用者管理腳本

```bash
cd ~/practice

# 寫一個腳本，建立使用者並設定基本環境
cat > create_user.sh << 'EOF'
#!/bin/bash

# 檢查是否有 root 權限
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: Please run as root (use sudo)"
    exit 1
fi

# 檢查是否有提供使用者名稱
if [ -z "$1" ]; then
    echo "Usage: $0 <username>"
    exit 1
fi

USERNAME=$1

# 建立使用者
useradd -m -s /bin/bash "$USERNAME"
echo "User $USERNAME created"

# 建立基本目錄結構
mkdir -p /home/$USERNAME/{projects,scripts,logs}
chown -R $USERNAME:$USERNAME /home/$USERNAME

echo "Directory structure created for $USERNAME"
echo "Done!"
EOF

chmod +x create_user.sh

# 執行（需要 sudo）
# sudo ./create_user.sh testuser
# sudo userdel -r testuser   # 清理
```

### 實戰 10-3：系統健康檢查腳本

```bash
cd ~/practice

cat > health_check.sh << 'EOF'
#!/bin/bash
echo "========================================="
echo "  System Health Check - $(date)"
echo "========================================="
echo ""

echo "--- Hostname ---"
hostname
echo ""

echo "--- Uptime ---"
uptime
echo ""

echo "--- Memory Usage ---"
free -h
echo ""

echo "--- Disk Usage ---"
df -h | grep -v tmpfs
echo ""

echo "--- Top 5 CPU Processes ---"
ps aux --sort=-%cpu | head -6
echo ""

echo "--- Top 5 Memory Processes ---"
ps aux --sort=-%mem | head -6
echo ""

echo "--- Network Interfaces ---"
ip -brief addr
echo ""

echo "--- Listening Ports ---"
ss -tulnp | head -20
echo ""

echo "--- Failed Services ---"
systemctl --failed --no-pager
echo ""

echo "========================================="
echo "  Health Check Complete"
echo "========================================="
EOF

chmod +x health_check.sh
./health_check.sh
```

---

## Level 11：Cron 排程

### 練習 11-1：設定排程工作

```bash
# 查看目前的 cron 排程
crontab -l

# 編輯 cron
crontab -e

# Cron 格式：
# 分 時 日 月 星期 指令
# *  *  *  *  *    command
# |  |  |  |  |
# |  |  |  |  +--- 星期（0-7，0和7都是週日）
# |  |  |  +------ 月份（1-12）
# |  |  +--------- 日期（1-31）
# |  +------------ 小時（0-23）
# +--------------- 分鐘（0-59）

# 範例：
# 每 5 分鐘執行
# */5 * * * * /home/neo/practice/health_check.sh >> /home/neo/practice/health.log 2>&1

# 每天早上 9 點執行
# 0 9 * * * /path/to/script.sh

# 每週一早上 8 點執行
# 0 8 * * 1 /path/to/script.sh

# 每月 1 號凌晨 2 點執行
# 0 2 1 * * /path/to/backup.sh
```

---

## Level 12：SSH 實作

### 練習 12-1：SSH Key 管理

```bash
# 產生 SSH key pair
ssh-keygen -t ed25519 -C "your_email@example.com"
# 按 Enter 接受預設路徑
# 設定 passphrase（可以留空但不建議）

# 查看產生的 key
ls -la ~/.ssh/
# id_ed25519      ← 私鑰（絕對不能給別人）
# id_ed25519.pub  ← 公鑰（可以放到伺服器上）

# 看公鑰內容
cat ~/.ssh/id_ed25519.pub

# 設定 SSH config 方便連線
cat > ~/.ssh/config << 'EOF'
Host myserver
    HostName 192.168.1.100
    User neo
    Port 22
    IdentityFile ~/.ssh/id_ed25519

Host dev-server
    HostName dev.example.com
    User deploy
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
EOF

# 設定權限（SSH 對權限很敏感）
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# 之後連線只需要：
# ssh myserver
# ssh dev-server
```

---

## 練習清單 Checklist

完成每個練習後打勾：

- [ ] Level 0：能查看系統基本資訊
- [ ] Level 1：能在目錄之間導航
- [ ] Level 2：能建立、複製、移動、刪除檔案和目錄
- [ ] Level 3：能查看和搜尋檔案內容
- [ ] Level 4：能理解和修改檔案權限
- [ ] Level 5：能使用 pipe 串接指令
- [ ] Level 6：能管理程序
- [ ] Level 7：能管理 systemd 服務
- [ ] Level 8：能查看和除錯網路
- [ ] Level 9：能查看磁碟使用情況
- [ ] Level 10：能完成綜合實戰題
- [ ] Level 11：能設定 cron 排程
- [ ] Level 12：能設定 SSH

---

## 每日練習建議

每天花 30 分鐘，依照順序練習：
1. 第 1-3 天：Level 0-2（基本導航和檔案操作）
2. 第 4-5 天：Level 3-4（搜尋和權限）
3. 第 6-7 天：Level 5-6（Pipe 和程序）
4. 第 8-9 天：Level 7-8（服務和網路）
5. 第 10 天：Level 9-12（綜合練習）

反覆做到不用看筆記也能打出來為止！
