"""Tests for voc_scout — VOC Scout 交互式搜索模块。

注意：用裸导入（from voc_scout import ...）与后端约定一致；
conftest.py 已把 webapp/backend 加入 sys.path。
"""
import pytest
from pydantic import ValidationError

from voc_scout import (
    ScoutRound1Output,
    ScoutTechRoute,
    ScoutRound2Input,
    ScoutRound2Output,
    ScoutCompanyDetail,
    scout_round1,
)


class TestScoutRound1:
    """VOC Scout Round 1: 从原始 VOC 探索技术方向。"""

    def test_tech_route_model(self):
        """ScoutTechRoute 校验必填字段。"""
        route = ScoutTechRoute(
            id="1",
            name="BASF route — high solids general purpose",
            description="Acronal V 215 is the market benchmark, 69% solids",
            companies=["BASF"],
            products=["Acronal V 215"],
            key_diff="69% solids content, core patent expired",
            patent_status_hint="expired",
            confidence="★★☆",
        )
        assert route.id == "1"
        assert len(route.companies) == 1
        assert route.confidence == "★★☆"

    def test_round1_output_structure(self):
        """Round 1 输出包含领域分类、置信度、路线列表。"""
        output = ScoutRound1Output(
            domain_class="材料/化工",
            confidence="★★☆",
            analysis="This VOC targets high-solids acrylic emulsion PSAs for tapes.",
            routes=[],
        )
        assert output.domain_class == "材料/化工"
        assert output.confidence == "★★☆"
        assert isinstance(output.routes, list)

    def test_scout_round1_handles_empty_voc(self):
        """空 VOC 抛 ValueError。"""
        with pytest.raises(ValueError, match="VOC cannot be empty"):
            scout_round1(voc="")

    def test_scout_round1_handles_whitespace_only_voc(self):
        """纯空白 VOC 也抛 ValueError。"""
        with pytest.raises(ValueError, match="VOC cannot be empty"):
            scout_round1(voc="   \n\t  ")

    @pytest.mark.integration
    def test_scout_round1_returns_routes(self):
        """scout_round1 调 LLM 返回 4-6 条带领域分类的技术路线。

        集成测试：需要 DEEPSEEK_API_KEY，无 key 时自动跳过。
        """
        import os
        if not os.environ.get("DEEPSEEK_API_KEY"):
            pytest.skip("DEEPSEEK_API_KEY not set — skipping integration test")

        result = scout_round1(
            voc="高固含量高粘性的乳液体系丙烯酸酯压敏胶",
        )
        assert result.domain_class in ("材料/化工", "电子", "医疗", "法规驱动型", "机械")
        assert 4 <= len(result.routes) <= 6
        for route in result.routes:
            assert route.id
            assert route.name
            assert len(route.companies) >= 1
            assert route.confidence in ("★★★", "★★☆", "★☆☆")


class TestScoutRound2:
    """VOC Scout Round 2: 钻入用户选定的路线。"""

    def test_round2_input_requires_at_least_one_route(self):
        """Round2Input 拒绝空 selected_route_ids 列表（Pydantic v2 ValidationError）。"""
        with pytest.raises(ValidationError):
            ScoutRound2Input(voc="test", selected_route_ids=[])

    def test_round2_input_accepts_selected_routes(self):
        """Round2Input 接受非空 selected_route_ids。"""
        inp = ScoutRound2Input(voc="test", selected_route_ids=["1", "3"])
        assert inp.selected_route_ids == ["1", "3"]

    def test_round2_output_has_company_details(self):
        """Round2Output 含每条路线下公司的专利信息。"""
        detail = ScoutCompanyDetail(
            level="P0",
            name="BASF",
            tech_summary="High solids general purpose, 69% solids",
            patent_number="US6927267B1",
            patent_status="expired",
            key_ctq={"solid_content": "69%", "source": "[T]"},
            notes=["Core patent expired, no FTO risk"],
            source_labels=["[T]", "[P]"],
        )
        assert detail.level == "P0"
        assert detail.patent_status == "expired"
        assert detail.key_ctq["source"] == "[T]"
