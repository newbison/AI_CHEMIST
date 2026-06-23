"""Tests for deep_search — 迭代专利全景检索引擎。

注意：用裸导入（from deep_search import ...）与后端约定一致；
conftest.py 已把 webapp/backend 加入 sys.path。
"""
import json
import os
from unittest.mock import patch, MagicMock

import pytest
from pydantic import ValidationError

from deep_search import (
    DeepSearchInput,
    DeepSearchOutput,
    DeepSearchRoute,
    DeepSearchCompany,
    CTQEntry,
    FTOAssessment,
    FTOItem,
    Recommendation,
    ConvergenceStatus,
    NewTermsExtract,
    search_round_company,
    extract_new_terms,
    judge_convergence,
    extract_ctq_single,
    prescreen_patents,
    dedup_patents,
)
from patent_search import Patent


class TestDeepSearchTypes:
    """数据模型校验。"""

    def test_ctq_entry_with_source(self):
        """CTQ 条目需要值 + 来源标签。"""
        entry = CTQEntry(
            parameter="溶胀率",
            value="<30% vol",
            condition="60°C/24h, EC/DMC/DEC 1:1:1",
            method="VDA 278",
            source="[P]",
        )
        assert entry.source == "[P]"
        assert entry.value == "<30% vol"

    def test_convergence_status_defaults(self):
        """ConvergenceStatus 有合理默认值。"""
        status = ConvergenceStatus(
            converged=False,
            total_rounds=1,
            new_routes_this_round=3,
            new_companies_this_round=5,
            reason="Initial search — expecting more rounds",
        )
        assert not status.converged
        assert status.new_routes_this_round == 3

    def test_deep_search_output_structure(self):
        """完整输出含所有必需节。"""
        fto = FTOAssessment(high_risk=[FTOItem(patent="US123", company="X", note="n")])
        output = DeepSearchOutput(
            voc="test voc",
            domain_class="材料/化工",
            confidence="★★☆",
            search_path="R1(12家公司,5路线)→R2(+6家)→R3(+3家,收敛)",
            converged=True,
            total_rounds=3,
            total_companies_found=21,
            routes=[],
            ctq_table=[],
            fto=fto,
            recommendation=Recommendation(
                short_term="Buy BASF Acronal V 215 directly",
                medium_term="Develop bimodal particle size route",
                long_term="Monitor reactive surfactant direction",
            ),
            user_corrections=[],
        )
        assert output.converged is True
        assert output.total_rounds == 3
        assert len(output.fto.high_risk) == 1

    def test_fto_assessment_defaults_empty(self):
        """FTOAssessment 默认空列表。"""
        fto = FTOAssessment()
        assert fto.high_risk == []
        assert fto.medium_risk == []

    def test_deep_search_company_defaults(self):
        """DeepSearchCompany 默认 level=P2, 空 CTQ。"""
        c = DeepSearchCompany(name="TestCo")
        assert c.level == "P2"
        assert c.ctq == {}


class TestPatentRetrieval:
    """Deep Search 必须用 patent_search.py，不能 LLM 合成。"""

    def test_deep_search_uses_patent_search_py(self):
        """一轮 Deep Search 调 patent_search 函数，而非 LLM 造专利。"""
        mock_patents = [
            Patent(
                patent_number="US10717890B2",
                title="PVDF binder with acrylic copolymer",
                assignee="Arkema France",
                snippet="Swelling <30% vol in EC/DMC/DEC",
                publication_date="2020-07-21",
                source="google_patents",
                url="https://patents.google.com/patent/US10717890B2",
                country="US",
            ),
        ]
        with patch("deep_search.search_patentsview", return_value=mock_patents):
            with patch("deep_search.search_google_patents", return_value=mock_patents):
                with patch("deep_search.search_epo_ops", return_value=[]):
                    with patch("deep_search.search_wipo_patentscope", return_value=[]):
                        with patch("deep_search.search_cn_patents", return_value=[]):
                            result = search_round_company(
                                company_name="Arkema",
                                keywords=["PVDF binder swelling"],
                                ipc="H01M 4/62",
                            )
                            assert len(result) >= 1
                            assert result[0].patent_number == "US10717890B2"
                            # 必须非合成——必须来自 patent_search.py
                            assert result[0].assignee == "Arkema France"

    def test_deep_search_rejects_llm_synthesis(self):
        """patent_search.py 返回空时，Deep Search 绝不回退到 LLM 合成。
        必须返回空列表，不返回编造的专利。"""
        with patch("deep_search.search_patentsview", return_value=[]):
            with patch("deep_search.search_google_patents", return_value=[]):
                with patch("deep_search.search_epo_ops", return_value=[]):
                    with patch("deep_search.search_wipo_patentscope", return_value=[]):
                        with patch("deep_search.search_cn_patents", return_value=[]):
                            result = search_round_company(
                                company_name="NonexistentCo",
                                keywords=["imaginary invention"],
                            )
                            assert result == []  # 空，不编造

    def test_dedup_patents_removes_duplicates(self):
        """按 patent_number 去重（大小写/空格不敏感）。"""
        p1 = Patent("US123", "t1", "a", "s", "d", "src", "u", "US")
        p2 = Patent("us123", "dup", "a", "s", "d", "src", "u", "US")  # 同号大小写不同
        p3 = Patent("US456", "t3", "a", "s", "d", "src", "u", "US")
        result = dedup_patents([p1, p2, p3])
        assert len(result) == 2
        assert result[0].patent_number == "US123"

    def test_dedup_preserves_family_distinct(self):
        """同族不同号不合并（法律状态因国而异）。"""
        p1 = Patent("US10717890B2", "t", "a", "s", "d", "src", "u", "US")
        p2 = Patent("CN108123456B", "t", "a", "s", "d", "src", "u", "CN")
        result = dedup_patents([p1, p2])
        assert len(result) == 2  # 同族保留，供 Reduce 归并


