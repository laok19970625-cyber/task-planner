"""命令行入口：目标拆解。用法: python main.py <目标描述>"""

import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))

from planner import LLMClient, format_plan, plan_goal  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print("用法：python main.py <目标描述>")
        return
    goal = sys.argv[1]
    try:
        plan = plan_goal(goal, LLMClient())
        print("=== 任务规划 ===")
        print(format_plan(plan))
    except RuntimeError as e:
        print(f"[错误] {e}")


if __name__ == "__main__":
    main()
