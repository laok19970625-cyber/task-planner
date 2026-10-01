"""AI 任务规划器：把一个大目标拆解成可执行的分步计划。

特性：
- 目标拆解：LLM 把目标拆成阶段 + 具体步骤 + 时间估算。
- 输出结构化 JSON，便于程序化消费。
"""

from __future__ import annotations

import json
import os
import urllib.request


class LLMClient:
    def __init__(self, api_key=None, api_base=None, model=None):
        self.api_key = api_key or os.environ.get("LLM_API_KEY", "")
        self.api_base = (api_base or os.environ.get("LLM_API_BASE", "https://open.bigmodel.cn/api/paas/v4")).rstrip("/")
        self.model = model or os.environ.get("LLM_MODEL", "glm-4-flash")

    def chat(self, messages, temperature=0.3):
        if not self.api_key:
            raise RuntimeError("未配置 LLM_API_KEY，请设置环境变量后重试。")
        url = f"{self.api_base}/chat/completions"
        payload = {"model": self.model, "messages": messages, "temperature": temperature}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]


PLANNER_PROMPT = (
    "你是一名项目管理专家。请把下面的目标拆解成一份可执行的计划，"
    "并以 JSON 数组格式输出，每个元素是一个阶段，结构如下：\n"
    '{"phase": "阶段名", "tasks": ["具体任务1", "具体任务2"], "estimate_days": 估算天数}\n'
    "要求：任务具体可执行、逻辑顺序合理、时间估算现实。只输出 JSON，不要其他文字。"
)


def plan_goal(goal: str, llm: LLMClient | None = None) -> list[dict]:
    """把目标拆解为阶段计划，返回结构化 JSON。"""
    llm = llm or LLMClient()
    messages = [
        {"role": "system", "content": PLANNER_PROMPT},
        {"role": "user", "content": goal},
    ]
    raw = llm.chat(messages)
    # 容错：剥离可能的 markdown 代码块包裹
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # 降级：返回原始文本包装
        return [{"phase": "计划", "tasks": [raw], "estimate_days": None}]


def format_plan(plan: list[dict]) -> str:
    """把结构化计划格式化为可读文本。"""
    lines = []
    total_days = 0
    for i, phase in enumerate(plan, 1):
        lines.append(f"阶段 {i}：{phase.get('phase', '未命名')}")
        for j, task in enumerate(phase.get("tasks", []), 1):
            lines.append(f"  {i}.{j} {task}")
        days = phase.get("estimate_days")
        if days is not None:
            total_days += days
            lines.append(f"  （预计 {days} 天）")
    if total_days:
        lines.append(f"\n总计约 {total_days} 天")
    return "\n".join(lines)
