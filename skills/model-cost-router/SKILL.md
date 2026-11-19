---
name: model-cost-router
description: Cost-aware routing, Flash subagent delegation for repetitive tool loops, two-strike failure handoff (.agents/handoff/CURRENT_TASK.md), and independent review triggers.
---

# 多模型省钱路由与防呆协作指南

## 1. 意图分级与首行徽章
收到新任务时，先判断任务复杂度（微意图直通 / 中意图自检 / 大意图先谋后工），并在首回合第一行输出：
`> 🧭 **【谋 / 工 / 察】** ｜ 路由：<轻量/主力/高阶> ｜ 判准：<一句话核心动作>`

## 2. 三条核心工作流
1. **苦力下沉（省钱省上下文）**：当前处于高阶/推理模型时，超过 2 步的目录扫描、日志排查或跑测试，通过 `invoke_subagent(TypeName="self", Model="flash", Workspace="inherit")` 下沉给轻量模型后台执行。
2. **二振熔断（防死循环）**：同一报错连续修改 **2 次** 仍未解决，立即停手，将「目标、行号、已排除死路」写入 `.agents/handoff/CURRENT_TASK.md`（≤200 行），请求切换更强模型或异构模型单点突破。
3. **独立审查（破盲区）**：连续多轮同源顺畅对话或核心模块交付前，主动拉起独立只读审查或异构模型（如 Sonnet/Opus）挑刺找反例，严禁自写自审。
