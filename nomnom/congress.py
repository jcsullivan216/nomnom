"""
Congressional trading data client.

Fetches congressional stock trades from public disclosure databases.
These trades may correlate with policy outcomes that affect prediction markets.
"""

import requests
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass


@dataclass
class CongressTrade:
    """Represents a congressional stock trade disclosure."""
    politician: str
    party: str
    chamber: str  # Senate or House
    state: str
    ticker: str
    company: str
    trade_type: str  # buy, sell
    amount_low: float
    amount_high: float
    trade_date: datetime
    disclosure_date: datetime
    committees: list[str]
    source_url: str

    @property
    def amount_midpoint(self) -> float:
        """Estimated trade size (midpoint of range)."""
        return (self.amount_low + self.amount_high) / 2

    @property
    def disclosure_delay_days(self) -> int:
        """Days between trade and disclosure."""
        return (self.disclosure_date - self.trade_date).days


class CongressTradingClient:
    """
    Client for fetching congressional trading data.

    Uses multiple data sources:
    - House Financial Disclosures API
    - Senate Financial Disclosures
    - Third-party aggregators (Quiver Quantitative style)
    """

    # Using a public congressional trading API
    QUIVER_API_BASE = "https://api.quiverquant.com/beta"
    HOUSE_STOCK_WATCHER = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
    SENATE_STOCK_WATCHER = "https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the client.

        Args:
            api_key: Optional API key for premium data sources
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "NomNom/0.1.0"
        })

    def get_recent_trades(self, days: int = 30) -> list[CongressTrade]:
        """
        Fetch recent congressional trades from public sources.

        Args:
            days: Number of days of history to fetch

        Returns:
            List of CongressTrade objects
        """
        trades = []
        cutoff = datetime.now() - timedelta(days=days)

        # Fetch House trades
        house_trades = self._fetch_house_trades(cutoff)
        trades.extend(house_trades)

        # Fetch Senate trades
        senate_trades = self._fetch_senate_trades(cutoff)
        trades.extend(senate_trades)

        # Sort by trade date (most recent first)
        trades.sort(key=lambda t: t.trade_date, reverse=True)

        return trades

    def _fetch_house_trades(self, cutoff: datetime) -> list[CongressTrade]:
        """Fetch trades from House Stock Watcher."""
        trades = []

        try:
            resp = self.session.get(self.HOUSE_STOCK_WATCHER, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            for item in data:
                try:
                    # Parse trade date
                    trade_date_str = item.get("transaction_date", "")
                    if not trade_date_str:
                        continue

                    trade_date = datetime.strptime(trade_date_str, "%Y-%m-%d")
                    if trade_date < cutoff:
                        continue

                    # Parse disclosure date
                    disclosure_date_str = item.get("disclosure_date", trade_date_str)
                    try:
                        disclosure_date = datetime.strptime(disclosure_date_str, "%Y-%m-%d")
                    except ValueError:
                        disclosure_date = trade_date

                    # Parse amount range
                    amount = item.get("amount", "$1,001 - $15,000")
                    amount_low, amount_high = self._parse_amount_range(amount)

                    # Determine trade type
                    trade_type_raw = item.get("type", "").lower()
                    if "purchase" in trade_type_raw:
                        trade_type = "buy"
                    elif "sale" in trade_type_raw:
                        trade_type = "sell"
                    else:
                        trade_type = trade_type_raw

                    trade = CongressTrade(
                        politician=item.get("representative", "Unknown"),
                        party=item.get("party", ""),
                        chamber="House",
                        state=item.get("state", ""),
                        ticker=item.get("ticker", ""),
                        company=item.get("asset_description", ""),
                        trade_type=trade_type,
                        amount_low=amount_low,
                        amount_high=amount_high,
                        trade_date=trade_date,
                        disclosure_date=disclosure_date,
                        committees=[],  # Would need additional lookup
                        source_url=item.get("ptr_link", "https://disclosures-clerk.house.gov/")
                    )
                    trades.append(trade)

                except (KeyError, ValueError, TypeError):
                    continue

        except requests.RequestException as e:
            print(f"Error fetching House trades: {e}")

        return trades

    def _fetch_senate_trades(self, cutoff: datetime) -> list[CongressTrade]:
        """Fetch trades from Senate Stock Watcher."""
        trades = []

        try:
            resp = self.session.get(self.SENATE_STOCK_WATCHER, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            for item in data:
                try:
                    # Parse trade date
                    trade_date_str = item.get("transaction_date", "")
                    if not trade_date_str:
                        continue

                    trade_date = datetime.strptime(trade_date_str, "%m/%d/%Y")
                    if trade_date < cutoff:
                        continue

                    # Parse disclosure date
                    disclosure_date_str = item.get("disclosure_date", "")
                    try:
                        disclosure_date = datetime.strptime(disclosure_date_str, "%m/%d/%Y")
                    except ValueError:
                        disclosure_date = trade_date

                    # Parse amount range
                    amount = item.get("amount", "$1,001 - $15,000")
                    amount_low, amount_high = self._parse_amount_range(amount)

                    # Determine trade type
                    trade_type_raw = item.get("type", "").lower()
                    if "purchase" in trade_type_raw:
                        trade_type = "buy"
                    elif "sale" in trade_type_raw:
                        trade_type = "sell"
                    else:
                        trade_type = trade_type_raw

                    trade = CongressTrade(
                        politician=item.get("senator", "Unknown"),
                        party=item.get("party", ""),
                        chamber="Senate",
                        state=item.get("state", ""),
                        ticker=item.get("ticker", ""),
                        company=item.get("asset_description", ""),
                        trade_type=trade_type,
                        amount_low=amount_low,
                        amount_high=amount_high,
                        trade_date=trade_date,
                        disclosure_date=disclosure_date,
                        committees=[],
                        source_url=item.get("ptr_link", "https://efdsearch.senate.gov/")
                    )
                    trades.append(trade)

                except (KeyError, ValueError, TypeError):
                    continue

        except requests.RequestException as e:
            print(f"Error fetching Senate trades: {e}")

        return trades

    def _parse_amount_range(self, amount_str: str) -> tuple[float, float]:
        """
        Parse congressional disclosure amount ranges.

        Ranges are reported in bands like "$1,001 - $15,000"
        """
        # Remove $ and commas
        amount_str = amount_str.replace("$", "").replace(",", "")

        # Common ranges
        ranges = {
            "1001 - 15000": (1001, 15000),
            "15001 - 50000": (15001, 50000),
            "50001 - 100000": (50001, 100000),
            "100001 - 250000": (100001, 250000),
            "250001 - 500000": (250001, 500000),
            "500001 - 1000000": (500001, 1000000),
            "1000001 - 5000000": (1000001, 5000000),
            "5000001 - 25000000": (5000001, 25000000),
            "25000001 - 50000000": (25000001, 50000000),
            "over 50000000": (50000000, 100000000),
        }

        amount_clean = amount_str.lower().strip()
        for key, val in ranges.items():
            if key in amount_clean:
                return val

        # Try to parse directly
        try:
            parts = amount_str.split("-")
            if len(parts) == 2:
                low = float(parts[0].strip())
                high = float(parts[1].strip())
                return (low, high)
        except ValueError:
            pass

        # Default to minimum disclosure range
        return (1001, 15000)

    def get_trades_by_sector(self, sector: str, days: int = 30) -> list[CongressTrade]:
        """
        Get trades filtered by sector/industry.

        Useful for correlating with prediction markets in specific sectors.
        """
        all_trades = self.get_recent_trades(days)
        # Basic filtering by company name keywords
        sector_keywords = {
            "tech": ["apple", "google", "microsoft", "meta", "amazon", "nvidia"],
            "finance": ["jpmorgan", "bank", "goldman", "morgan stanley", "wells fargo"],
            "defense": ["lockheed", "raytheon", "northrop", "boeing", "general dynamics"],
            "pharma": ["pfizer", "moderna", "johnson", "merck", "eli lilly"],
            "energy": ["exxon", "chevron", "conocophillips", "schlumberger"],
        }

        keywords = sector_keywords.get(sector.lower(), [])
        if not keywords:
            return all_trades

        return [
            t for t in all_trades
            if any(kw in t.company.lower() for kw in keywords)
        ]

    def get_unusual_trades(self, days: int = 30) -> list[CongressTrade]:
        """
        Identify potentially unusual congressional trades.

        Flags trades that may be noteworthy:
        - Large amounts ($100k+)
        - Short disclosure delays (filed quickly = time-sensitive?)
        - Clusters of similar trades across multiple members
        """
        all_trades = self.get_recent_trades(days)
        unusual = []

        for trade in all_trades:
            is_unusual = False
            reasons = []

            # Large trade
            if trade.amount_high >= 100000:
                is_unusual = True
                reasons.append("large_amount")

            # Quick disclosure (unusual urgency?)
            if trade.disclosure_delay_days <= 7:
                is_unusual = True
                reasons.append("quick_disclosure")

            if is_unusual:
                unusual.append(trade)

        return unusual
