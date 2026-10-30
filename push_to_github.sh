#!/usr/bin/env bash
# Sube los cambios a GitHub verificando que ningún secreto vaya en el commit.
set -euo pipefail

REPO_URL="https://github.com/Marcoflesh/InterviewAI-page.git"
MSG="${1:-chore: actualizar InterviewAI}"

[ -d .git ] || { git init; git branch -M main; }
git remote get-url origin >/dev/null 2>&1 && git remote set-url origin "$REPO_URL" || git remote add origin "$REPO_URL"

git add -A
if git diff --cached --name-only | grep -Eq '(^|/)\.env$'; then
  echo "ERROR: .env está en el commit. Revisa .gitignore." >&2; exit 1
fi
if git diff --cached -U0 | grep -Eq '^\+.*(sk-proj-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{35}|ghp_[A-Za-z0-9]{30,})'; then
  echo "ERROR: parece que hay una llave real en los cambios. No se subió nada." >&2; exit 1
fi

git commit -m "$MSG" || echo "Sin cambios para commitear."
git push -u origin main
