# Speedtest Auto Runner

Automated Speedtest runner using Ookla Speedtest CLI with:

- worldwide Speedtest server extraction
- sequential server rotation
- Telegram reporting
- auto image generation using `freeze`
- systemd auto-start on reboot
- persistent server rotation state

---

# Files

```text
get_speedtest_servers.py
speedtest_batch.sh
speedtest_server_ids.txt
speedtest_servers_by_country.json
speedtest_server_ids_by_country.json
missing_countries.json
```

---

# Features

- Extracts Speedtest servers worldwide
- Selects 3 random servers per country
- Sequentially rotates through server IDs
- Random sleep between tests
- Sends result image to Telegram
- Auto restart on crash
- Auto start after reboot
- Logs all activity

---

# Requirements

Ubuntu 22.04+ recommended

Install dependencies:

```bash
apt update

apt install -y \
    curl \
    jq \
    gawk \
    coreutils \
    python3 \
    python3-pip \
    speedtest \
    nodejs \
    npm
```

Install freeze:

```bash
npm install -g freeze-cli
```

---

# Generate Server List

Run:

```bash
python3 get_speedtest_servers.py
```

Generated files:

```text
speedtest_servers_by_country.json
speedtest_server_ids_by_country.json
speedtest_server_ids.txt
missing_countries.json
```

---

# Configure Telegram

Edit:

```bash
nano speedtest_batch.sh
```

Update:

```bash
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
```

---

# Run Manually

```bash
chmod +x speedtest_batch.sh
./speedtest_batch.sh
```

---

# Run In Background

```bash
nohup ./speedtest_batch.sh > nohup.out 2>&1 &
```

Check:

```bash
pgrep -af speedtest
```

Stop:

```bash
pkill -9 -f speedtest_batch.sh
pkill -9 -f '/snap/speedtest'
```

---

# Setup Auto Start On Boot

Create service:

```bash
nano /etc/systemd/system/speedtest-auto.service
```

Paste:

```ini
[Unit]
Description=Run Speedtest Batch Script on Boot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/root
ExecStart=/bin/bash /root/speedtest_batch.sh

StandardOutput=journal
StandardError=journal

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
systemctl daemon-reload
systemctl enable speedtest-auto.service
systemctl start speedtest-auto.service
```

---

# Service Management

Check status:

```bash
systemctl status speedtest-auto.service
```

Live logs:

```bash
journalctl -u speedtest-auto.service -f
```

Restart:

```bash
systemctl restart speedtest-auto.service
```

Stop:

```bash
systemctl stop speedtest-auto.service
```

Disable:

```bash
systemctl disable speedtest-auto.service
```

---

# Logs

Main log:

```bash
tail -f speedtest_log.txt
```

Systemd logs:

```bash
journalctl -u speedtest-auto.service -f
```

---

# Server Rotation

Behavior:

- sequential server rotation
- persistent index state
- random sleep interval
- auto restart if crash

Index file:

```text
.speedtest_server_index
```

---

# Sleep Timing

Configured in:

```bash
min_sleep=300
max_sleep=600
```

Meaning:

- minimum 5 minutes
- maximum 10 minutes

---

# Telegram Caption Example

```text
Speedtest (Singapore (SG) | Verizon / Singapore | Server ID: 50406)
```

---

# Important Notes

- `speedtest_server_ids.txt` must exist before running batch script
- run extractor first
- systemd service assumes files are in `/root`
- Speedtest CLI must be installed
- Telegram bot token should remain private

---

# Workflow

```bash
python3 get_speedtest_servers.py
systemctl restart speedtest-auto.service
```

---

# Troubleshooting

Check running processes:

```bash
pgrep -af speedtest
```

Kill all:

```bash
pkill -9 -f speedtest_batch.sh
pkill -9 -f '/snap/speedtest'
```

Check logs:

```bash
tail -f speedtest_log.txt
```

Check server index:

```bash
cat .speedtest_server_index
```
