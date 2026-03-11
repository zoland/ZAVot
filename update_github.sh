#!/usr/bin/env bash
set -euo pipefail

# ===== Настройки по умолчанию =====
DEFAULT_BRANCH="main"

# ===== Проверки =====
if ! command -v git >/dev/null 2>&1; then
  echo "❌ Git не установлен."
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Текущая папка не является git-репозиторием."
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "❌ Remote 'origin' не настроен."
  exit 1
fi

# ===== Определяем текущую ветку =====
CURRENT_BRANCH="$(git branch --show-current || true)"
if [[ -z "${CURRENT_BRANCH}" ]]; then
  CURRENT_BRANCH="${DEFAULT_BRANCH}"
fi

echo "📁 Репозиторий: $(basename "$(git rev-parse --show-toplevel)")"
echo "🌿 Ветка: ${CURRENT_BRANCH}"
echo "🔗 Origin: $(git remote get-url origin)"
echo

# ===== Проверяем есть ли изменения =====
if [[ -z "$(git status --porcelain)" ]]; then
  echo "✅ Нет изменений для коммита."
  exit 0
fi

echo "Изменения:"
git status --short
echo

# ===== Сообщение коммита =====
COMMIT_MSG="${1:-}"
if [[ -z "${COMMIT_MSG}" ]]; then
  read -r -p "Введите сообщение коммита: " COMMIT_MSG
fi

if [[ -z "${COMMIT_MSG}" ]]; then
  echo "❌ Сообщение коммита пустое."
  exit 1
fi

# ===== Commit =====
git add -A
git commit -m "${COMMIT_MSG}"

# ===== Обновляемся перед push =====
echo "⬇️  git pull --rebase origin ${CURRENT_BRANCH}"
git pull --rebase origin "${CURRENT_BRANCH}"

# ===== Push =====
echo "⬆️  git push origin ${CURRENT_BRANCH}"
git push origin "${CURRENT_BRANCH}"

echo
echo "✅ Готово: изменения отправлены в origin/${CURRENT_BRANCH}"