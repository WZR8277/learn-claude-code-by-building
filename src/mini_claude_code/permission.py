"""The three-gate permission pipeline introduced by s03."""

from . import tool


# 第一关：命中硬拒绝列表的 Bash 命令永远不执行，也不会询问用户。
DENY_LIST = [
    "rm -rf /",
    "sudo",
    "shutdown",
    "reboot",
    "mkfs",
    "dd if=",
    "> /dev/sda",
]


def check_deny_list(command: str) -> str | None:
    for pattern in DENY_LIST:
        if pattern in command:
            return f"Blocked: '{pattern}' is on the deny list"
    return None


# 第二关：这些操作不是直接拒绝，而是交给用户决定是否执行。
PERMISSION_RULES = [
    {
        "tools": ["write_file", "edit_file"],
        "check": lambda args: not (
            tool.WORKDIR / args.get("path", "")
        ).resolve().is_relative_to(tool.WORKDIR),
        "message": "Writing outside workspace",
    },
    {
        "tools": ["bash"],
        "check": lambda args: any(
            keyword in args.get("command", "")
            for keyword in ["rm ", "> /etc/", "chmod 777"]
        ),
        "message": "Potentially destructive command",
    },
]


def check_rules(tool_name: str, args: dict) -> str | None:
    for rule in PERMISSION_RULES:
        if tool_name in rule["tools"] and rule["check"](args):
            return rule["message"]
    return None


def ask_user(tool_name: str, args: dict, reason: str) -> str:
    """第三关：规则命中后暂停，只认可明确的 yes。"""
    print(f"\n\033[33m⚠ {reason}\033[0m")
    print(f" Tool: {tool_name}({args})")
    choice = input(" Allow? [y/N] ").strip().lower()
    return "allow" if choice in ("y", "yes") else "deny"


def check_permission(block) -> bool:
    """按硬拒绝、规则匹配、用户审批的固定顺序判断一次工具调用。"""
    if block.name == "bash":
        reason = check_deny_list(block.input.get("command", ""))
        if reason:
            print(f"\n\033[31m⛔ {reason}\033[0m")
            return False

    reason = check_rules(block.name, block.input)
    if reason and ask_user(block.name, block.input, reason) == "deny":
        return False

    return True
