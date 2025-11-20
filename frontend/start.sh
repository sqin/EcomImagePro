#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "未找到 node_modules，正在安装依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "错误: 依赖安装失败"
        exit 1
    fi
fi

# 检查是否已安装依赖
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到 npm，请先安装 Node.js"
    exit 1
fi

# 配置（从 vite.config.js 读取，默认 3000）
PORT=${VITE_PORT:-3000}
HOST=${VITE_HOST:-"0.0.0.0"}
LOG_FILE="logs/app.log"
PID_FILE="app.pid"

# 创建日志目录
mkdir -p logs

# 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "服务已在运行中 (PID: $OLD_PID)"
        echo "如需重启，请先运行: ./stop.sh"
        exit 1
    else
        echo "清理旧的PID文件..."
        rm -f "$PID_FILE"
    fi
fi

# 启动服务
echo "正在启动 EcomImagePro Frontend 服务..."
echo "端口: $PORT"
echo "日志文件: $LOG_FILE"

# 设置环境变量并后台运行
export VITE_PORT=$PORT
export VITE_HOST=$HOST

# 后台运行，保存PID
nohup npm run dev > "$LOG_FILE" 2>&1 &
PID=$!

# 保存PID
echo $PID > "$PID_FILE"

# 等待一下，检查服务是否成功启动
sleep 3

if ps -p "$PID" > /dev/null 2>&1; then
    echo "✓ 服务启动成功!"
    echo "  PID: $PID"
    echo "  访问地址: http://localhost:$PORT"
    echo "  日志文件: $LOG_FILE"
    echo "  停止服务: ./stop.sh 或 kill $PID"
    echo ""
    echo "提示: 如果端口被占用，可以设置环境变量:"
    echo "  VITE_PORT=3000 ./start.sh"
else
    echo "✗ 服务启动失败，请查看日志: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

