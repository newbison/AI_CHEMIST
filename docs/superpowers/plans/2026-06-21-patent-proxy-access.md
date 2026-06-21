# 专利全文获取：代理访问 Google Patents 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 `patent_search.py` 的所有 `httpx.Client` 调用通过本地代理访问 Google Patents，拿到专利全文（Claims + Description + Examples），解决报告核心章节空白问题。

**Architecture:** 在 `patent_search.py` 顶部新增 `_PATENT_PROXY` 模块级常量（从 `PATENT_PROXY` 环境变量读取，默认 `http://127.0.0.1:7890`）。给所有 8 处 `httpx.Client(...)` 调用添加 `proxy=_PATENT_PROXY` 参数。代理失败时自动降级到已有的 Scholar 摘要兜底逻辑（不变）。

**Tech Stack:** Python 3.11+, httpx (proxy 参数), python-dotenv (环境变量)

---

## 文件结构

| 文件 | 责任 | 改动类型 |
|------|------|---------|
| `webapp/backend/patent_search.py` | 专利检索与详情抓取 | 修改：加 `_PATENT_PROXY` 常量 + 8 处 `httpx.Client` 加 `proxy` 参数 |
| `webapp/backend/.env` | 环境变量配置 | 修改：加 `PATENT_PROXY` 条目（可选，有默认值） |
| `webapp/backend/_test_proxy_impl.py` | 验证脚本（实施后删除） | 新建：临时测试脚本 |

---

## Task 1: 新增 `_PATENT_PROXY` 常量

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\patent_search.py:46-54`

- [ ] **Step 1: 在 `BROWSER_HEADERS` 定义后、`EPO_TOKEN_URL` 定义前插入 `_PATENT_PROXY` 常量**

定位到 `patent_search.py` 第 46-50 行：

```python
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

# EPO OPS API — 免费注册 developers.epo.org 获取
EPO_TOKEN_URL = "https://ops.epo.org/3.2/auth/accesstoken"
```

在 `BROWSER_HEADERS` 字典的 `}` 和 `# EPO OPS API` 注释之间插入：

```python
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

# 专利数据源代理（Clash/V2Ray 本地代理）
# 默认 http://127.0.0.1:7890（Clash 默认端口）
# 设为空字符串则禁用代理（直连，国内会 503）
# 可通过环境变量 PATENT_PROXY 覆盖
_PATENT_PROXY = os.environ.get("PATENT_PROXY", "http://127.0.0.1:7890") or None

# EPO OPS API — 免费注册 developers.epo.org 获取
EPO_TOKEN_URL = "https://ops.epo.org/3.2/auth/accesstoken"
```

注意：`or None` 把空字符串转成 `None`，这样 `httpx.Client(proxy=None)` 等于不走代理（直连）。

- [ ] **Step 2: 验证常量定义正确**

运行：
```bash
python -c "from patent_search import _PATENT_PROXY; print(f'_PATENT_PROXY = {_PATENT_PROXY!r}')"
```

预期输出（未设置环境变量时）：
```
_PATENT_PROXY = 'http://127.0.0.1:7890'
```

- [ ] **Step 3: 验证空字符串环境变量时返回 None**

运行：
```bash
set PATENT_PROXY= && python -c "from patent_search import _PATENT_PROXY; print(f'_PATENT_PROXY = {_PATENT_PROXY!r}')"
```

预期输出：
```
_PATENT_PROXY = None
```

- [ ] **Step 4: Commit**

```bash
git add webapp/backend/patent_search.py
git commit -m "feat(patent): add _PATENT_PROXY constant for proxy configuration"
```

---

## Task 2: 给 `search_google_patents` 加代理

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\patent_search.py:235-238`

- [ ] **Step 1: 修改 `search_google_patents` 的 `httpx.Client` 调用**

定位到第 235-238 行：

```python
        with httpx.Client(
            headers={**BROWSER_HEADERS, "Referer": "https://patents.google.com/"},
            timeout=timeout,
        ) as client:
