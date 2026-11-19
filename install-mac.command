#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$DIR/install.sh" ]; then
  bash "$DIR/install.sh"
else
  curl -fsSL https://wole278.github.io/ai-ops-starter/install.sh | bash
fi
echo ""
read -r -p "安装已结束，按回车键关闭此窗口..."
