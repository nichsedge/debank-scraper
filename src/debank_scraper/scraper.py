import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

SCRAPING_JS = r"""
() => {
    const data = {
      timestamp: new Date().toISOString(),
      wallet: {},
      social: {},
      tokens: [],
      protocols: [],
      nfts: []
    };

    // 1. Overview & Social
    const netWorthEl = document.querySelector("div[class*='HeaderInfo_totalAssetInner'], div[class*='HeaderInfo_totalAsset']");
    const changeEl = document.querySelector("div[class*='HeaderInfo_changePercent'], [class*='HeaderInfo_isLoss'], [class*='HeaderInfo_isProfit']");

    data.wallet.total_net_worth = netWorthEl ? (netWorthEl.querySelector("[class*='Value']")?.innerText.trim() || netWorthEl.innerText.split('\n')[0].trim()) : null;
    data.wallet.change_24h = changeEl ? changeEl.innerText.trim() : null;

    const rankingEl = document.querySelector("a[href='/ranking'][class*='RankingTag_rankingTag']");
    data.social.ranking = rankingEl ? rankingEl.innerText.trim() : null;

    const infoItems = document.querySelectorAll("div[class*='HeaderInfo_infoItem']");
    infoItems.forEach(item => {
      const text = item.innerText.trim();
      if (text.includes('Followers')) data.social.followers = text.replace('Followers', '').trim();
      else if (text.includes('Following')) data.social.following = text.replace('Following', '').trim();
      else if (text.includes('TVF')) data.social.tvf = text.replace('TVF', '').trim();
    });

    // 2. Wallet Tokens
    const tokenRows = document.querySelectorAll("div[class*='TokenWallet_table'] .db-table-row");
    tokenRows.forEach(row => {
      const symbol = row.querySelector("[class*='TokenWallet_detailLink']")?.innerText.trim();
      const cells = Array.from(row.querySelectorAll(".db-table-cell"));

      const chainLogoImg = row.querySelector("img[class*='TokenWallet_tokenChainIcon']");
      let chain = null;
      if (chainLogoImg && chainLogoImg.src) {
        const urlParts = chainLogoImg.src.split('/');
        const logoUrlIndex = urlParts.indexOf('logo_url');
        if (logoUrlIndex !== -1 && logoUrlIndex + 1 < urlParts.length) {
          chain = urlParts[logoUrlIndex + 1];
        }
      }

      if (symbol && cells.length >= 4) {
        data.tokens.push({
          symbol,
          chain,
          price: cells[1]?.innerText.trim(),
          amount: cells[2]?.innerText.trim(),
          value: cells[3]?.innerText.trim()
        });
      }
    });

    // 3. Protocols
    const protocolContainers = document.querySelectorAll("div[class*='Project_project__']");
    protocolContainers.forEach(container => {
      const nameEl = container.querySelector("[class*='ProjectTitle_projectTitle'], [class*='ProjectTitle_name'], [class*='Project_projectName']");
      const valueEl = container.querySelector("[class*='projectTitle-number'], [class*='ProjectTitle_number'], [class*='Project_projectValue']");
      
      if (nameEl) {
        let name = nameEl.innerText.trim().split('\n')[0].replace(/\$.*/, '').trim();
        const value = valueEl ? valueEl.innerText.trim() : null;
        
        const protocolData = {
          name,
          value,
          positions: []
        };
        
        const categories = container.querySelectorAll("div[class*='Panel_container__']");
        categories.forEach(cat => {
          const typeEl = cat.querySelector("div[class*='Panel_panelHead__']");
          const type = typeEl ? typeEl.innerText.trim() : "Other";
          
          const headers = Array.from(cat.querySelectorAll("div[class*='table_header__'] > div")).map(h => h.innerText.trim().toLowerCase());
          const balanceIdx = headers.indexOf('balance');
          const rewardsIdx = headers.indexOf('rewards');
          const usdValueIdx = headers.lastIndexOf('usd value');

          const rows = cat.querySelectorAll("div[class*='table_contentRow__']");
          rows.forEach(row => {
            const cells = Array.from(row.children);
            if (cells.length >= 2) {
              const poolName = cells[0].innerText.trim().replace(/\n/g, ' ');
              const positionValue = usdValueIdx !== -1 && cells[usdValueIdx] ? cells[usdValueIdx].innerText.trim() : cells[cells.length - 1].innerText.trim();
              
              const getCleanedEntries = (cell) => {
                if (!cell) return [];
                const entries = [];
                const tokenLinks = cell.querySelectorAll("a[class*='utils_detailLink__'], a[class*='TokenWallet_detailLink__']");
                
                if (tokenLinks.length === 0) {
                   const text = cell.innerText.trim().replace(/\n/g, ' ');
                   if (text) entries.push({ symbol: null, balance: text });
                } else {
                  tokenLinks.forEach(link => {
                    const symbol = link.innerText.trim();
                    const cellClone = cell.cloneNode(true);
                    cellClone.querySelectorAll('button').forEach(btn => btn.remove());
                    let balanceText = cellClone.innerText.trim().replace(/\n/g, ' ');
                    balanceText = balanceText.replace(/\(\$.*?\)/g, '').trim();
                    entries.push({ symbol, balance: balanceText });
                  });
                }
                return entries;
              };

              const tokens = [];
              if (balanceIdx !== -1) tokens.push(...getCleanedEntries(cells[balanceIdx]));
              if (rewardsIdx !== -1) tokens.push(...getCleanedEntries(cells[rewardsIdx]));
              
              const uniqueTokens = [];
              const seen = new Set();
              tokens.forEach(t => {
                const key = `${t.symbol}|${t.balance}`;
                if (!seen.has(key)) {
                  uniqueTokens.push(t);
                  seen.add(key);
                }
              });

              protocolData.positions.push({
                type,
                pool: poolName,
                value: positionValue,
                tokens: uniqueTokens
              });
            }
          });
        });
        
        if (name && name !== 'Wallet' && !data.protocols.find(p => p.name === name)) {
          data.protocols.push(protocolData);
        }
      }
    });

    // Fallback for summary-only items
    const summaryItems = document.querySelectorAll("[class*='ProjectCell_assetsItem'], [class*='ProjectCell_projectCell'], [class*='ProjectCell_assetsItemWrap']");
    summaryItems.forEach(item => {
      const nameEl = item.querySelector("[class*='ProjectCell_assetsItemNameText'], [class*='ProjectCell_name']");
      const valueEl = item.querySelector("[class*='ProjectCell_assetsItemWorth'], [class*='ProjectCell_value']");

      if (nameEl) {
        const name = nameEl.innerText.trim().split('\n')[0].replace(/\$.*/, '').trim();
        const value = valueEl ? valueEl.innerText.trim() : null;

        if (name && name !== 'Wallet' && !data.protocols.find(p => p.name === name)) {
          data.protocols.push({ name, value, positions: [] });
        }
      }
    });

    return data;
}
"""


