# AI Ops Starter · 组织化 AI 工程协作入门套件

> 一套跨平台（Windows / macOS / Linux）、零外部依赖的 Antigravity 入门插件与交互式教学指南，帮助新手 3 分钟建立「安全卡口 + 省钱路由 + 二振熔断 + 独立挑刺」的组织化 AI 使用思维。

## 在线学习网页
- **在线交互指南**：https://wole278.github.io/ai-ops-starter/
- **离线学习**：直接双击本目录内的 `index.html` 即可在浏览器中离线学习与实操。

## 30 秒傻瓜式一键安装（Windows / macOS / Linux）

无需提前配置 Git 或环境变量，复制对应系统的一行命令在终端回车即可（自动检测 Python 3 并安装插件）：

- **Windows（PowerShell）**：
  ```powershell
  irm https://wole278.github.io/ai-ops-starter/install.ps1 | iex
  ```
- **macOS / Linux（终端 Terminal）**：
  ```bash
  curl -fsSL https://wole278.github.io/ai-ops-starter/install.sh | bash
  ```
- **离线压缩包安装（零命令双击）**：
  - Windows：解压后直接双击 `install.bat`
  - macOS：解压后直接双击 `install-mac.command`
  - Linux：解压后运行 `bash install.sh`

安装完成后重启或新开一个 Antigravity 窗口即可生效。

## 核心组件说明
- `rules/AGENTS.md`：精简热内存工程宪章（四大姿态 + 五条底线 + 省钱路由）
- `skills/model-cost-router/SKILL.md`：多模型分工、Flash 苦力下沉与交接单工作流
- `hooks.json` + `scripts/*.py`：跨平台后台防呆卡口（高危命令 `force_ask`、二振熔断、`AGENTS.md` 定容防膨胀）
