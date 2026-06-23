"""Pytest 配置：把 webapp/backend 加入 sys.path，使测试可用裸导入。

后端模块之间用裸导入（from patent_search import ...），与 main.py 一致。
测试沿用同一约定：from voc_scout import ... / from deep_search import ...
"""
import os
import sys

_BACKEND = os.path.join(os.path.dirname(__file__), "webapp", "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)


def pytest_configure(config):
    """注册自定义 mark，消除 PytestUnknownMarkWarning。"""
    config.addinivalue_line(
        "markers", "integration: requires live API key / network (auto-skipped without DEEPSEEK_API_KEY)"
    )
