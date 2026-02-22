"""Streamlit web UI for pharmaceutical market analysis."""

import os

import streamlit as st
from dotenv import load_dotenv

from src.analyzer import PharmaceuticalAnalyzer
from src.models import DrugInput

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="医药市场分析工具",
    page_icon="💊",
    layout="wide",
)

st.title("💊 医药市场竞争格局分析系统")
st.markdown(
    "输入 pipeline 药物的基本信息，自动生成包含**市场格局、产品定位与竞品对比**的专业分析报告。"
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 设置")
    api_key = st.text_input(
        "Anthropic API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="也可以在 .env 文件中设置 ANTHROPIC_API_KEY",
    )
    st.divider()
    st.markdown(
        """
**报告包含三大部分：**
1. 市场格局判断（流行病学、治疗格局、未来趋势）
2. 产品分析（特点解读、定位方案）
3. 竞品对比（多维度对比表格）

**模型：** claude-opus-4-6
**预计生成时间：** 2–4 分钟
        """
    )

# ── Input form ────────────────────────────────────────────────────────────────
with st.form("drug_input_form"):
    st.subheader("📋 药物基本信息")

    col1, col2 = st.columns(2)

    with col1:
        drug_name = st.text_input(
            "药品名称/代号 *",
            placeholder="如：EternaTear、AZR-MD-001、候选药XYZ",
        )
        therapeutic_area = st.text_input(
            "治疗领域 *",
            placeholder="如：眼科、肿瘤、心血管、神经科",
        )
        indication = st.text_input(
            "主要适应症 *",
            placeholder="如：干眼症、非小细胞肺癌、心房颤动",
        )
        dosage_form = st.text_input(
            "剂型 *",
            placeholder="如：眼用乳液、口服片剂、皮下注射、鼻喷雾剂",
        )
        development_stage = st.selectbox(
            "研发阶段 *",
            ["临床前", "I期临床", "II期临床", "III期临床", "NDA/申报中", "已上市"],
        )
        market_region = st.selectbox(
            "目标市场",
            ["中国", "美国", "欧洲", "全球"],
        )

    with col2:
        key_ingredients = st.text_area(
            "关键成分/活性物质 *",
            placeholder=(
                "请详细描述，包括浓度和关键特性\n"
                "如：4.5%矿物油（35nm颗粒）、蜂蜡（增稠）、透明质酸（保湿）"
            ),
            height=110,
        )
        mechanism_of_action = st.text_area(
            "作用机制",
            placeholder=(
                "如：通过矿物油+蜂蜡形成脂质层封锁，提升泪膜脂质层厚度（LLT），"
                "防止泪液蒸发"
            ),
            height=90,
        )
        target_patient = st.text_input(
            "目标患者群体",
            placeholder="如：脂质异常型/混合型中重度干眼症患者",
        )
        unique_features = st.text_area(
            "独特特点/差异化优势",
            placeholder=(
                "如：粒径2–45微米、PureFlow无防腐剂多次使用瓶、"
                "戴隐形眼镜时可使用、zeta电位−80~−100mV稳定性高"
            ),
            height=80,
        )

    st.divider()

    competitors_focus = st.text_input(
        "重点竞品（可选，留空则自动识别）",
        placeholder="如：Miebo、Systane Complete PF、Retaine MGD、恒沁",
    )
    additional_context = st.text_area(
        "额外背景信息（可粘贴临床数据、专利信息、现有研究等）",
        placeholder=(
            "如：临床试验结果摘要、专利到期时间、已知定价策略、"
            "监管进展、公司内部调研数据等"
        ),
        height=120,
    )

    submitted = st.form_submit_button(
        "🔍 生成市场分析报告",
        type="primary",
        use_container_width=True,
    )

# ── Analysis ──────────────────────────────────────────────────────────────────
if submitted:
    required = {
        "药品名称": drug_name,
        "治疗领域": therapeutic_area,
        "主要适应症": indication,
        "关键成分": key_ingredients,
        "剂型": dosage_form,
    }
    missing = [k for k, v in required.items() if not v.strip()]

    if not api_key:
        st.error("请在侧边栏输入 Anthropic API Key。")
    elif missing:
        st.error(f"请填写必填字段：{', '.join(missing)}")
    else:
        drug_input = DrugInput(
            drug_name=drug_name.strip(),
            therapeutic_area=therapeutic_area.strip(),
            indication=indication.strip(),
            key_ingredients=key_ingredients.strip(),
            dosage_form=dosage_form.strip(),
            mechanism_of_action=mechanism_of_action.strip() or None,
            target_patient=target_patient.strip() or None,
            development_stage=development_stage,
            unique_features=unique_features.strip() or None,
            market_region=market_region,
            competitors_focus=competitors_focus.strip() or None,
            additional_context=additional_context.strip() or None,
        )

        analyzer = PharmaceuticalAnalyzer(api_key=api_key)

        progress = st.progress(0, text="正在启动分析...")

        try:
            # Step 1 ──────────────────────────────────────────────────────
            progress.progress(10, text="第1步：分析市场格局与治疗趋势（约1–2分钟）...")
            market_analysis = analyzer.generate_market_landscape(drug_input)
            progress.progress(55, text="第2步：分析产品定位与竞品对比（约1–2分钟）...")

            # Step 2 ──────────────────────────────────────────────────────
            product_competitive = analyzer.generate_product_and_competitive(
                drug_input, market_analysis
            )
            progress.progress(100, text="分析完成！")

            full_report = (
                f"# {drug_input.drug_name} 市场分析报告\n\n"
                f"{market_analysis}\n\n---\n\n"
                f"{product_competitive}"
            )

            st.success("✅ 报告生成完成！")

            # Download button ──────────────────────────────────────────────
            st.download_button(
                label="📥 下载完整报告 (Markdown)",
                data=full_report,
                file_name=f"{drug_input.drug_name}_市场分析报告.md",
                mime="text/markdown",
            )

            # Display report ───────────────────────────────────────────────
            st.divider()
            st.markdown(full_report)

        except Exception as exc:
            progress.empty()
            st.error(f"分析过程中出错：{exc}")
            st.exception(exc)
