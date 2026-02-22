import anthropic
from .models import DrugInput
from .prompts import SYSTEM_PROMPT, MARKET_LANDSCAPE_TEMPLATE, PRODUCT_AND_COMPETITIVE_TEMPLATE


class PharmaceuticalAnalyzer:
    """Orchestrates multi-step LLM calls to generate pharmaceutical market analysis reports."""

    MODEL = "claude-opus-4-6"
    MAX_TOKENS = 8096

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_market_landscape(self, drug_input: DrugInput) -> str:
        """Generate Section 1: Market landscape (市场格局判断)."""
        prompt = MARKET_LANDSCAPE_TEMPLATE.format(
            drug_context=self._format_drug_context(drug_input),
            indication=drug_input.indication,
            market_region=drug_input.market_region,
        )
        return self._call(prompt)

    def generate_product_and_competitive(
        self, drug_input: DrugInput, market_analysis: str
    ) -> str:
        """Generate Section 2 (product analysis) and Section 3 (competitive comparison)."""
        prompt = PRODUCT_AND_COMPETITIVE_TEMPLATE.format(
            drug_context=self._format_drug_context(drug_input),
            market_analysis=market_analysis,
            drug_name=drug_input.drug_name,
            indication=drug_input.indication,
            market_region=drug_input.market_region,
        )
        return self._call(prompt)

    def analyze(self, drug_input: DrugInput) -> str:
        """Run the full two-step analysis and return the combined Markdown report."""
        market = self.generate_market_landscape(drug_input)
        product_competitive = self.generate_product_and_competitive(drug_input, market)
        return (
            f"# {drug_input.drug_name} 市场分析报告\n\n"
            f"{market}\n\n---\n\n"
            f"{product_competitive}"
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _format_drug_context(self, drug_input: DrugInput) -> str:
        lines = [
            f"药品名称: {drug_input.drug_name}",
            f"治疗领域: {drug_input.therapeutic_area}",
            f"主要适应症: {drug_input.indication}",
            f"关键成分: {drug_input.key_ingredients}",
            f"剂型: {drug_input.dosage_form}",
            f"研发阶段: {drug_input.development_stage}",
            f"目标市场: {drug_input.market_region}",
        ]
        if drug_input.mechanism_of_action:
            lines.append(f"作用机制: {drug_input.mechanism_of_action}")
        if drug_input.target_patient:
            lines.append(f"目标患者: {drug_input.target_patient}")
        if drug_input.unique_features:
            lines.append(f"独特特点: {drug_input.unique_features}")
        if drug_input.competitors_focus:
            lines.append(f"重点竞品: {drug_input.competitors_focus}")
        if drug_input.additional_context:
            lines.append(f"\n【额外背景信息】\n{drug_input.additional_context}")
        return "\n".join(lines)

    def _call(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