async def _auto_scroll(page):
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 400;
                let timer = setInterval(() => {
                    let scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if (totalHeight >= scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }
    """)


class DeBankScraper:
    """
    Playwright-based scraper for DeBank profile pages.
    """

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout

    async def scrape(self, address: str) -> Dict[str, Any]:
        """
        Scrape complete portfolio breakdown for a given EVM wallet address.
        """
        clean_address = address.strip().lower()
        profile_url = f"https://debank.com/profile/{clean_address}"

        logger.info(f"Starting DeBank scrape for {clean_address}")
        async with async_playwright() as p:
            browser = None
            try:
                # Try system chrome channel first, fallback to bundled chromium
                browser = await p.chromium.launch(channel="chrome", headless=self.headless)
            except Exception:
                browser = await p.chromium.launch(headless=self.headless)

            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                logger.debug(f"Navigating to {profile_url}")
                await page.goto(profile_url, wait_until="load", timeout=self.timeout)

                # Wait for total assets element
                try:
                    await page.wait_for_selector(
                        "div[class*='HeaderInfo_totalAssetInner'], div[class*='HeaderInfo_totalAsset'], div[class*='HeaderInfo_totalAssetValue']",
                        timeout=self.timeout,
                    )
                except Exception as e:
                    logger.warning(f"Timed out waiting for total assets selector: {e}")

                # Click unfold chains button if present
                try:
                    unfold_btn = await page.query_selector("div[class*='AssetsOnChain_unfoldBtn']")
                    if unfold_btn:
                        await unfold_btn.click()
                        await page.wait_for_timeout(1000)
                except Exception:
                    pass

                # Scroll to trigger lazy loaded items
                await _auto_scroll(page)
                await page.wait_for_timeout(2000)

                data = await page.evaluate(SCRAPING_JS)
                data["wallet"]["address"] = clean_address
                return data

            finally:
                if browser:
                    await browser.close()

    async def scrape_to_file(self, address: str, output_path: str | Path) -> Dict[str, Any]:
        """
        Scrape portfolio data and save to JSON file.
        """
        data = await self.scrape(address)
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved DeBank portfolio to {path}")
        return data


async def scrape_debank(address: str, headless: bool = True) -> Dict[str, Any]:
    """Convenience helper function to scrape an EVM address."""
    scraper = DeBankScraper(headless=headless)
    return await scraper.scrape(address)
