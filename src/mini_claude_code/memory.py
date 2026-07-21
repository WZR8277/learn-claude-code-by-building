"""Persistent memory files for cross-session tutorial state."""

import json
import os
import re
import time
from pathlib import Path
from typing import Any

import yaml
from anthropic import Anthropic


WORKDIR = Path.cwd()
MEMORY_DIR = WORKDIR / ".memory"
MEMORY_INDEX = MEMORY_DIR / "MEMORY.md"
MEMORY_TYPES = {"user", "feedback", "project", "reference"}
CONSOLIDATE_THRESHOLD = 10


def _ensure_memory_dir() -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        metadata = {}
    return metadata, parts[2].strip()


def _slugify(name: str) -> str:
    slug = name.lower().replace(" ", "-").replace("/", "-")
    return re.sub(r"[^a-z0-9_.-]+", "-", slug).strip("-") or f"memory-{int(time.time())}"


def _block_type(block: Any) -> str | None:
    if isinstance(block, dict):
        return block.get("type")
    return getattr(block, "type", None)


def _block_text(block: Any) -> str:
    if isinstance(block, dict):
        return str(block.get("text", ""))
    return str(getattr(block, "text", ""))


def extract_text(content: Any) -> str:
    if not isinstance(content, list):
        return str(content)
    return "\n".join(_block_text(block) for block in content if _block_type(block) == "text")


def write_memory_file(name: str, mem_type: str, description: str, body: str) -> Path:
    """写入单个记忆文件，并重建轻量索引。"""
    _ensure_memory_dir()
    if mem_type not in MEMORY_TYPES:
        mem_type = "user"

    filename = f"{_slugify(name)}.md"
    path = MEMORY_DIR / filename
    path.write_text(
        f"---\nname: {name}\ndescription: {description}\ntype: {mem_type}\n---\n\n{body}\n"
    )
    rebuild_index()
    return path


def rebuild_index() -> None:
    """MEMORY.md 只保存 name/description，避免 system prompt 常驻完整记忆正文。"""
    _ensure_memory_dir()
    lines = []
    for path in sorted(MEMORY_DIR.glob("*.md")):
        if path.name == "MEMORY.md":
            continue
        raw = path.read_text()
        metadata, body = parse_frontmatter(raw)
        name = str(metadata.get("name") or path.stem)
        fallback = body.splitlines()[0][:80] if body else ""
        description = str(metadata.get("description") or fallback)
        lines.append(f"- [{name}]({path.name}) — {description}")
    MEMORY_INDEX.write_text("\n".join(lines) + "\n" if lines else "")


def read_memory_index() -> str:
    if not MEMORY_INDEX.exists():
        return ""
    return MEMORY_INDEX.read_text().strip()


def read_memory_file(filename: str) -> str | None:
    path = MEMORY_DIR / filename
    # 记忆按索引中的文件名读取，不接受路径穿越。
    if path.resolve().parent != MEMORY_DIR.resolve() or not path.exists():
        return None
    return path.read_text()


def list_memory_files() -> list[dict[str, str]]:
    if not MEMORY_DIR.exists():
        return []

    memories = []
    for path in sorted(MEMORY_DIR.glob("*.md")):
        if path.name == "MEMORY.md":
            continue
        raw = path.read_text()
        metadata, body = parse_frontmatter(raw)
        memories.append({
            "filename": path.name,
            "name": str(metadata.get("name") or path.stem),
            "description": str(metadata.get("description") or ""),
            "type": str(metadata.get("type") or "user"),
            "body": body,
        })
    return memories


def _recent_user_text(messages: list[dict[str, Any]], max_items: int = 3) -> str:
    recent_texts = []
    for message in reversed(messages):
        if message.get("role") != "user":
            continue
        text = extract_text(message.get("content", ""))
        if text.strip():
            recent_texts.append(text)
        if len(recent_texts) >= max_items:
            break
    return " ".join(reversed(recent_texts))[:2000]


def _parse_json_array(text: str) -> list[Any] | None:
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if not match:
        return None
    try:
        value = json.loads(match.group())
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, list) else None


