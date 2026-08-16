# DeBank Scraper

[![PyPI version](https://img.shields.io/pypi/v/debank-scraper.svg)](https://pypi.org/project/debank-scraper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Server](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![Playwright](https://img.shields.io/badge/Playwright-Headless%20Scraper-orange.svg)](https://playwright.dev/)

An asynchronous, headless browser-based scraper and **Model Context Protocol (MCP)** server for extracting complete multi-chain EVM wallet portfolios, token balances, and DeFi protocol positions from [DeBank](https://debank.com).

---

## ✨ Features

* 🪙 **Multi-Chain Token Balances**: Retrieves price, amount, USD value, and chain identification for all held assets.
* 🚜 **DeFi Protocol Breakdown**: Extracts pools, staking, lending, reward balances, and LP positions across EVM chains.
* 🤖 **MCP Server Support**: Exposes tools and resources to query live wallet portfolios directly inside AI assistants (Claude, Cursor, Gemini, Copilot).
* ⚡ **Fast & Asynchronous**: Built with Playwright and modern async Python (`asyncio`).
* 📦 **CLI & Library Ready**: Run as a standalone CLI tool, import as a Python library, or run as a stdio MCP server.

---

## 🔧 Prerequisites

* Python 3.11 or higher
* [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or `pip`
* Chromium browser installed (install via `playwright install chromium`)

---

## 📦 Installation

### From PyPI (Recommended)

```bash
# Using uv (recommended)
uv add debank-scraper
# or install CLI globally
uv tool install debank-scraper

# Using pip
pip install debank-scraper

# Install browser binaries
playwright install chromium
```

### From Source

```bash
# Clone the repository
git clone https://github.com/nichsedge/debank-scraper.git
cd debank-scraper

# Install dependencies and setup Playwright
uv sync
uv run playwright install chromium
```

---

## 🚀 Usage

### 1. CLI Usage

Run directly using `uv run` or via `uvx`:

```bash
# Scrape specific EVM address to default ./data directory
uv run debank-scrape 0x1234567890abcdef1234567890abcdef12345678

# Save to a custom output directory or file
uv run debank-scrape 0x1234567890abcdef1234567890abcdef12345678 -o ./output/portfolio.json

# Run with visible browser (non-headless) for debugging
uv run debank-scrape 0x1234567890abcdef1234567890abcdef12345678 --no-headless

# Use environment variables
export EVM_ADDRESS="0x1234567890abcdef1234567890abcdef12345678"
export PORTFOLIO_DATA_DIR="./data"
uv run debank-scrape
```

#### CLI Options

| Option | Flag | Description |
| :--- | :--- | :--- |
| `address` | Positional | Target EVM address (or defaults to `EVM_ADDRESS` env var) |
| Output Path | `-o`, `--output` | Destination file or directory for the output JSON |
| Visible Mode | `--no-headless` | Open browser window in non-headless mode |
| Timeout | `--timeout` | Page load timeout in milliseconds (default: `30000`) |

---

### 2. Python Library Usage

```python
import asyncio
from debank_scraper import DeBankScraper, scrape_debank

async def main():
    scraper = DeBankScraper(headless=True)
    portfolio = await scraper.scrape("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")

    print(f"Total Net Worth: {portfolio['wallet']['total_net_worth']}")
    print(f"Tokens tracked: {len(portfolio['tokens'])}")
    print(f"Protocols active: {len(portfolio['protocols'])}")

asyncio.run(main())
```

---

### 3. Model Context Protocol (MCP) Server

Connect DeBank Scraper to your MCP client (Claude Desktop, Cursor, etc.).

#### Claude Desktop Configuration

Add to `claude_desktop_config.json` (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "debank": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/debank-scraper",
        "run",
        "debank-mcp"
      ]
    }
  }
}
```

#### Available MCP Capabilities

* **Tool**: `get_wallet_portfolio(address: str)` — Retrieves complete token holdings, protocol yields, and DeFi positions for any EVM wallet address.
* **Resource**: `debank://wallet/{address}` — Dynamic resource providing raw JSON portfolio data for an EVM wallet address.

---

## 📊 Output Data Schema

The scraper outputs structured JSON containing:

```json
{
  "timestamp": "2026-08-15T01:23:45.678Z",
  "wallet": {
    "total_net_worth": "$125,430.50",
    "change_24h": "+2.4%"
  },
  "social": {
    "ranking": "1,234",
    "followers": "56",
    "following": "12",
    "tvf": "$1.2M"
  },
  "tokens": [
    {
      "symbol": "ETH",
      "chain": "eth",
      "price": "$2,650.00",
      "amount": "10.5",
      "usd_value": "$27,825.00"
    }
  ],
  "protocols": [
    {
      "name": "Aave V3",
      "chain": "eth",
      "net_usd_value": "$50,000.00",
      "portfolio_items": [...]
    }
  ],
  "nfts": []
}
```

---

## 📄 License

Distributed under the MIT License. See [LICENSE](./LICENSE) for details.
