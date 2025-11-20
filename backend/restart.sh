#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "重启 EcomImagePro Backend 服务..."

# 停止服务
if [ -f "stop.sh" ]; then
    bash stop.sh
else
    echo "未找到 stop.sh，尝试直接停止..."
    if [ -f "app.pid" ]; then
        PID=$(cat app.pid)
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID" 2>/dev/null
            rm -f app.pid
        fi
    fi
fi

# 等待一下
sleep 2

# 启动服务
bash start.sh

