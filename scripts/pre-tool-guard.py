#!/usr/bin/env python3
"""
Antigravity PreToolUse Hook (Cross-Platform Python 3)
Enforces:
1. Default/Error Fail-Ask (never silently 'allow' unmatched tool calls).
2. AG-11 force_ask guard on destructive CLI (Windows/Mac/Linux).
3. Swarm surgical-knife guard: force_ask on n>1, tasks, share/branch, fork, or high-cost models.
4. AGENTS.md / GEMINI.md capacity cap (120 lines global / 80 lines project; 18431 bytes max), allowing shrinking edits.
"""
import json
import os
import re
import sys

HIGH_RISK_CMD_RE = re.compile(
    r"(?i)(\bgit\b.*\b(push\b.*(\s-f\b|--force\b|\s\+\S|--delete\b|--mirror\b|\s:\S)|reset\s+--hard|clean\b.*(\s-\w*f|--force)|filter-(branch|repo)|branch\s+-D)|\b(Remove-Item|ri|del|erase|rd|rmdir)\b.*(\s-r\w*|\s/s)\b|\brm\s.*(-\w*r|--recursive)|\bnpm\s+(publish|i(nstall)?\b.*\s-g\b)|\bgh\s+(repo\s+(edit|delete)|release\s+create)|--visibility\b)"
)
HIGH_COST_MODEL_RE = re.compile(r"(opus|sonnet|argon|xhigh|extra)", re.I)
ADD_HIGH_COST_RE = re.compile(r"(opus|sonnet|argon|xhigh|extra)", re.I)
DOC_CAP_RE = re.compile(r"[\\/](AGENTS|GEMINI)\.md$", re.I)
GLOBAL_RULE_RE = re.compile(r"(ai-ops-starter[\\/]rules[\\/]AGENTS\.md|[\\/]\.gemini[\\/]GEMINI\.md)$", re.I)


def out_json(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.exit(0)


def check_doc_capacity(tool_name: str, args: dict):
    target_path = str(args.get("Path") or "")
    if not DOC_CAP_RE.search(target_path):
        return None

    orig_text = None
    if os.path.isfile(target_path):
        try:
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                orig_text = f.read()
        except Exception:
            orig_text = None

    final_text = None
    if tool_name == "write_file" and "Content" in args:
        content = str(args.get("Content") or "")
        is_append = args.get("Append") in (True, "true", "True")
        if is_append and orig_text is not None:
            final_text = orig_text + content
        else:
            final_text = content
    elif tool_name == "edit_file" and orig_text is not None and "Target" in args:
        target_str = str(args.get("Target") or "")
        replace_str = str(args.get("Replacement") or "")
        if target_str and target_str in orig_text:
            final_text = orig_text.replace(target_str, replace_str)

    if final_text is None:
        return None

    lines = len(re.split(r"\r?\n", final_text))
    byte_count = len(final_text.encode("utf-8"))
    is_global = bool(GLOBAL_RULE_RE.search(target_path))
    line_limit = 120 if is_global else 80
    byte_limit = 18431

    if orig_text is not None:
        orig_lines = len(re.split(r"\r?\n", orig_text))
        orig_bytes = len(orig_text.encode("utf-8"))
        if lines < orig_lines and byte_count <= orig_bytes:
            return None

    if lines > line_limit or byte_count > byte_limit:
        return {
            "decision": "deny",
            "reason": f"[J0 定容门禁拦截] {target_path} 预计落盘 {lines} 行 / {byte_count} 字节，超过上限 ({line_limit} 行 / {byte_limit} 字节)，请先精简后再写。",
        }
    return None


def main():
    try:
        raw = sys.stdin.read()
        if not raw or not raw.strip() or raw.strip() == "{}":
            out_json({"decision": "ask"})
        payload = json.loads(raw)
        tool_call = payload.get("toolCall") if isinstance(payload, dict) else None
        if not isinstance(tool_call, dict):
            out_json({"decision": "ask"})

        tool_name = str(tool_call.get("name") or "")
        raw_args = tool_call.get("args")
        if isinstance(raw_args, str):
            args = json.loads(raw_args) if raw_args.strip() else {}
        elif isinstance(raw_args, dict):
            args = raw_args
        else:
            args = {}

        if tool_name == "swarm":
            action = str(args.get("action") or "").lower()
            model_val = str(args.get("model") or payload.get("modelName") or "")
            if action == "add":
                try:
                    n_val = int(args.get("n")) if args.get("n") is not None else 1
                    n_invalid = False
                except Exception:
                    n_val = 1
                    n_invalid = True
                tasks = args.get("tasks")
                has_tasks = isinstance(tasks, list) and len(tasks) > 0
                ws_val = str(args.get("workspace") or "inherit").lower()
                has_fork = bool(str(args.get("fork") or "").strip())
                if n_invalid or n_val > 1 or has_tasks or ws_val in ("share", "branch") or has_fork or ADD_HIGH_COST_RE.search(model_val):
                    out_json({
                        "decision": "force_ask",
                        "reason": "[M0 Swarm 卡口] 检测到批量分片、独立工作区(share/branch)、fork 或高价模型，需确认后执行。",
                    })
            elif action == "model" and HIGH_COST_MODEL_RE.search(model_val):
                out_json({
                    "decision": "force_ask",
                    "reason": "[M0 Swarm 卡口] 检测到原地切换至高价/高配额模型，需确认后执行。",
                })
            elif action == "kill":
                out_json({
                    "decision": "ask",
                    "reason": "[AG-11 Swarm 收刀确认] kill 将永久销毁 worker 及其关联工作区。",
                })
            out_json({"decision": "ask"})

        if tool_name in ("write_file", "edit_file"):
            res = check_doc_capacity(tool_name, args)
            if res:
                out_json(res)
            out_json({"decision": "ask"})

        if tool_name == "run_command":
            cmd = str(args.get("CommandLine") or "")
            if HIGH_RISK_CMD_RE.search(cmd):
                out_json({
                    "decision": "force_ask",
                    "reason": "[AG-11 高危命令卡口] 检测到高危/不可逆命令（force push / reset --hard / 递归删除 / 全局发布等），需确认后执行。",
                })
            out_json({"decision": "ask"})

        out_json({"decision": "ask"})
    except Exception:
        out_json({"decision": "ask"})


if __name__ == "__main__":
    main()
