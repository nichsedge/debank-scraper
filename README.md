# DeBank Scraper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An async, headless browser-based scraper and **Model Context Protocol (MCP)** server for extracting complete multi-chain EVM wallet portfolios, token balances, and DeFi protocol positions from [DeBank](https://debank.com).

---

## ✨ Features

* 🪙 **Multi-chain Token Balances**: Price, amount, USD value, and chain identification.
* 🚜 **DeFi Protocol Breakdown**: Pools, staking, lending, rewards, and LP positions across all EVM chains.
* 🤖 **MCP Server**: Query live wallet portfolios directly inside Claude, Cursor, Gemini, or Copilot.
* 📦 **Standalone CLI & Python Library**: Use in automated scripts or pipelines with zero hassle.

---

## 🔧 Prerequisites

* Python 3.11 or higher
* Chromium / Google Chrome installed (or install via `playwright install chromium`)
* [`uv`](https://docs.astral.sh/uv/getting-started/installation/)

---

## 🚀 Quick Start

### 1. CLI Usage

```bash
# Scrape specific EVM address to JSON file
uvx debank-scraper 0x1234567890abcdef1234567890abcdef12345678 --output ./data

# Or set EVM_ADDRESS in your environment
export EVM_ADDRESS="0x1234567890abcdef1234567890abcdef12345678"
uv run debank-scrape
```

---

### 2. Python Library Usage

```python
import asyncio
from debank_scraper import DeBankScraper, scrape_debank

async def main():
    scraper = DeBankScraper(headless=True)
    portfolio = await scraper.scrape("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
    print(f"Total Net Worth: {portfolio['wallet']['total_net_worth']}")
    print(f"Tokens: {len(portfolio['tokens'])}")
    print(f"Protocols: {len(portfolio['protocols'])}")

asyncio.run(main())
```

---

### 3. As an MCP Server

Add to your MCP client configuration (`claude_desktop_config.json`, Cursor, etc.):

```json
{
  "mcpServers": {
    "debank": {
      "type": "stdio",
      "command": "uvx",
      "args": ["debank-scraper", "debank-mcp"]
    }
  }
}
```

---

## 📄 License

Licensed under the MIT License. See [LICENSE](./LICENSE) for details.
