#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

git -C "$REPO_DIR" pull --no-rebase origin main

python3 "$REPO_DIR/scripts/daily_check.py"

ts=$(date '+%Y-%m-%d %H:%M')

if ! git -C "$REPO_DIR" diff --quiet -- daily-news.md || [ -n "$(git -C "$REPO_DIR" status --short -- daily-news.md)" ]; then
  status="$(git -C "$REPO_DIR" status --short)"
  if printf '%s\n' "$status" | grep -E '(^.. AGENTS\.md|^.. \.codex)'; then
    echo "Refuse to commit local-only files:"
    git -C "$REPO_DIR" status --short
    exit 1
  fi

  git -C "$REPO_DIR" add daily-news.md
  git -C "$REPO_DIR" commit -m "chore: update news digest ${ts}"
  git -C "$REPO_DIR" push origin main
fi
