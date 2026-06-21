"""测试 /api/upload-doc 端点"""
import os
import sys

# 清除代理环境变量
for k in list(os.environ.keys()):
    if k.lower().endswith('proxy'):
        del os.environ[k]

import requests

API_BASE = "http://localhost:8001"

# 创建一个简单的测试文本文件（模拟 docx）
test_content = """Test Document

Technical Points:
This document describes a new lithium battery tape technology. The tape uses polyimide substrate with acrylic adhesive coating.

Application Scenarios:
- Power battery cell internal fixation
- High temperature environment (above 120C) use
- Scenarios requiring electrolyte corrosion resistance

Main Conclusions:
The tape maintains good adhesion performance at 120C high temperature, with剥离 force retention rate exceeding 85% after 500 hours of electrolyte immersion.

Key Data:
- Substrate thickness: 25 um
- Peel force: >= 8 N/cm
- Temperature resistance: 150C/24h
- Electrolyte immersion retention: >= 85%
""".encode('utf-8')

# 测试 /api/health
print("测试 /api/health...")
r = requests.get(f"{API_BASE}/api/health")
print(f"  状态码: {r.status_code}")
print(f"  响应: {r.json()}")
print()

# 测试上传文件
print("测试 /api/upload-doc...")
files = {
    'file': ('test_document.docx', test_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
}
data = {
    'doc_name': 'test_lithium_battery_tape.docx'
}

try:
    r = requests.post(f"{API_BASE}/api/upload-doc", files=files, data=data, timeout=120)
    print(f"  状态码: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"  文件名: {result.get('doc_name')}")
        print(f"  原文预览（前200字）: {result.get('text_preview', '')[:200]}...")
        print(f"  分析结果:")
        print(result.get('analysis', '')[:500])
    else:
        print(f"  错误: {r.text}")
except Exception as e:
    print(f"  请求失败: {e}")

print()
print("测试完成")
