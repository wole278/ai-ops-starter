#!/usr/bin/env bash
set -euo pipefail

echo "=== AI Ops Starter 一键安装向导 (macOS / Linux) ==="

# 1. 检测 Python 3
if command -v python3 >/dev/null 2>&1; then
  echo "[OK] 检测到 $(python3 --version)"
elif command -v python >/dev/null 2>&1 && python --version 2>&1 | grep -q "Python 3\."; then
  echo "[OK] 检测到 $(python --version)"
else
  echo "[提示] 未检测到 Python 3，Hooks 护栏需要 Python 3。macOS 可运行 brew install python3，Ubuntu/Debian 可运行 sudo apt install -y python3。"
fi

# 2. 判断是本地离线目录运行，还是 curl | bash 远程运行
SCRIPT_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

DEST_DIR="$HOME/.gemini/config/plugins/ai-ops-starter"
INSTALLED=0

copy_plugin_files() {
  local src="$1"
  mkdir -p "$DEST_DIR"
  for item in plugin.json hooks.json rules skills scripts; do
    if [ -e "$src/$item" ]; then
      rm -rf "$DEST_DIR/$item"
      cp -R "$src/$item" "$DEST_DIR/$item"
    fi
  done
}

if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/plugin.json" ]; then
  if command -v agy >/dev/null 2>&1; then
    if agy plugin install "$SCRIPT_DIR"; then
      INSTALLED=1
    fi
  fi
  if [ "$INSTALLED" -eq 0 ]; then
    copy_plugin_files "$SCRIPT_DIR"
    INSTALLED=1
  fi
else
  if command -v agy >/dev/null 2>&1; then
    if agy plugin install https://github.com/wole278/ai-ops-starter; then
      INSTALLED=1
    fi
  fi
  if [ "$INSTALLED" -eq 0 ]; then
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "$TMP_DIR"' EXIT
    echo "[执行] 正在下载并安装插件到 $DEST_DIR ..."
    curl -fsSL "https://github.com/wole278/ai-ops-starter/archive/refs/heads/main.tar.gz" | tar -xz -C "$TMP_DIR"
    copy_plugin_files "$TMP_DIR/ai-ops-starter-main"
    INSTALLED=1
  fi
fi

if [ "$INSTALLED" -eq 1 ]; then
  echo ""
  echo "[OK] ai-ops-starter 安装完成！请重启或新开一个 Antigravity 窗口即可生效。"
else
  echo "[FAIL] 安装未完成，请检查网络或权限后重试。" >&2
  exit 1
fi