def select_relevant_memories(
    messages: list[dict[str, Any]],
    max_items: int = 5,
    client=None,
    model: str | None = None,
) -> list[str]:
    """先让模型根据索引挑记忆；失败时降级为 name/description 关键词匹配。"""
    files = list_memory_files()
    recent = _recent_user_text(messages)
    if not files or not recent.strip():
        return []

    catalog = "\n".join(
        f"{index}: {memory['name']} — {memory['description']}"
        for index, memory in enumerate(files)
    )
    prompt = (
        "Given the recent conversation and the memory catalog below, "
        "select the indices of memories that are clearly relevant. "
        "Return ONLY a JSON array of integers, e.g. [0, 3]. "
        "If none are relevant, return [].\n\n"
        f"Recent conversation:\n{recent}\n\n"
        f"Memory catalog:\n{catalog}"
    )

    try:
        if client is None:
            client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
        model = model or os.environ["MODEL_ID"]
        response = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        indices = _parse_json_array(extract_text(response.content).strip())
        if indices is not None:
            selected = []
            for index in indices:
                if isinstance(index, int) and 0 <= index < len(files):
                    selected.append(files[index]["filename"])
                if len(selected) >= max_items:
                    break
            return selected
    except Exception:
        pass

    keywords = [word.lower() for word in re.findall(r"[\w-]+", recent) if len(word) > 3]
    selected = []
    for memory in files:
        haystack = f"{memory['name']} {memory['description']}".lower()
        if any(keyword in haystack for keyword in keywords):
            selected.append(memory["filename"])
        if len(selected) >= max_items:
            break
    return selected


def load_memories(messages: list[dict[str, Any]], client=None, model: str | None = None) -> str:
    selected_files = select_relevant_memories(messages, client=client, model=model)
    if not selected_files:
        return ""

    parts = ["<relevant_memories>"]
    for filename in selected_files:
        content = read_memory_file(filename)
        if content:
            parts.append(content)
    parts.append("</relevant_memories>")
    return "\n\n".join(parts)


def _recent_dialogue(messages: list[dict[str, Any]]) -> str:
    parts = []
    for message in messages[-10:]:
        text = extract_text(message.get("content", ""))
        if text.strip():
            parts.append(f"{message.get('role', '?')}: {text}")
    return "\n".join(parts)


def extract_memories(messages: list[dict[str, Any]], client=None, model: str | None = None) -> int:
    """从回合结束时的对话里提取稳定偏好或项目事实。"""
    dialogue = _recent_dialogue(messages)
    if not dialogue.strip():
        return 0

    existing = list_memory_files()
    existing_desc = "\n".join(
        f"- {memory['name']}: {memory['description']}"
        for memory in existing
    ) if existing else "(none)"
    prompt = (
        "Extract user preferences, constraints, or project facts from this dialogue.\n"
        "Return a JSON array. Each item: {name, type, description, body}.\n"
        "- name: short kebab-case identifier\n"
        "- type: one of user, feedback, project, reference\n"
        "- description: one-line summary for index lookup\n"
        "- body: full detail in markdown\n"
        "If nothing new or already covered by existing memories, return [].\n\n"
        f"Existing memories:\n{existing_desc}\n\n"
        f"Dialogue:\n{dialogue[:4000]}"
    )

    try:
        if client is None:
            client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
        model = model or os.environ["MODEL_ID"]
        response = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )
        items = _parse_json_array(extract_text(response.content).strip())
        if not items:
            return 0
    except Exception:
        return 0

    count = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or f"memory-{int(time.time())}")
        mem_type = str(item.get("type") or "user")
        description = str(item.get("description") or "")
        body = str(item.get("body") or "")
        if description and body:
            write_memory_file(name, mem_type, description, body)
            count += 1

    if count:
        print(f"\n\033[33m[Memory: extracted {count} new memories]\033[0m")
    return count


def consolidate_memories(client=None, model: str | None = None) -> int:
    """记忆数量超过阈值后，让模型做一次低频去重整理。"""
    files = list_memory_files()
    if len(files) < CONSOLIDATE_THRESHOLD:
        return 0

    catalog = "\n\n".join(
        f"## {memory['filename']}\n"
        f"name: {memory['name']}\n"
        f"description: {memory['description']}\n"
        f"{memory['body']}"
        for memory in files
    )
    prompt = (
        "Consolidate the following memory files. Rules:\n"
        "1. Merge duplicates into one\n"
        "2. Remove outdated or contradicted memories\n"
        "3. Keep the total under 30 memories\n"
        "4. Preserve important user preferences above all\n"
        "Return a JSON array. Each item: {name, type, description, body}.\n\n"
        f"{catalog[:16000]}"
    )

    try:
        if client is None:
            client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
        model = model or os.environ["MODEL_ID"]
        response = client.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
        )
        items = _parse_json_array(extract_text(response.content).strip())
        if items is None:
            return 0
    except Exception:
        return 0

    for path in MEMORY_DIR.glob("*.md"):
        if path.name != "MEMORY.md":
            path.unlink()

    for item in items:
        if not isinstance(item, dict):
            continue
        description = str(item.get("description") or "")
        body = str(item.get("body") or "")
        if description and body:
            write_memory_file(
                str(item.get("name") or f"memory-{int(time.time())}"),
                str(item.get("type") or "user"),
                description,
                body,
            )

    print(f"\n\033[33m[Memory: consolidated {len(files)} -> {len(items)} memories]\033[0m")
    return len(items)