```

改为：

```python
        with httpx.Client(
            headers={**BROWSER_HEADERS, "Referer": "https://patents.google.com/"},
            timeout=timeout,
            proxy=_PATENT_PROXY,
        ) as client:
```

- [ ] **Step 2: 验证搜索走代理成功**

运行（需要 Clash 代理在 7890 端口运行）：
```bash
python -c "from patent_search import search_google_patents; r = search_google_patents('lithium battery tape', num=3, timeout=15.0); print(f'found {len(r)} patents'); [print(f'  {p.patent_number} | {p.title[:50]}') for p in r[:3]]"
```

预期输出（代理可用时）：
```
found 3 patents
  US... | ...
  US... | ...
  US... | ...
```

如果代理未开启，预期输出：
```
found 0 patents
```
（不会崩溃，降级逻辑后续 Task 处理）

- [ ] **Step 3: Commit**

```bash
git add webapp/backend/patent_search.py
git commit -m "feat(patent): route search_google_patents through proxy"
```

---

## Task 3: 给 `fetch_patent_detail` 路径 1（Google Patents 全文）加代理

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\patent_search.py:872-875`

- [ ] **Step 1: 修改 `fetch_patent_detail` 路径 1 的 `httpx.Client` 调用**

定位到第 872-875 行：

```python
        with httpx.Client(
            headers={**BROWSER_HEADERS, "Referer": "https://patents.google.com/"},
            timeout=timeout,
        ) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html_text = resp.text
            detail = _extract_patent_detail_from_html(html_text)
```

改为：

```python
        with httpx.Client(
            headers={**BROWSER_HEADERS, "Referer": "https://patents.google.com/"},
            timeout=timeout,
            proxy=_PATENT_PROXY,
        ) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html_text = resp.text
            detail = _extract_patent_detail_from_html(html_text)
```

- [ ] **Step 2: 验证全文抓取走代理成功**

运行：
```bash
python -c "from patent_search import fetch_patent_detail; d = fetch_patent_detail('US9755207B2', timeout=15.0); print(f'len={len(d)}'); print(f'has Claims: {\"[Claims]\" in d}'); print(f'has Description: {\"[Description]\" in d}'); print(f'preview: {d[:200]}')"
```

预期输出（代理可用时）：
```
[detail] OK Google Patents US9755207B2: ...KB HTML -> ... chars
len=...
has Claims: True
has Description: True
preview: [Abstract]...[Inventors]...[Assignee]...[Claims]...[Description]...
```

关键验证点：`has Claims: True` 和 `has Description: True` 必须为 True，证明拿到了全文。

- [ ] **Step 3: Commit**

```bash
git add webapp/backend/patent_search.py
git commit -m "feat(patent): route fetch_patent_detail Google Patents path through proxy"
```

---

## Task 4: 给 `fetch_patent_detail` 路径 2（EPO Espacenet）加代理

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\patent_search.py:891-894`

- [ ] **Step 1: 修改 `fetch_patent_detail` 路径 2 的 `httpx.Client` 调用**

定位到第 891-894 行：

```python
        with httpx.Client(
            headers={**BROWSER_HEADERS, "Referer": "https://worldwide.espacenet.com/"},
            timeout=timeout,
        ) as client:
            resp = client.get(epo_url)
```

改为：

```python
        with httpx.Client(
            headers={**BROWSER_HEADERS, "Referer": "https://worldwide.espacenet.com/"},
            timeout=timeout,
            proxy=_PATENT_PROXY,
        ) as client:
            resp = client.get(epo_url)
```

- [ ] **Step 2: Commit**

```bash
git add webapp/backend/patent_search.py
git commit -m "feat(patent): route fetch_patent_detail EPO path through proxy"
```

---

## Task 5: 给 `search_google_scholar` 加代理

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\patent_search.py:296`

- [ ] **Step 1: 修改 `search_google_scholar` 的 `httpx.Client` 调用**

定位到第 296 行：

```python
        with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True) as client:
```

改为：

```python
        with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True, proxy=_PATENT_PROXY) as client:
```

- [ ] **Step 2: 验证 Scholar 搜索仍可用**

