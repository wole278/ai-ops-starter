#!/usr/bin/env python3
"""
Antigravity PreInvocation Hook (Cross-Platform Python 3)
Provides:
1. Context size warning (/compact reminder at >= 200KB).
2. Consecutive failure telemetry (2-strike circuit breaker) using structured JSONL parsing.
3. High-cost model loop breaker (delegate >2-step chores to Flash).
4. Echo-chamber audit reminder on >=3rd multiple user turns.
5. First-line stance badge guidance.
Fail-open ({}) on any error.
"""
import json
import os
import re
import sys

EXPENSIVE_RE = re.compile(r"(argon|opus|sonnet)", re.I)
FLASH_RE = re.compile(r"flash", re.I)
HYDROGEN_XHIGH_RE = re.compile(r"(hydrogen|neon)-(?:tiered-)?(xhigh|extra)$", re.I)
ROUTINE_RE = re.compile(
    r"^\s*(\bgit\b\s|\bcommit\b|\bpush\b|\bpull\b|\bsync\b|提交|同步|跑一下测试|运行测试|格式|\bformat\b|\blint\b|继续收尾|查看状态|清理)",
    re.I,
)
SHOWING_LINES_RE = re.compile(r"(?m)^Showing lines \d+")
CMD_EXIT_FAIL_RE = re.compile(r"Command exited with code [1-9]\d*")
CMD_EXIT_OK_RE = re.compile(r"Command exited with code 0\b")
TOOL_EXEC_ERR_RE = re.compile(r"Encountered error in tool execution")


def out_json(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.exit(0)


def count_recent_failures(transcript_path: str, tail_lines: int = 45):
    if not transcript_path or not os.path.isfile(transcript_path):
        return 0, 0
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception:
        return 0, 0

    user_turns = 0
    for line in lines:
        try:
            obj = json.loads(line)
            if obj.get("type") == "USER_INPUT":
                user_turns += 1
        except Exception:
            continue

    recent = lines[-tail_lines:] if len(lines) > tail_lines else lines
    err_count = 0
    last_tools = []
    for line in recent:
        try:
            obj = json.loads(line)
        except Exception:
            continue
        t = obj.get("type", "")
        status = obj.get("status", "")
        if t == "PLANNER_RESPONSE":
            tcs = obj.get("tool_calls") or []
            last_tools = [tc.get("name", "") for tc in tcs if isinstance(tc, dict)]
            if status == "ERROR":
                err_count += 1
            continue

        if status == "ERROR":
            err_count += 1
            continue

        if t == "GENERIC":
            content = obj.get("content", "") or ""
            if SHOWING_LINES_RE.search(content):
                continue
            head = content.split("Command output:", 1)[0]
            has_run_cmd = (not last_tools) or ("run_command" in last_tools)
            if has_run_cmd and (CMD_EXIT_FAIL_RE.search(head) or TOOL_EXEC_ERR_RE.search(head)):
                err_count += 1
            elif CMD_EXIT_OK_RE.search(head) or (status == "DONE" and last_tools and last_tools != ["read_file"]):
                err_count = 0
        elif status == "DONE" and t != "USER_INPUT":
            err_count = 0

    return err_count, user_turns


def main():
    try:
        raw = sys.stdin.read()
        if not raw or not raw.strip() or raw.strip() == "{}":
            out_json({})
        payload = json.loads(raw)
        if not isinstance(payload, dict) or not payload:
            out_json({})

        model_name = str(payload.get("modelName") or "")
        last_input = str(payload.get("lastUserInput") or "")
        inv_num = int(payload.get("invocationNum") or 1)
        transcript_path = str(payload.get("transcriptPath") or "")

        is_flash = bool(FLASH_RE.search(model_name)) or not model_name.strip()
        is_expensive = bool(EXPENSIVE_RE.search(model_name))
        is_xhigh = bool(HYDROGEN_XHIGH_RE.search(model_name))
        is_sonnet = bool(re.search(r"sonnet", model_name, re.I))
        is_routine = bool(ROUTINE_RE.search(last_input))

        steps = []

        # 1. Context Watcher (>= 200KB)
        if inv_num == 1 and transcript_path and os.path.isfile(transcript_path):
            size_bytes = os.path.getsize(transcript_path)
            if size_bytes >= 200000:
                kb = round(size_bytes / 1024)
                steps.append({
                    "systemMessage": {
                        "systemMessage": "",
                        "metadata": {
                            "user_markdown": f"> 💡 **【上下文健康预警】**：当前对话历史已累计 {kb} KB，建议输入 `/compact` 精简上下文后再继续。"
                        },
                    }
                })

        # 2. High-cost loop breaker (exempt Sonnet read-only audit)
        if is_expensive and (not is_sonnet) and inv_num >= 4:
            steps.append({
                "systemMessage": {
                    "systemMessage": f"[M0 成本熔断 (invocationNum={inv_num})]：当前处于高价模型 ({model_name})，请将多步文件检索或测试运行通过 invoke_subagent(TypeName='self', Model='flash', Workspace='inherit') 下沉给轻量模型完成。"
                }
            })
        elif is_xhigh and inv_num >= 5:
            steps.append({
                "systemMessage": {
                    "systemMessage": f"[M0 护栏 (invocationNum={inv_num})]：多步检索与测试请委派 invoke_subagent(TypeName='self', Model='flash', Workspace='inherit') 执行。"
                }
            })

        # 3. First invocation checks
        if inv_num == 1:
            err_count, user_turns = count_recent_failures(transcript_path)
            if (not is_expensive) and (not is_xhigh) and err_count >= 2:
                steps.append({
                    "systemMessage": {
                        "systemMessage": "",
                        "metadata": {
                            "user_markdown": "> 🛑 **【二振硬件熔断】**：检测到连续多次报错，已建议停止盲改并整理交接单 `.agents/handoff/CURRENT_TASK.md` 升级高阶模型破局。"
                        },
                    }
                })
                steps.append({
                    "systemMessage": {
                        "systemMessage": "[M0 二振熔断]：检测到近期连续 >= 2 次失败！严禁第 3 次盲改！请立即停手，将目标、行号与已排除死路写入 .agents/handoff/CURRENT_TASK.md，优先用 swarm(action='model', model='claude-opus-5-5-high') 或提示用户切换高阶模型。"
                    }
                })
            elif not is_expensive:
                steps.append({
                    "systemMessage": {
                        "systemMessage": "[M0 首行徽章]：请在回复首行输出：> 🧭 **【谋 / 工 / 察】** ｜ 路由：<轻量/主力/高阶> ｜ 判准：<一句话核心动作>。连续 2 次失败即停手写交接单。"
                    }
                })
            elif is_routine:
                steps.append({
                    "systemMessage": {
                        "systemMessage": f"[M0 成本提醒]：当前为高价模型 ({model_name}) 处理常规操作，请通过 invoke_subagent(Model='flash') 下沉执行，完成后提醒用户切回常驻主力模型。"
                    }
                })

            if (not is_expensive) and (not is_routine) and user_turns >= 3 and (user_turns % 3 == 0):
                steps.append({
                    "systemMessage": {
                        "systemMessage": f"[察克君 · 同温层发难提醒]：当前同源对话已持续 {user_turns} 轮。若涉及重要架构或高风险变更，请主动拉起独立只读审查或异构模型挑刺，严禁自写自审。"
                    }
                })

        if steps:
            out_json({"injectSteps": steps})
        out_json({})
    except Exception:
        out_json({})


if __name__ == "__main__":
    main()
