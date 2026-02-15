#!/usr/bin/env python3
"""Custom financial chatbot powered by FINAL_FINANCIAL_DATASET.csv."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from typing import Optional


DATA_FILE = "FINAL_FINANCIAL_DATASET.csv"

METRIC_ALIASES = {
    "revenue": "Total Revenue (USD millions)",
    "total revenue": "Total Revenue (USD millions)",
    "income": "Net Income (USD millions)",
    "net income": "Net Income (USD millions)",
    "profit": "Net Income (USD millions)",
    "assets": "Total Assets (USD millions)",
    "total assets": "Total Assets (USD millions)",
    "liabilities": "Total Liabilities (USD millions)",
    "total liabilities": "Total Liabilities (USD millions)",
    "debt": "Total Liabilities (USD millions)",
    "cash flow": "Operating Cash Flow (USD millions)",
    "operating cash flow": "Operating Cash Flow (USD millions)",
    "cfo": "Operating Cash Flow (USD millions)",
}


@dataclass
class BotContext:
    rows: list[dict[str, object]]
    companies: list[str]
    years: list[int]


def load_data(path: str = DATA_FILE) -> BotContext:
    rows: list[dict[str, object]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean: dict[str, object] = {
                "Company": str(row["Company"]),
                "Fiscal Year (filename)": int(row["Fiscal Year (filename)"]),
                "File": row["File"],
            }
            for metric in set(METRIC_ALIASES.values()):
                clean[metric] = float(row[metric])
            rows.append(clean)

    companies = sorted({str(r["Company"]) for r in rows})
    years = sorted({int(r["Fiscal Year (filename)"]) for r in rows})
    return BotContext(rows=rows, companies=companies, years=years)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def find_company(query: str, companies: list[str]) -> Optional[str]:
    q = normalize_text(query)
    for company in companies:
        if company.lower() in q:
            return company
    return None


def find_year(query: str, years: list[int]) -> Optional[int]:
    m = re.search(r"(20\d{2})", query)
    if m:
        year = int(m.group(1))
        if year in years:
            return year
    return None


def find_metric(query: str) -> Optional[str]:
    q = normalize_text(query)
    for alias, metric in sorted(METRIC_ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
        if alias in q:
            return metric
    return None


def money(value: float) -> str:
    return f"${value:,.0f}M"


def get_row(ctx: BotContext, company: str, year: int) -> Optional[dict[str, object]]:
    for row in ctx.rows:
        if str(row["Company"]).lower() == company.lower() and int(row["Fiscal Year (filename)"]) == year:
            return row
    return None


def handle_query(ctx: BotContext, query: str) -> str:
    q = normalize_text(query)
    if q in {"help", "h", "?"}:
        return help_text(ctx)

    if "list companies" in q or "companies" == q:
        return "Companies: " + ", ".join(ctx.companies)

    if "list years" in q or "years" == q:
        return "Years: " + ", ".join(str(y) for y in ctx.years)

    if "top" in q or "highest" in q:
        metric = find_metric(q)
        year = find_year(q, ctx.years)
        if not metric or not year:
            return "Please specify both metric and year. Example: top revenue in 2025"
        yearly = [r for r in ctx.rows if int(r["Fiscal Year (filename)"]) == year]
        top_row = sorted(yearly, key=lambda r: float(r[metric]), reverse=True)[0]
        return f"Top {metric} in {year}: {top_row['Company']} with {money(float(top_row[metric]))}."

    if "compare" in q:
        metric = find_metric(q)
        year = find_year(q, ctx.years)
        if not metric or not year:
            return "For compare, include metric and year. Example: compare net income 2024"
        yearly = [r for r in ctx.rows if int(r["Fiscal Year (filename)"]) == year]
        yearly = sorted(yearly, key=lambda r: float(r[metric]), reverse=True)
        lines = [f"{metric} in {year}:"]
        for row in yearly:
            lines.append(f"- {row['Company']}: {money(float(row[metric]))}")
        return "\n".join(lines)

    if "growth" in q or "change" in q:
        company = find_company(q, ctx.companies)
        metric = find_metric(q)
        years = sorted(set(int(y) for y in re.findall(r"20\d{2}", q)))
        if not company or not metric or len(years) < 2:
            return (
                "For growth, include company, metric, and two years. "
                "Example: growth of Tesla revenue from 2023 to 2025"
            )
        y1, y2 = years[0], years[-1]
        if y1 not in ctx.years or y2 not in ctx.years:
            return f"Available years are: {', '.join(str(y) for y in ctx.years)}"
        r1 = get_row(ctx, company, y1)
        r2 = get_row(ctx, company, y2)
        if r1 is None or r2 is None:
            return f"Missing data for {company} in {y1} or {y2}."
        old = float(r1[metric])
        new = float(r2[metric])
        delta = new - old
        pct = (delta / old) * 100 if old else 0
        sign = "+" if delta >= 0 else "-"
        return (
            f"{company} {metric} changed from {money(old)} ({y1}) to {money(new)} ({y2}): "
            f"{sign}{money(abs(delta))} ({sign}{abs(pct):.2f}%)."
        )

    company = find_company(q, ctx.companies)
    year = find_year(q, ctx.years)
    metric = find_metric(q)

    if company and year and metric:
        row = get_row(ctx, company, year)
        if row is None:
            return f"No data for {company} in {year}."
        return f"{company} {metric} in {year}: {money(float(row[metric]))}."

    if company and ("summary" in q or "overview" in q):
        latest = max(ctx.years)
        row = get_row(ctx, company, latest)
        if row is None:
            return f"No summary available for {company}."
        return (
            f"{company} summary ({latest}):\n"
            f"- Revenue: {money(float(row['Total Revenue (USD millions)']))}\n"
            f"- Net Income: {money(float(row['Net Income (USD millions)']))}\n"
            f"- Total Assets: {money(float(row['Total Assets (USD millions)']))}\n"
            f"- Total Liabilities: {money(float(row['Total Liabilities (USD millions)']))}\n"
            f"- Operating Cash Flow: {money(float(row['Operating Cash Flow (USD millions)']))}"
        )

    return (
        "I couldn't understand that. Type `help` for examples.\n"
        "Tip: ask like 'Apple revenue 2025' or 'compare net income 2024'."
    )


def help_text(ctx: BotContext) -> str:
    return (
        "Custom Financial Chatbot\n"
        f"- Companies: {', '.join(ctx.companies)}\n"
        f"- Years: {', '.join(str(y) for y in ctx.years)}\n\n"
        "Examples:\n"
        "- Apple revenue 2025\n"
        "- compare net income 2024\n"
        "- top operating cash flow 2025\n"
        "- growth of Tesla revenue from 2023 to 2025\n"
        "- Microsoft summary\n"
        "- list companies\n"
        "- list years\n"
        "- exit"
    )


def main() -> None:
    ctx = load_data()
    print("Financial Chatbot ready. Type `help` for sample questions. Type `exit` to quit.")
    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBot: Bye.")
            break
        if not user:
            continue
        if normalize_text(user) in {"exit", "quit"}:
            print("Bot: Bye.")
            break
        print("Bot:", handle_query(ctx, user))


if __name__ == "__main__":
    main()