运行：
```bash
python -c "from patent_search import search_google_scholar; r = search_google_scholar('lithium battery tape', num=3, timeout=15.0); print(f'found {len(r)}'); [print(f'  {p.patent_number} | {p.title[:50]}') for p in r[:3]]"
```

预期输出（代理可用时）：找到若干专利。

- [ ] **Step 3: Commit**

```bash
git add webapp/backend/patent_search.py
git commit -m "feat(patent): route search_google_scholar through proxy"
```

---

## Task 6: 给 `search_patentsview` 加代理

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\patent_search.py:185`

- [ ] **Step 1: 修改 `search_patentsview` 的 `httpx.Client` 调用**

定位到第 185 行：

```python
        with httpx.Client(headers=BROWSER_HEADERS, timeout=timeout) as client:
            resp = client.get(url, params=params, follow_redirects=True)
```

改为：

```python
        with httpx.Client(headers=BROWSER_HEADERS, timeout=timeout, proxy=_PATENT_PROXY) as client:
            resp = client.get(url, params=params, follow_redirects=True)
```

- [ ] **Step 2: Commit**

```bash
git add webapp/backend/patent_search.py
git commit -m "feat(patent): route search_patentsview through proxy"
```

---

## Task 7: 给 EPO OPS API 的两处 `httpx.Client` 加代理

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\patent_search.py:443` (token 获取)
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\patent_search.py:487-494` (搜索)

- [ ] **Step 1: 修改 EPO token 获取的 `httpx.Client` 调用**

定位到第 443 行：

```python
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                EPO_TOKEN_URL,
```

改为：

```python
        with httpx.Client(timeout=10.0, proxy=_PATENT_PROXY) as client:
            resp = client.post(
                EPO_TOKEN_URL,
```

- [ ] **Step 2: 修改 EPO 搜索的 `httpx.Client` 调用**

定位到第 487-494 行：

```python
        with httpx.Client(
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/xml",
                "User-Agent": BROWSER_HEADERS["User-Agent"],
            },
            timeout=timeout,
        ) as client:
```

改为：

```python
        with httpx.Client(
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/xml",
                "User-Agent": BROWSER_HEADERS["User-Agent"],
            },
            timeout=timeout,
            proxy=_PATENT_PROXY,
        ) as client:
```

- [ ] **Step 3: Commit**

```bash
git add webapp/backend/patent_search.py
git commit -m "feat(patent): route EPO OPS API through proxy"
```

---

## Task 8: 给 `search_wipo_patentscope` 加代理

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\patent_search.py:637-644`

- [ ] **Step 1: 修改 `search_wipo_patentscope` 的 `httpx.Client` 调用**

定位到第 637-644 行：

```python
        with httpx.Client(
            headers={
                **BROWSER_HEADERS,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            timeout=timeout,
            follow_redirects=True,
        ) as client:
```

改为：

```python
        with httpx.Client(
            headers={
                **BROWSER_HEADERS,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            timeout=timeout,
            follow_redirects=True,
            proxy=_PATENT_PROXY,
        ) as client:
```

- [ ] **Step 2: Commit**

```bash
git add webapp/backend/patent_search.py
git commit -m "feat(patent): route search_wipo_patentscope through proxy"
```

---

## Task 9: 在 `.env` 文件添加 `PATENT_PROXY` 配置

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\.env`

- [ ] **Step 1: 读取现有 `.env` 文件**

运行：
```bash
python -c "from pathlib import Path; p = Path('.env'); print(p.read_text(encoding='utf-8') if p.exists() else 'NO .env FILE')"
```

- [ ] **Step 2: 在 `.env` 文件末尾追加 `PATENT_PROXY` 配置**

如果 `.env` 文件存在，在末尾追加（如果已有 `PATENT_PROXY` 行则跳过）：

```
# 专利数据源代理（Clash/V2Ray 本地代理）
# 默认 http://127.0.0.1:7890（Clash 默认端口）
# 设为空字符串则禁用代理（直连，国内会 503）
PATENT_PROXY=http://127.0.0.1:7890
```

如果 `.env` 文件不存在，跳过此 Task（代码有默认值，不依赖 `.env`）。

- [ ] **Step 3: 验证环境变量被正确读取**

运行：
```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(f'PATENT_PROXY from env: {os.environ.get(\"PATENT_PROXY\", \"(not set)\")!r}')"
```

预期输出：
```
PATENT_PROXY from env: 'http://127.0.0.1:7890'
```

- [ ] **Step 4: Commit**

```bash
git add webapp/backend/.env
git commit -m "chore(config): add PATENT_PROXY to .env"
```

---

## Task 10: 端到端验证 — 搜索 + 全文抓取 + 降级

**Files:**
- Create: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\_test_proxy_impl.py`（临时测试脚本，验证后删除）

