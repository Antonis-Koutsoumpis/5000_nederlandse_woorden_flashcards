#!/bin/bash
# validate new-word batch N, rebuild data, commit+push on success
set -e
cd "$(dirname "$0")"
python3 newlib.py check "$1"
python3 assemble.py > /tmp/claude-0/asm.log 2>&1 || { cat /tmp/claude-0/asm.log; echo "NOT SAVED"; exit 1; }
head -1 /tmp/claude-0/asm.log
./save.sh "New words batch $1"
