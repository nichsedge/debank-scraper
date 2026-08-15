import os
import sys
import json
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from debank_scraper.scraper import DeBankScraper


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="debank-scrape",
        description="Scrape EVM wallet portfolio and DeFi positions from DeBank",
    )
    parser.add_argument(
        "address",
        nargs="?",
        default=os.getenv("EVM_ADDRESS"),
        help="EVM wallet address (defaults to EVM_ADDRESS environment variable)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output directory or file path for the scraped JSON",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in non-headless (visible) mode",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30000,
        help="Page load timeout in milliseconds (default: 30000)",
    )

    args = parser.parse_args()

    if not args.address or args.address == "your_default_address_here":
        print(
            "❌ Error: EVM wallet address must be provided as an argument or via EVM_ADDRESS env var.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Determine output path
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_target = args.output
    if not output_target:
        data_dir = (
            os.getenv("PORTFOLIO_DATA_DIR")
            or os.getenv("DATA_DIR")
            or "./data"
        )
        output_path = Path(data_dir) / f"{current_date}_raw_debank.json"
    else:
        target_path = Path(output_target)
        if target_path.is_dir() or output_target.endswith("/"):
            output_path = target_path / f"{current_date}_raw_debank.json"
        else:
            output_path = target_path

    print(f"Scraping DeBank for wallet: {args.address}...", file=sys.stderr)
    scraper = DeBankScraper(headless=not args.no_headless, timeout=args.timeout)

    try:
        data = asyncio.run(scraper.scrape_to_file(args.address, output_path))
        net_worth = data.get("wallet", {}).get("total_net_worth", "N/A")
        tokens_count = len(data.get("tokens", []))
        protocols_count = len(data.get("protocols", []))
        print(
            f"✓ Successfully scraped {tokens_count} tokens and {protocols_count} protocols (Net Worth: {net_worth})",
            file=sys.stderr,
        )
        print(f"✓ Saved to: {output_path.resolve()}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error scraping DeBank: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
