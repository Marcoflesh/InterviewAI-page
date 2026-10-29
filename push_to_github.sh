#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/Marcoflesh/InterviewAI-page.git"

if [ ! -d ".git" ]; then
  git init
  git branch -M main
fi

if git remote | grep -q "^origin$"; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi

git add -A
git commit -m "feat: initial full-stack skeleton (FastAPI, LangGraph, Ollama, PostgreSQL, Docker, minimalist UI)" || true
echo "Subiendo proyecto a $REPO_URL ..."
git push -u origin main
