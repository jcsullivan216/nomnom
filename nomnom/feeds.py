"""
Data Feeds Module - Tracks all data sources and their health status.

Monitors connectivity and data flow from:
- Prediction Markets: Polymarket, Kalshi
- On-chain Data: The Graph, Dune Analytics, Bitquery
- Congressional Trading: House/Senate Stock Watcher, Quiver Quant
- Regulatory: SEC EDGAR, Federal Register, CFTC
- OSINT: ADS-B Exchange, CourtListener, Coresignal
- Market Data: Options flow, CDS spreads
"""

import requests
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import time


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"
    NOT_CONFIGURED = "not_configured"


@dataclass
class DataFeed:
    """Represents a data source with health monitoring."""
    id: str
    name: str
    category: str
    description: str
    url: str
    api_endpoint: Optional[str] = None
    requires_auth: bool = False
    auth_type: Optional[str] = None  # "api_key", "oauth", "none"
    status: HealthStatus = HealthStatus.UNKNOWN
    last_check: Optional[datetime] = None
    last_success: Optional[datetime] = None
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    sample_data: Optional[dict] = None
    data_points_24h: int = 0
    is_free: bool = True
    rate_limit: Optional[str] = None


class DataFeedManager:
    """Manages all data feeds and their health checks."""

    def __init__(self):
        self.feeds = self._initialize_feeds()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "NomNom/0.1.0",
            "Accept": "application/json"
        })

    def _initialize_feeds(self) -> dict[str, DataFeed]:
        """Initialize all data feeds from the README sources."""
        feeds = {}

        # ============ PREDICTION MARKETS ============
        feeds["polymarket_gamma"] = DataFeed(
            id="polymarket_gamma",
            name="Polymarket Gamma API",
            category="Prediction Markets",
            description="Market data, prices, volumes for all Polymarket events",
            url="https://gamma-api.polymarket.com",
            api_endpoint="https://gamma-api.polymarket.com/markets?limit=1",
            requires_auth=False,
            is_free=True,
            rate_limit="100 req/min"
        )

        feeds["polymarket_clob"] = DataFeed(
            id="polymarket_clob",
            name="Polymarket CLOB API",
            category="Prediction Markets",
            description="Order book data, trades, real-time prices",
            url="https://clob.polymarket.com",
            api_endpoint="https://clob.polymarket.com/markets",
            requires_auth=False,
            is_free=True,
            rate_limit="100 req/min"
        )

        feeds["kalshi"] = DataFeed(
            id="kalshi",
            name="Kalshi API",
            category="Prediction Markets",
            description="US-regulated prediction market data",
            url="https://api.kalshi.com",
            api_endpoint="https://api.kalshi.com/trade-api/v2/markets",
            requires_auth=False,
            is_free=True,
            rate_limit="10 req/sec"
        )

        # ============ ON-CHAIN DATA ============
        feeds["polygon_rpc"] = DataFeed(
            id="polygon_rpc",
            name="Polygon RPC",
            category="On-Chain Data",
            description="Direct blockchain queries for Polymarket contracts on Polygon",
            url="https://polygon-rpc.com",
            api_endpoint="https://polygon-rpc.com",
            requires_auth=False,
            is_free=True,
            rate_limit="Limited"
        )

        feeds["the_graph"] = DataFeed(
            id="the_graph",
            name="The Graph (Polymarket Subgraph)",
            category="On-Chain Data",
            description="Indexed Polymarket data: positions, P&L, order fills",
            url="https://thegraph.com/hosted-service/subgraph/polymarket/polymarket-matic",
            api_endpoint=None,  # Requires subgraph query
            requires_auth=False,
            is_free=True,
            rate_limit="1000 queries/day free"
        )

        feeds["dune_analytics"] = DataFeed(
            id="dune_analytics",
            name="Dune Analytics",
            category="On-Chain Data",
            description="SQL queries on blockchain data, Polymarket dashboards",
            url="https://dune.com",
            api_endpoint="https://api.dune.com/api/v1/query/1234/results",
            requires_auth=True,
            auth_type="api_key",
            is_free=False,
            rate_limit="Tier-based"
        )

        feeds["bitquery"] = DataFeed(
            id="bitquery",
            name="Bitquery GraphQL",
            category="On-Chain Data",
            description="Polymarket contract events via GraphQL",
            url="https://graphql.bitquery.io",
            api_endpoint="https://graphql.bitquery.io",
            requires_auth=True,
            auth_type="api_key",
            is_free=False,
            rate_limit="Tier-based"
        )

        # ============ CONGRESSIONAL TRADING ============
        feeds["house_stock_watcher"] = DataFeed(
            id="house_stock_watcher",
            name="House Stock Watcher",
            category="Congressional Trading",
            description="House of Representatives financial disclosures",
            url="https://housestockwatcher.com",
            api_endpoint="https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json",
            requires_auth=False,
            is_free=True,
            rate_limit="None"
        )

        feeds["senate_stock_watcher"] = DataFeed(
            id="senate_stock_watcher",
            name="Senate Stock Watcher",
            category="Congressional Trading",
            description="Senate financial disclosures",
            url="https://senatestockwatcher.com",
            api_endpoint="https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json",
            requires_auth=False,
            is_free=True,
            rate_limit="None"
        )

        feeds["quiver_quant"] = DataFeed(
            id="quiver_quant",
            name="Quiver Quantitative",
            category="Congressional Trading",
            description="Congressional trading aggregator with API",
            url="https://www.quiverquant.com",
            api_endpoint="https://api.quiverquant.com/beta/live/congresstrading",
            requires_auth=True,
            auth_type="api_key",
            is_free=False,
            rate_limit="Tier-based"
        )

        feeds["capitol_trades"] = DataFeed(
            id="capitol_trades",
            name="Capitol Trades",
            category="Congressional Trading",
            description="Congressional trading tracker",
            url="https://www.capitoltrades.com",
            api_endpoint=None,
            requires_auth=False,
            is_free=True,
            rate_limit="Web scraping"
        )

        # ============ REGULATORY DATA ============
        feeds["sec_edgar"] = DataFeed(
            id="sec_edgar",
            name="SEC EDGAR",
            category="Regulatory",
            description="8-K filings, Form 4 insider trades, 13D activist positions",
            url="https://www.sec.gov/cgi-bin/browse-edgar",
            api_endpoint="https://data.sec.gov/submissions/CIK0000320193.json",
            requires_auth=False,
            is_free=True,
            rate_limit="10 req/sec"
        )

        feeds["federal_register"] = DataFeed(
            id="federal_register",
            name="Federal Register API",
            category="Regulatory",
            description="Federal Register contents since 1994, rule announcements",
            url="https://www.federalregister.gov",
            api_endpoint="https://www.federalregister.gov/api/v1/documents.json?per_page=1",
            requires_auth=False,
            is_free=True,
            rate_limit="None"
        )

        feeds["lobbying_senate"] = DataFeed(
            id="lobbying_senate",
            name="Senate Lobbying Disclosures",
            category="Regulatory",
            description="LD-1, LD-2, LD-203 lobbying filings",
            url="https://lda.senate.gov",
            api_endpoint=None,  # REST API requires registration
            requires_auth=True,
            auth_type="registration",
            is_free=True,
            rate_limit="Unknown"
        )

        # ============ OSINT SOURCES ============
        feeds["adsb_exchange"] = DataFeed(
            id="adsb_exchange",
            name="ADS-B Exchange",
            category="OSINT",
            description="Flight tracking (doesn't honor FAA blocks) - corporate jets, gov aircraft",
            url="https://www.adsbexchange.com",
            api_endpoint="https://adsbexchange.com/api/aircraft/json/",
            requires_auth=True,
            auth_type="api_key",
            is_free=False,
            rate_limit="Tier-based"
        )

        feeds["court_listener"] = DataFeed(
            id="court_listener",
            name="CourtListener / RECAP",
            category="OSINT",
            description="Federal court filings, litigation monitoring",
            url="https://www.courtlistener.com",
            api_endpoint="https://www.courtlistener.com/api/rest/v3/dockets/?cursor=1",
            requires_auth=True,
            auth_type="api_key",
            is_free=True,  # Free tier available
            rate_limit="5 alerts/day free"
        )

        feeds["coresignal"] = DataFeed(
            id="coresignal",
            name="Coresignal Jobs API",
            category="OSINT",
            description="Job postings as leading indicators (231M+ records)",
            url="https://coresignal.com",
            api_endpoint=None,
            requires_auth=True,
            auth_type="api_key",
            is_free=False,
            rate_limit="Tier-based"
        )

        feeds["cert_transparency"] = DataFeed(
            id="cert_transparency",
            name="Certificate Transparency (crt.sh)",
            category="OSINT",
            description="SSL certificates reveal upcoming products/acquisitions",
            url="https://crt.sh",
            api_endpoint="https://crt.sh/?q=example.com&output=json",
            requires_auth=False,
            is_free=True,
            rate_limit="Unknown"
        )

        # ============ MARKET DATA ============
        feeds["unusual_whales"] = DataFeed(
            id="unusual_whales",
            name="Unusual Whales",
            category="Market Data",
            description="Options flow, unusual activity detection",
            url="https://unusualwhales.com",
            api_endpoint=None,
            requires_auth=True,
            auth_type="subscription",
            is_free=False,
            rate_limit="$50/month"
        )

        feeds["finra_shorts"] = DataFeed(
            id="finra_shorts",
            name="FINRA Short Interest",
            category="Market Data",
            description="Short interest data, bi-monthly updates",
            url="https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data",
            api_endpoint=None,
            requires_auth=False,
            is_free=True,
            rate_limit="Bi-monthly"
        )

        # ============ AGGREGATORS ============
        feeds["finfeed_api"] = DataFeed(
            id="finfeed_api",
            name="FinFeedAPI",
            category="Aggregators",
            description="Unified API for Polymarket, Kalshi, Myriad",
            url="https://finfeedapi.com",
            api_endpoint=None,
            requires_auth=True,
            auth_type="api_key",
            is_free=False,
            rate_limit="Tier-based"
        )

        feeds["eventarb"] = DataFeed(
            id="eventarb",
            name="EventArb",
            category="Aggregators",
            description="Cross-platform arbitrage calculator",
            url="https://eventarb.com",
            api_endpoint=None,
            requires_auth=False,
            is_free=True,
            rate_limit="Web only"
        )

        return feeds

    def check_feed_health(self, feed_id: str) -> DataFeed:
        """Check the health of a specific data feed."""
        if feed_id not in self.feeds:
            raise ValueError(f"Unknown feed: {feed_id}")

        feed = self.feeds[feed_id]
        feed.last_check = datetime.now()

        if not feed.api_endpoint:
            feed.status = HealthStatus.NOT_CONFIGURED
            feed.error_message = "No API endpoint configured"
            return feed

        if feed.requires_auth and feed.auth_type in ["api_key", "oauth"]:
            # Can't check without credentials
            feed.status = HealthStatus.NOT_CONFIGURED
            feed.error_message = f"Requires {feed.auth_type} authentication"
            return feed

        try:
            start_time = time.time()
            response = self.session.get(
                feed.api_endpoint,
                timeout=10,
                allow_redirects=True
            )
            elapsed_ms = int((time.time() - start_time) * 1000)
            feed.response_time_ms = elapsed_ms

            if response.status_code == 200:
                feed.status = HealthStatus.HEALTHY
                feed.last_success = datetime.now()
                feed.error_message = None

                # Try to get sample data
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        feed.sample_data = {"count": len(data), "sample": str(data[0])[:200]}
                        feed.data_points_24h = len(data)
                    elif isinstance(data, dict):
                        feed.sample_data = {"keys": list(data.keys())[:5]}
                        feed.data_points_24h = 1
                except:
                    feed.sample_data = {"raw_length": len(response.text)}

            elif response.status_code == 429:
                feed.status = HealthStatus.DEGRADED
                feed.error_message = "Rate limited"
            elif response.status_code in [401, 403]:
                feed.status = HealthStatus.NOT_CONFIGURED
                feed.error_message = "Authentication required"
            else:
                feed.status = HealthStatus.DOWN
                feed.error_message = f"HTTP {response.status_code}"

        except requests.Timeout:
            feed.status = HealthStatus.DOWN
            feed.error_message = "Timeout"
            feed.response_time_ms = 10000
        except requests.ConnectionError as e:
            feed.status = HealthStatus.DOWN
            feed.error_message = f"Connection failed"
        except Exception as e:
            feed.status = HealthStatus.DOWN
            feed.error_message = str(e)[:100]

        return feed

    def check_all_feeds(self) -> dict[str, DataFeed]:
        """Check health of all configured feeds."""
        for feed_id in self.feeds:
            self.check_feed_health(feed_id)
        return self.feeds

    def get_feeds_by_category(self) -> dict[str, list[DataFeed]]:
        """Group feeds by category."""
        categories = {}
        for feed in self.feeds.values():
            if feed.category not in categories:
                categories[feed.category] = []
            categories[feed.category].append(feed)
        return categories

    def get_feed_summary(self) -> dict:
        """Get summary statistics for all feeds."""
        total = len(self.feeds)
        healthy = sum(1 for f in self.feeds.values() if f.status == HealthStatus.HEALTHY)
        degraded = sum(1 for f in self.feeds.values() if f.status == HealthStatus.DEGRADED)
        down = sum(1 for f in self.feeds.values() if f.status == HealthStatus.DOWN)
        not_configured = sum(1 for f in self.feeds.values() if f.status == HealthStatus.NOT_CONFIGURED)
        unknown = sum(1 for f in self.feeds.values() if f.status == HealthStatus.UNKNOWN)

        return {
            "total": total,
            "healthy": healthy,
            "degraded": degraded,
            "down": down,
            "not_configured": not_configured,
            "unknown": unknown,
            "health_percentage": round((healthy / total) * 100, 1) if total > 0 else 0
        }


# Singleton instance
_feed_manager = None

def get_feed_manager() -> DataFeedManager:
    """Get the singleton DataFeedManager instance."""
    global _feed_manager
    if _feed_manager is None:
        _feed_manager = DataFeedManager()
    return _feed_manager
