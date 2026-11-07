#!/bin/bash
# merge wip-10k-expansion into main and push, then return to the wip branch
set -e
cd "$(dirname "$0")/.."
git checkout -q main && git pull -q --ff-only origin main
git -c user.name="koutsouma" -c user.email="koutsouma@hotmail.com" merge -q --no-ff wip-10k-expansion -m "Merge 10k expansion: ${1:-new words}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KT6DjPxj9UTzvJk12goFUN"
git push -q origin main
git checkout -q wip-10k-expansion
git log --oneline -1 main
