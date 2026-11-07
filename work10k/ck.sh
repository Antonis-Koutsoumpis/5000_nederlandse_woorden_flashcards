#!/bin/bash
# usage: ./ck.sh N  -> validate batch N; save+push only when there are no errors, then show batch N+1
cd /home/claude/5000_nederlandse_woorden_flashcards/work10k
out=$(python3 enrichlib.py check $1); echo "$out"
if echo "$out" | grep -q ERR; then echo "NOT SAVED"; exit 1; fi
./save.sh "Enrich batch $1" && python3 enrichlib.py show $(($1+1))
