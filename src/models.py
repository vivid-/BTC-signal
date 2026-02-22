from pydantic import BaseModel, Field
from typing import Optional


class DrugInput(BaseModel):
    drug_name: str = Field(..., description="药品名称/代号")
    therapeutic_area: str = Field(..., description="治疗领域（如眼科、肿瘤、心血管）")
    indication: str = Field(..., description="主要适应症（如干眼症、非小细胞肺癌）")
    key_ingredients: str = Field(..., description="关键成分/活性物质（如4.5%矿物油、环孢素0.05%）")
    dosage_form: str = Field(..., description="剂型（如眼用乳液、口服片剂、注射液）")
    mechanism_of_action: Optional[str] = Field(None, description="作用机制")
    target_patient: Optional[str] = Field(None, description="目标患者群体")
    development_stage: str = Field(..., description="研发阶段（临床前/I期/II期/III期/NDA/上市）")
    unique_features: Optional[str] = Field(None, description="独特特点/差异化优势")
    market_region: str = Field(default="中国", description="目标市场")
    competitors_focus: Optional[str] = Field(None, description="需要重点分析的竞品（可选）")
    additional_context: Optional[str] = Field(None, description="其他背景信息（临床数据、专利、定价等）")
