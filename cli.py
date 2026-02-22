#!/usr/bin/env python3
"""Command-line interface for pharmaceutical market analysis."""

import argparse
import os
import sys

from dotenv import load_dotenv

from src.analyzer import PharmaceuticalAnalyzer
from src.models import DrugInput


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pharma-analyze",
        description="医药市场竞争格局分析工具 — 输入pipeline药物信息，生成专业市场分析报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python cli.py \\
      --name "EternaTear" \\
      --area "眼科" \\
      --indication "干眼症" \\
      --ingredients "4.5%矿物油, 蜂蜡, 透明质酸" \\
      --form "眼用乳液" \\
      --stage "临床前" \\
      --output report.md
        """,
    )

    # Required
    req = parser.add_argument_group("必填参数")
    req.add_argument("--name", required=True, metavar="NAME", help="药品名称/代号")
    req.add_argument("--area", required=True, metavar="AREA", help="治疗领域（如眼科、肿瘤）")
    req.add_argument("--indication", required=True, metavar="IND", help="主要适应症（如干眼症）")
    req.add_argument(
        "--ingredients", required=True, metavar="ING", help="关键成分/活性物质（含浓度）"
    )
    req.add_argument("--form", required=True, metavar="FORM", help="剂型（如眼用乳液、口服片）")
    req.add_argument(
        "--stage",
        required=True,
        metavar="STAGE",
        help="研发阶段（临床前/I期/II期/III期/NDA/上市）",
    )

    # Optional
    opt = parser.add_argument_group("可选参数")
    opt.add_argument("--mechanism", metavar="MOA", help="作用机制")
    opt.add_argument("--target", metavar="PATIENT", help="目标患者群体")
    opt.add_argument("--features", metavar="FEAT", help="独特特点/差异化优势")
    opt.add_argument("--region", default="中国", metavar="REGION", help="目标市场（默认：中国）")
    opt.add_argument("--competitors", metavar="COMP", help="重点竞品（逗号分隔）")
    opt.add_argument("--context", metavar="CTX", help="额外背景信息（临床数据、专利等）")
    opt.add_argument("--output", metavar="FILE", help="输出文件路径（默认：打印到控制台）")
    opt.add_argument(
        "--api-key",
        metavar="KEY",
        help="Anthropic API Key（也可设置 ANTHROPIC_API_KEY 环境变量）",
    )
    opt.add_argument(
        "--section",
        choices=["all", "market", "product"],
        default="all",
        help="只生成指定部分：all（全部）、market（市场格局）、product（产品+竞品）",
    )

    return parser


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    api_key = args.api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "错误：请设置 ANTHROPIC_API_KEY 环境变量或使用 --api-key 参数",
            file=sys.stderr,
        )
        sys.exit(1)

    drug_input = DrugInput(
        drug_name=args.name,
        therapeutic_area=args.area,
        indication=args.indication,
        key_ingredients=args.ingredients,
        dosage_form=args.form,
        development_stage=args.stage,
        mechanism_of_action=args.mechanism,
        target_patient=args.target,
        unique_features=args.features,
        market_region=args.region,
        competitors_focus=args.competitors,
        additional_context=args.context,
    )

    analyzer = PharmaceuticalAnalyzer(api_key=api_key)

    def log(msg: str) -> None:
        print(msg, file=sys.stderr)

    report_parts: list[str] = [f"# {args.name} 市场分析报告\n"]

    if args.section in ("all", "market"):
        log("第1步：生成市场格局分析...")
        market = analyzer.generate_market_landscape(drug_input)
        report_parts.append(market)

    if args.section in ("all", "product"):
        market_ctx = report_parts[-1] if len(report_parts) > 1 else ""
        log("第2步：生成产品分析与竞品对比...")
        product_competitive = analyzer.generate_product_and_competitive(
            drug_input, market_ctx
        )
        if args.section == "all":
            report_parts.append("---")
        report_parts.append(product_competitive)

    report = "\n\n".join(report_parts)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        log(f"✅ 报告已保存到 {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
