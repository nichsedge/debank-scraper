"""
Legacy shim for debank_scraper.debank
"""

from debank_scraper.cli import main
from debank_scraper.scraper import DeBankScraper, scrape_debank

__all__ = ["main", "DeBankScraper", "scrape_debank"]

if __name__ == "__main__":
    main()
