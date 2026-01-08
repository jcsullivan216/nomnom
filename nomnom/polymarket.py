"""
Polymarket API client for fetching prediction market data.

Uses the CLOB (Central Limit Order Book) API at clob.polymarket.com
and the gamma-api for market metadata.
"""

import requests
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass


@dataclass
class Market:
    """Represents a Polymarket prediction market."""
    id: str
    question: str
    slug: str
    yes_price: float
    no_price: float
    volume_24h: float
    total_volume: float
    liquidity: float
    end_date: Optional[datetime]
    category: str
    url: str
    tokens: list

    @property
    def trade_url(self) -> str:
        """Direct link to trade this market on Polymarket."""
        return f"https://polymarket.com/event/{self.slug}"


@dataclass
class TraderStats:
    """Statistics for a trader/wallet on Polymarket."""
    address: str
    total_trades: int
    win_rate: float
    total_volume: float
    pnl: float
    markets_traded: int
    avg_position_size: float


class PolymarketClient:
    """Client for interacting with Polymarket APIs."""

    GAMMA_API_BASE = "https://gamma-api.polymarket.com"
    CLOB_API_BASE = "https://clob.polymarket.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "NomNom/0.1.0"
        })

    def get_markets(self, limit: int = 100, active: bool = True) -> list[Market]:
        """
        Fetch active prediction markets from Polymarket.

        Args:
            limit: Maximum number of markets to return
            active: If True, only return active (not resolved) markets

        Returns:
            List of Market objects
        """
        params = {
            "limit": limit,
            "active": str(active).lower(),
            "closed": "false",
            "order": "volume24hr",
            "ascending": "false"
        }

        try:
            resp = self.session.get(
                f"{self.GAMMA_API_BASE}/markets",
                params=params,
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()

            markets = []
            for item in data:
                try:
                    # Extract token prices
                    tokens = item.get("tokens", [])
                    yes_price = 0.5
                    no_price = 0.5

                    for token in tokens:
                        outcome = token.get("outcome", "").lower()
                        price = float(token.get("price", 0.5))
                        if outcome == "yes":
                            yes_price = price
                        elif outcome == "no":
                            no_price = price

                    # Parse end date
                    end_date = None
                    if item.get("endDate"):
                        try:
                            end_date = datetime.fromisoformat(
                                item["endDate"].replace("Z", "+00:00")
                            )
                        except (ValueError, TypeError):
                            pass

                    market = Market(
                        id=item.get("id", ""),
                        question=item.get("question", ""),
                        slug=item.get("slug", item.get("id", "")),
                        yes_price=yes_price,
                        no_price=no_price,
                        volume_24h=float(item.get("volume24hr", 0)),
                        total_volume=float(item.get("volume", 0)),
                        liquidity=float(item.get("liquidity", 0)),
                        end_date=end_date,
                        category=item.get("category", ""),
                        url=f"https://polymarket.com/event/{item.get('slug', item.get('id', ''))}",
                        tokens=tokens
                    )
                    markets.append(market)
                except (KeyError, TypeError, ValueError) as e:
                    continue

            return markets

        except requests.RequestException as e:
            print(f"Error fetching markets: {e}")
            return []

    def get_market_by_slug(self, slug: str) -> Optional[Market]:
        """Fetch a specific market by its slug."""
        try:
            resp = self.session.get(
                f"{self.GAMMA_API_BASE}/markets/{slug}",
                timeout=30
            )
            resp.raise_for_status()
            item = resp.json()

            tokens = item.get("tokens", [])
            yes_price = 0.5
            no_price = 0.5

            for token in tokens:
                outcome = token.get("outcome", "").lower()
                price = float(token.get("price", 0.5))
                if outcome == "yes":
                    yes_price = price
                elif outcome == "no":
                    no_price = price

            end_date = None
            if item.get("endDate"):
                try:
                    end_date = datetime.fromisoformat(
                        item["endDate"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

            return Market(
                id=item.get("id", ""),
                question=item.get("question", ""),
                slug=item.get("slug", slug),
                yes_price=yes_price,
                no_price=no_price,
                volume_24h=float(item.get("volume24hr", 0)),
                total_volume=float(item.get("volume", 0)),
                liquidity=float(item.get("liquidity", 0)),
                end_date=end_date,
                category=item.get("category", ""),
                url=f"https://polymarket.com/event/{item.get('slug', slug)}",
                tokens=tokens
            )

        except requests.RequestException:
            return None

    def get_market_activity(self, market_id: str) -> dict:
        """
        Get recent trading activity for a market.

        Returns metrics useful for detecting informed trading:
        - Recent volume spikes
        - Order imbalance (buy vs sell pressure)
        - Large trade counts
        """
        # Note: Full activity data requires on-chain analysis
        # This provides basic market metrics
        try:
            resp = self.session.get(
                f"{self.GAMMA_API_BASE}/markets/{market_id}",
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()

            return {
                "volume_24h": float(data.get("volume24hr", 0)),
                "total_volume": float(data.get("volume", 0)),
                "liquidity": float(data.get("liquidity", 0)),
                "spread": data.get("spread", 0),
                "last_trade_price": data.get("lastTradePrice"),
            }
        except requests.RequestException:
            return {}

    def get_orderbook(self, token_id: str) -> dict:
        """
        Fetch the order book for a specific token.

        Useful for analyzing:
        - Bid-ask spread (tighter spread = more informed activity)
        - Order clustering
        - Large resting orders
        """
        try:
            resp = self.session.get(
                f"{self.CLOB_API_BASE}/book",
                params={"token_id": token_id},
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException:
            return {"bids": [], "asks": []}

    def calculate_order_imbalance(self, orderbook: dict) -> float:
        """
        Calculate order flow imbalance from orderbook.

        Order imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)

        Positive values indicate buying pressure (potential informed buying)
        Negative values indicate selling pressure (potential informed selling)

        Based on research: order imbalance is the most robust predictor
        of informed trading.
        """
        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])

        bid_volume = sum(float(b.get("size", 0)) for b in bids)
        ask_volume = sum(float(a.get("size", 0)) for a in asks)

        total = bid_volume + ask_volume
        if total == 0:
            return 0.0

        return (bid_volume - ask_volume) / total
