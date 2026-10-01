"""任务规划器单元测试。"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from planner import LLMClient, format_plan, plan_goal  # noqa: E402


class FakeLLM(LLMClient):
    def chat(self, messages, temperature=0.3):
        return '[{"phase": "调研", "tasks": ["收集资料", "分析竞品"], "estimate_days": 2}]'


class TestPlanner(unittest.TestCase):
    def test_plan_goal_parses_json(self):
        plan = plan_goal("开发一个App", FakeLLM())
        self.assertEqual(plan[0]["phase"], "调研")
        self.assertEqual(len(plan[0]["tasks"]), 2)

    def test_format_plan(self):
        plan = [{"phase": "调研", "tasks": ["收集资料"], "estimate_days": 2}]
        out = format_plan(plan)
        self.assertIn("阶段 1", out)
        self.assertIn("收集资料", out)
        self.assertIn("2 天", out)


class TestFallback(unittest.TestCase):
    class BrokenLLM(LLMClient):
        def chat(self, messages, temperature=0.3):
            return "无法解析的内容"

    def test_plan_goal_fallback(self):
        plan = plan_goal("目标", self.BrokenLLM())
        self.assertEqual(plan[0]["phase"], "计划")
        self.assertIn("无法解析的内容", plan[0]["tasks"][0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
