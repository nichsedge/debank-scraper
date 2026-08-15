import os
import sys
import json
import logging
from typing import Any, Dict
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from debank_scraper.scraper import DeBankScraper

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("debank.mcp")

mcp = FastMCP(
    name="debank-scraper",
    instructions="MCP server for scraping and retrieving EVM wallet portfolio balances and DeFi positions from DeBank.",
)

_scraper = DeBankScraper(headless=True)


@mcp.tool()
async def get_wallet_portfolio(address: str) -> Dict[str, Any]:
    """
    Get complete token holdings, protocol yields, and DeFi positions for an EVM wallet address from DeBank.

    Args:
        address: The EVM wallet address (0x...) to scrape.
    """
    return await _scraper.scrape(address)


@mcp.resource("debank://wallet/{address}")
async def resource_wallet_portfolio(address: str) -> str:
    """Resource returning the complete JSON portfolio for an EVM wallet."""
    data = await _scraper.scrape(address)
    return json.dumps(data, indent=2, ensure_ascii=False)


def run():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
