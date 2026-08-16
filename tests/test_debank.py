import pytest
from debank_scraper.scraper import clean_address, DeBankScraper, scrape_debank
from debank_scraper import __version__
from debank_scraper.mcp import mcp


def test_version():
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_clean_address():
    # Standard lowercase
    assert clean_address("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045") == "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
    
    # Whitespace and quotes
    assert clean_address("  '0x1234567890abcdef1234567890abcdef12345678'  ") == "0x1234567890abcdef1234567890abcdef12345678"
    assert clean_address('  "0xABCDEF1234567890ABCDEF1234567890ABCDEF12"  ') == "0xabcdef1234567890abcdef1234567890abcdef12"
    
    # Empty cases
    assert clean_address("") == ""
    assert clean_address(None) == ""


def test_scraper_init():
    scraper = DeBankScraper(headless=True, timeout=15000)
    assert scraper.headless is True
    assert scraper.timeout == 15000

    scraper_visible = DeBankScraper(headless=False, timeout=60000)
    assert scraper_visible.headless is False
    assert scraper_visible.timeout == 60000


def test_scraper_empty_address_raises():
    scraper = DeBankScraper()
    with pytest.raises(ValueError, match="Invalid EVM wallet address"):
        import asyncio
        asyncio.run(scraper.scrape(""))


def test_mcp_server_setup():
    assert mcp.name == "debank-scraper"
    assert hasattr(mcp, "run")
