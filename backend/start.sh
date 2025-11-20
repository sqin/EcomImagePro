#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查虚拟环境是否存在
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
else
    echo "警告: 未找到虚拟环境 venv，使用系统Python"
fi

# 检查是否已安装依赖
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "错误: 未找到 uvicorn，请先安装依赖: pip install -r requirements.txt"
    exit 1
fi

# 配置
PORT=9000
HOST="0.0.0.0"
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
echo "正在启动 EcomImagePro Backend 服务..."
echo "端口: $PORT"
echo "日志文件: $LOG_FILE"

# 后台运行，保存PID
nohup uvicorn app.main:app --host "$HOST" --port "$PORT" > "$LOG_FILE" 2>&1 &
PID=$!

# 保存PID
echo $PID > "$PID_FILE"

# 等待一下，检查服务是否成功启动
sleep 2

if ps -p "$PID" > /dev/null 2>&1; then
    echo "✓ 服务启动成功!"
    echo "  PID: $PID"
    echo "  访问地址: http://localhost:$PORT"
    echo "  日志文件: $LOG_FILE"
    echo "  停止服务: ./stop.sh 或 kill $PID"
else
    echo "✗ 服务启动失败，请查看日志: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
