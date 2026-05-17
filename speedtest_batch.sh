#!/bin/bash

# Ensure HOME environment variable is set (required by Ookla Speedtest CLI to avoid C++ crash under systemd/cron)
export HOME="${HOME:-/root}"

# Load server IDs from generated file
SERVER_IDS_FILE="./speedtest_server_ids.txt"

if [[ ! -f "$SERVER_IDS_FILE" ]]; then
    echo "Missing: $SERVER_IDS_FILE"
    echo "Run first: python3 get_speedtest_servers.py"
    exit 1
fi

mapfile -t servers < <(
    grep -v '^#' "$SERVER_IDS_FILE" \
    | grep -v '^$' \
    | awk '{print $1}'
)

if [[ ${#servers[@]} -eq 0 ]]; then
    echo "No server IDs found in $SERVER_IDS_FILE"
    exit 1
fi

echo "Loaded ${#servers[@]} server IDs from $SERVER_IDS_FILE"

# Sequential index file
current_index_file=".speedtest_server_index"

if [[ ! -f "$current_index_file" ]]; then
    echo 0 > "$current_index_file"
fi

# Random sleep range
min_sleep=450
max_sleep=900

# Telegram config
TELEGRAM_BOT_TOKEN="8781656242:AAHk6ZgAADgoCgwzRsKPqDkgtDo_kRjrDto"
TELEGRAM_CHAT_ID="7381939387"

# Log file
log_file="./speedtest_log.txt"

echo "=== Speedtest Auto Runner Started ===" | tee -a "$log_file"

while true; do
    current_index=$(cat "$current_index_file")

    if ! [[ "$current_index" =~ ^[0-9]+$ ]]; then
        current_index=0
    fi

    if (( current_index >= ${#servers[@]} )); then
        current_index=0
    fi

    server_id=${servers[$current_index]}

    next_index=$((current_index + 1))
    echo "$next_index" > "$current_index_file"

    echo "------------------------------------------" | tee -a "$log_file"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Running speedtest on server ID: $server_id" | tee -a "$log_file"
    echo "Server index: $((current_index + 1)) / ${#servers[@]}" | tee -a "$log_file"
    echo "------------------------------------------" | tee -a "$log_file"

    tmp_speedtest="./.speedtest_result.tmp"

    speedtest --accept-license --accept-gdpr -s "$server_id" | tee "$tmp_speedtest" | tee -a "$log_file"

    if [[ -n "$TELEGRAM_BOT_TOKEN" && "$TELEGRAM_BOT_TOKEN" != "YOUR_BOT_TOKEN" && -n "$TELEGRAM_CHAT_ID" && "$TELEGRAM_CHAT_ID" != "YOUR_CHAT_ID" ]]; then

        url_line=$(grep -E "(Result URL|Share results):" "$tmp_speedtest")
        result_url=$(echo "$url_line" | grep -oE "https?://[a-zA-Z0-9./_-]+")

        clean_output=$(grep -vE "(Result URL|Share results):" "$tmp_speedtest" | sed 's/[[:space:]]*$//')

        echo "$clean_output" > .speedtest_clean.tmp

        image_generated=false

        if command -v freeze &> /dev/null; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Generating image with freeze..." >> "$log_file"

            freeze --language text \
                --theme nord \
                --font.size 28 \
                --margin 0 \
                --padding 15 \
                -o speedtest_result.png \
                .speedtest_clean.tmp >> "$log_file" 2>&1

            [[ -s "speedtest_result.png" ]] && image_generated=true
        fi

        rm -f .speedtest_clean.tmp

        if [[ "$image_generated" == true ]]; then

            actual_server_id=$(grep -oE '\(id: [0-9]+\)' "$tmp_speedtest" | grep -oE '[0-9]+' | head -n1)

            if [[ -z "$actual_server_id" ]]; then
                actual_server_id="$server_id"
            fi

            server_info=$(awk -v id="$actual_server_id" '/^# /{country=substr($0,3);next} $1==id{$1="";sub(/^ # /,"");print country " | " $0;exit}' "$SERVER_IDS_FILE")

            if [[ -z "$server_info" ]]; then
                server_info="Unknown"
            fi

            caption="<b>Speedtest</b> (${server_info} | Server ID: <code>$actual_server_id</code>)"

            if [[ -n "$result_url" ]]; then
                caption="$caption

Result URL: $result_url"
            fi

            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sending photo to Telegram..." >> "$log_file"

            export TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID caption

            python3 -c '
import urllib.request
import os
import uuid

token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")
caption = os.environ.get("caption")

url = f"https://api.telegram.org/bot{token}/sendPhoto"
boundary = uuid.uuid4().hex

body = bytearray()

body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n".encode("utf-8"))
body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"parse_mode\"\r\n\r\nHTML\r\n".encode("utf-8"))

if caption:
    body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption}\r\n".encode("utf-8"))

body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"speedtest.png\"\r\nContent-Type: image/png\r\n\r\n".encode("utf-8"))

with open("speedtest_result.png", "rb") as f:
    body.extend(f.read())

body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

req = urllib.request.Request(
    url,
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
)

try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except Exception as e:
    if hasattr(e, "read"):
        print("Python upload error:", e, e.read().decode())
    else:
        print("Python upload error:", e)
' >> "$log_file" 2>&1

            rm -f "speedtest_result.png"

        else
            actual_server_id=$(grep -oE '\(id: [0-9]+\)' "$tmp_speedtest" | grep -oE '[0-9]+' | head -n1)

            if [[ -z "$actual_server_id" ]]; then
                actual_server_id="$server_id"
            fi

            server_info=$(awk -v id="$actual_server_id" '/^# /{country=substr($0,3);next} $1==id{$1="";sub(/^ # /,"");print country " | " $0;exit}' "$SERVER_IDS_FILE")

            if [[ -z "$server_info" ]]; then
                server_info="Unknown"
            fi

            escaped_output=$(echo "$clean_output" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')

            telegram_text="<b>Speedtest</b> (${server_info} | Server ID: <code>$actual_server_id</code>):
<blockquote><pre>$escaped_output</pre></blockquote>"

            if [[ -n "$result_url" ]]; then
                telegram_text="$telegram_text

Result URL: $result_url"
            fi

            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Image failed or freeze not found, sending text fallback to Telegram..." >> "$log_file"

            curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
                -d chat_id="${TELEGRAM_CHAT_ID}" \
                -d parse_mode="HTML" \
                --data-urlencode text="$telegram_text" >> "$log_file" 2>&1
        fi
    fi

    rm -f "$tmp_speedtest"

    sleep_time=$((RANDOM % (max_sleep - min_sleep + 1) + min_sleep))

    echo "Sleeping for $sleep_time seconds..." | tee -a "$log_file"

    for ((i=sleep_time; i>0; i--)); do
        echo -ne "Next test in: $i seconds...\r"
        sleep 1
    done

    echo -e "\n" | tee -a "$log_file"
done