- [ ] **Step 1: 创建端到端验证脚本**

```python
"""端到端验证：代理访问 Google Patents 全文 + 降级"""
import os
import time
from dotenv import load_dotenv
load_dotenv()

from patent_search import (
    _PATENT_PROXY,
    search_google_patents,
    search_google_scholar,
    fetch_patent_detail,
    search_by_strategies,
)

print(f"当前代理: {_PATENT_PROXY!r}")
print()

# 测试 1: 搜索走代理
print("=" * 60)
print("测试 1: search_google_patents 走代理")
print("=" * 60)
t0 = time.time()
hits = search_google_patents("lithium battery termination tape", num=5, timeout=15.0)
dt = time.time() - t0
print(f"找到 {len(hits)} 篇，耗时 {dt:.1f}s")
for p in hits[:3]:
    print(f"  {p.patent_number} | {p.title[:50]}")
print()

# 测试 2: 全文抓取走代理
print("=" * 60)
print("测试 2: fetch_patent_detail 走代理（拿全文）")
print("=" * 60)
if hits:
    test_num = hits[0].patent_number
    t0 = time.time()
    detail = fetch_patent_detail(test_num, timeout=15.0)
    dt = time.time() - t0
    has_claims = "[Claims]" in detail
    has_desc = "[Description]" in detail
    print(f"专利 {test_num}: {len(detail)} chars, {dt:.1f}s")
    print(f"  含 [Claims]: {has_claims}")
    print(f"  含 [Description]: {has_desc}")
    if has_claims and has_desc:
        print("  ✅ 全文抓取成功！")
    else:
        print("  ⚠️ 未拿到全文（可能代理未开启，降级到摘要）")
print()

# 测试 3: 降级测试（临时禁用代理）
print("=" * 60)
print("测试 3: 禁用代理后降级到 Scholar")
print("=" * 60)
import patent_search
original_proxy = patent_search._PATENT_PROXY
patent_search._PATENT_PROXY = None  # 临时禁用
try:
    t0 = time.time()
    detail = fetch_patent_detail("US9755207B2", timeout=8.0)
    dt = time.time() - t0
    has_abstract = "[Abstract]" in detail
    has_claims = "[Claims]" in detail
    print(f"禁用代理后: {len(detail)} chars, {dt:.1f}s")
    print(f"  含 [Abstract]: {has_abstract}")
    print(f"  含 [Claims]: {has_claims}")
    if has_abstract and not has_claims:
        print("  ✅ 降级成功（拿到摘要，无全文）")
finally:
    patent_search._PATENT_PROXY = original_proxy  # 恢复
print()

# 测试 4: 完整搜索流程（多角度）
print("=" * 60)
print("测试 4: search_by_strategies 完整流程")
print("=" * 60)
strats = [
    {"angle": "材料组成", "query": "lithium battery termination tape electrolyte", "rationale": ""},
    {"angle": "粘接性能", "query": "pressure sensitive adhesive battery tape", "rationale": ""},
]
t0 = time.time()
results = search_by_strategies(strats, num_per_angle=3, total=5)
dt = time.time() - t0
print(f"找到 {len(results)} 篇专利，耗时 {dt:.1f}s")
for p in results[:5]:
    print(f"  {p.patent_number} | {p.source} | {p.title[:50]}")
print()

print("=" * 60)
print("全部测试完成")
print("=" * 60)
```

- [ ] **Step 2: 运行验证脚本**

