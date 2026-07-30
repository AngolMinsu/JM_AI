#!/bin/bash

LOG_FILE="$(pwd)/embedding.log"

echo "Qwen3-Embedding-8B 서버를 백그라운드에서 시작합니다..."
echo "로그 확인: tail -f $LOG_FILE"

nohup llama-server \
    --model "$HOME/work/models/Qwen3-Embedding-8B/Qwen3-Embedding-8B.Q5_K_M.gguf" \
    --host 0.0.0.0 \
    --port 8081 \
    -c 8192 \
    --embedding \
    --pooling mean > "$LOG_FILE" 2>&1 &