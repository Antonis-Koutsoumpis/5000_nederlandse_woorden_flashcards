#!/bin/bash
# usage: ./save.sh "message"  -> commit everything on the wip branch and push
cd /home/claude/5000_nederlandse_woorden_flashcards
git add -A
git -c user.name="koutsouma" -c user.email="koutsouma@hotmail.com" commit -qm "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KT6DjPxj9UTzvJk12goFUN" && git push -q 2>&1 | tail -1
git log --oneline | head -1