运行：
```bash
python _test_proxy_impl.py
```

预期输出（代理可用时）：
```
当前代理: 'http://127.0.0.1:7890'

测试 1: search_google_patents 走代理
找到 5 篇，耗时 ~3s
  US... | ...
  ...

测试 2: fetch_patent_detail 走代理（拿全文）
专利 US...: ... chars, ~3s
  含 [Claims]: True
  含 [Description]: True
  ✅ 全文抓取成功！

测试 3: 禁用代理后降级到 Scholar
禁用代理后: ~180 chars, ~5s
  含 [Abstract]: True
  含 [Claims]: False
  ✅ 降级成功（拿到摘要，无全文）

测试 4: search_by_strategies 完整流程
找到 5 篇专利，耗时 ~10s
  ...

全部测试完成
```

关键验证点：
- 测试 2: `含 [Claims]: True` 和 `含 [Description]: True` 必须为 True
- 测试 3: 降级到摘要，`含 [Claims]: False`
- 测试 4: 多角度搜索能找到专利

- [ ] **Step 3: 删除临时测试脚本**

```bash
del _test_proxy_impl.py
```

- [ ] **Step 4: Commit（仅提交代码变更，不含测试脚本）**

```bash
git status  # 确认 _test_proxy_impl.py 已删除，不在提交中
git add -A
git commit --allow-empty -m "test(patent): verify proxy access end-to-end"
```

---

## Task 11: 端到端验证 — 完整报告生成流程

**Files:**
- 无文件改动，仅手动验证

- [ ] **Step 1: 确保后端服务在运行**

运行：
```bash
python -c "import urllib.request; r = urllib.request.urlopen('http://localhost:8001/api/health', timeout=3); print(f'Backend: {r.status}')"
```

如果未运行，启动后端：
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

- [ ] **Step 2: 在前端 http://localhost:5173 完整跑一次流程**

1. 输入 VOC（如"锂电池终止胶带"）
2. 点击"AI 生成检索关键词"
3. 确认策略
4. 点击"确认并检索专利"
5. 选择 5-8 篇专利
6. 点击"生成报告"
7. 等待报告生成完成

- [ ] **Step 3: 验证报告核心章节不再空白**

打开生成的报告 Markdown，检查以下章节是否有实质内容（不再是空标题）：

- 第 6 章「Patent Technical Extraction Summary」— 应有每篇专利的 Key Xs / Key Ys
- 第 7 章「Test Method Comparability」— 应有测试方法对比
- 第 8 章「Cross-Evidence X-Y Synthesis」— 应有 X-Y 关系矩阵
- 第 11 章「Experiment Portfolio」— 应有实验组合
- 第 12 章「DOE Details」— 应有 DOE 实验设计

关键验证点：对比之前的 `_report_check.txt`（这些章节空白），现在应有内容。

- [ ] **Step 4: 如果报告被截断（LLM 输出 8192 tokens 上限），记录现象**

如果报告在某个章节突然中断（如第 10 章后没有内容），说明 LLM 输出被截断。记录截断位置，后续单独处理 `max_tokens` 问题（不在本次范围）。

- [ ] **Step 5: Commit 验证记录**

```bash
git add -A
git commit --allow-empty -m "test(patent): verify full report generation with proxy access"
```

---

## 完成标准

- [ ] `_PATENT_PROXY` 常量定义正确，支持环境变量覆盖
- [ ] 8 处 `httpx.Client` 调用全部加了 `proxy=_PATENT_PROXY` 参数
- [ ] 代理可用时，`fetch_patent_detail` 返回含 `[Claims]` + `[Description]` 的全文
- [ ] 代理不可用时，自动降级到 Scholar 摘要（行为与改动前一致）
- [ ] 完整报告生成流程跑通，第 6/7/8 章不再空白
- [ ] 所有改动已 commit

## 不在本次范围

- LLM `max_tokens=8192` 上限调整（验证报告是否被截断后再决定）
- 本地缓存（方案 B）
- 数据充分性标注（方案 C）
- `prompt_builder` 截断逻辑调整
