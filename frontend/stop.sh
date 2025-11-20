#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

PID_FILE="app.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "未找到PID文件，服务可能未运行"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "进程不存在 (PID: $PID)，清理PID文件"
    rm -f "$PID_FILE"
    exit 1
fi

echo "正在停止服务 (PID: $PID)..."
kill "$PID"

# 等待进程结束
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# 如果还在运行，强制杀死
if ps -p "$PID" > /dev/null 2>&1; then
    echo "强制停止服务..."
    kill -9 "$PID"
    sleep 1
fi

# 清理PID文件
rm -f "$PID_FILE"

# 尝试杀死所有相关的 node 进程（Vite开发服务器）
pkill -f "vite" 2>/dev/null

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "✓ 服务已停止"
else
    echo "✗ 停止服务失败"
    exit 1
fi

