# Custom Financial Chatbot

A lightweight command-line chatbot that answers financial questions from `FINAL_FINANCIAL_DATASET.csv`.

## Features

- Company/year/metric lookups (revenue, net income, assets, liabilities, operating cash flow)
- Cross-company comparison for a selected year and metric
- Top performer query by metric and year
- Growth analysis between two years
- Company summary for latest year in dataset
- No external dependencies (pure Python standard library)

## Dataset

Source file: `FINAL_FINANCIAL_DATASET.csv`

Included companies:
- Apple
- Microsoft
- Tesla

Included years:
- 2023
- 2024
- 2025

## Project Structure

```text
archive-chatbot/
├── custom_chatbot.py
├── FINAL_FINANCIAL_DATASET.csv
├── extract.py
└── README.md
```

## Quick Start

```bash
cd "/Users/ankurshah/Documents/New project/archive-chatbot"
python3 custom_chatbot.py
```

## Supported Question Types

- Direct lookup:
  - `Apple revenue 2025`
  - `Tesla net income 2024`
- Compare companies:
  - `compare net income 2024`
  - `compare revenue 2025`
- Top performer:
  - `top operating cash flow 2025`
  - `highest assets 2024`
- Growth/change:
  - `growth of Tesla revenue from 2023 to 2025`
  - `change in Apple net income 2024 to 2025`
- Summary:
  - `Microsoft summary`
- Utility commands:
  - `help`
  - `list companies`
  - `list years`
  - `exit`

## Sample Session

```text
You: Apple revenue 2025
Bot: Apple Total Revenue (USD millions) in 2025: $416,161M.

You: compare net income 2024
Bot: Net Income (USD millions) in 2024:
- Apple: $93,736M
- Microsoft: $88,136M
- Tesla: $14,974M

You: growth of Tesla revenue from 2023 to 2025
Bot: Tesla Total Revenue (USD millions) changed from $81,462M (2023) to $97,690M (2025): +$16,228M (+19.92%).
```

## Notes

- Values are reported in USD millions as stored in the dataset.
- If a question is not recognized, type `help` for valid patterns.
