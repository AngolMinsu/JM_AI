#!/bin/bash

LOG_FILE="$(pwd)/llm.log"

echo "Qwen3.5-9B 서버를 백그라운드에서 시작합니다..."
echo "로그 확인: tail -f $LOG_FILE"

nohup llama-server \
    --model "$HOME/work/models/Qwen3.5-9B/Qwen3.5-9B-Q4_K_M.gguf" \
    --mmproj "$HOME/work/models/Qwen3.5-9B/mmproj-BF16.gguf" \
    --host 0.0.0.0 \
    --port 8080 \
    -c 8192 \
    -n 8192 \
    -ub 512 > "$LOG_FILE" 2>&1 &