class TestDeepSearchPipeline:
    """Deep Search LLM 管线测试。"""

    def test_judge_convergence_returns_status(self):
        """收敛检查返回带原因的结构化状态。"""
        status = judge_convergence(
            round_number=3,
            new_routes=0,
            new_companies=3,
            prev_new_companies=12,
            new_ipc=0,
            new_concepts=2,
        )
        assert status.converged is True
        assert "converged" in status.reason.lower() or "收敛" in status.reason

    def test_judge_convergence_not_converged_when_new_routes(self):
        """出现新路线时仍未收敛。"""
        status = judge_convergence(
            round_number=2,
            new_routes=1,
            new_companies=8,
            prev_new_companies=10,
            new_ipc=2,
            new_concepts=5,
        )
        assert status.converged is False

    def test_judge_convergence_converges_when_3_signals(self):
        """4 信号满足 3 个即收敛。"""
        # new_routes=0, company_ratio<0.3, new_ipc=0, new_concepts>=3 → 3 信号
        status = judge_convergence(
            round_number=3,
            new_routes=0,
            new_companies=2,
            prev_new_companies=10,
            new_ipc=0,
            new_concepts=5,
        )
        assert status.converged is True

    def test_prescreen_passthrough_when_under_limit(self):
        """专利数 ≤ max_select 时原样返回。"""
        nums = ["US1", "US2", "US3"]
        assert prescreen_patents(nums, max_select=50) == nums

    @pytest.mark.integration
    def test_extract_new_terms_from_sample_data(self):
        """给定样例搜索结果文本，提取结构化新词。需 API key。"""
        if not os.environ.get("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not set — skipping integration test")

        sample_text = """
        Patent US20250096272A1 (CATL): fluorine-free terpolymer binder, NMP soluble.
        Patent US10717890B2 (Arkema): PVDF + acrylic copolymer blend, <30% swelling.
        Patent EP4428167A1 (Nitto Belgium): reactive surfactant + tackifier, LSE.
        Also found: Sichuan Indigo Technology Co., Ltd. uses acrylonitrile copolymer.
        New IPC: C09J 11/06 appears frequently.
        """
        result = extract_new_terms(
            search_results_text=sample_text,
            known_keywords=["NMP soluble", "PVDF", "binder", "swelling"],
            known_companies=["Arkema", "CATL"],
            known_ipc=["H01M 4/62", "C09J 133/08"],
        )
        assert isinstance(result, dict)
        assert "keywords" in result
        assert "company_names" in result
        assert "ipc_codes" in result

    @pytest.mark.integration
    def test_extract_ctq_single_extracts_json(self):
        """给定单篇专利全文，提取 ≤300 字符的结构化 CTQ 记录。需 API key。"""
        if not os.environ.get("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not set — skipping integration test")

        sample_full_text = """
        [Abstract] A binder comprising PVDF and an acrylic copolymer...
        [Claims] 1. A binder wherein swelling is less than 30% by volume
        when immersed in EC/DMC/DEC at 60C for 24 hours.
        [Description] Example 1: 95wt% PVDF + 5wt% acrylic copolymer.
        The swelling ratio was measured as 25% vol.
        """
        record = extract_ctq_single(
            patent_number="US10717890B2",
            full_text=sample_full_text,
        )
        assert record["patent_number"] == "US10717890B2"
        assert len(record["ctq"]) >= 1

    def test_extract_ctq_returns_default_on_empty_text(self):
        """空/纯空白文本返回最小记录，不报错。"""
        record = extract_ctq_single("XX12345", "")
        assert record["patent_number"] == "XX12345"
        assert record["ctq"] == []

    def test_extract_ctq_returns_default_on_short_text(self):
        """过短文本返回最小记录。"""
        record = extract_ctq_single("XX12345", "ab")  # <50 字符
        assert record["ctq"] == []
        assert record["notes"] == "No full text available"
