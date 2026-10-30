#!/usr/bin/env bash
# Instala un pre-commit que impide subir .env o llaves por accidente.
#   bash scripts/install_git_hooks.sh
set -euo pipefail
HOOK="$(git rev-parse --git-dir)/hooks/pre-commit"
cat > "$HOOK" <<'HOOK_EOF'
#!/usr/bin/env bash
if git diff --cached --name-only | grep -Eq '(^|/)\.env$'; then
  echo "BLOQUEADO: intentas commitear .env (tus llaves)." >&2; exit 1
fi
if git diff --cached -U0 | grep -Eq '^\+.*(sk-(proj-)?[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{35}|AQ\.[A-Za-z0-9_-]{30,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})'; then
  echo "BLOQUEADO: parece que hay una llave real en los cambios." >&2; exit 1
fi
HOOK_EOF
chmod +x "$HOOK"
echo "pre-commit instalado en $HOOK"
