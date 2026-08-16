"""
DeBank EVM Portfolio Scraper and MCP Server
"""

from debank_scraper.scraper import DeBankScraper, clean_address, scrape_debank

__version__ = "0.1.0"
__all__ = ["DeBankScraper", "clean_address", "scrape_debank"]
