"""
On-Chain Analysis Module - Wallet behavior analysis for Polymarket.

Analyzes on-chain data to detect informed trading patterns:
- Wallet age vs bet timing (fresh wallets with high accuracy)
- Historical win rates (>70% across 20+ predictions is suspicious)
- Position building patterns (accumulation vs aggressive)
- Wallet clustering (coordinated multi-wallet activity)
- Order flow imbalance
"""

import requests
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class WalletRiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class WalletMetrics:
    """Metrics for a wallet's trading behavior."""
    address: str
    wallet_age_days: int
    total_trades: int
    win_rate: float  # 0-1
    total_volume_usd: float
    avg_position_size: float
    markets_traded: int
    profitable_markets: int
    largest_win: float
    largest_loss: float
    risk_level: WalletRiskLevel
    risk_factors: list[str]
    first_trade_date: Optional[datetime]
    last_trade_date: Optional[datetime]


@dataclass
class OnChainSignal:
    """Represents an on-chain signal for a market."""
    market_id: str
    signal_type: str
    description: str
    strength: float  # 0-1
    wallets_involved: int
    total_volume: float
    detected_at: datetime
    details: dict


class OnChainAnalyzer:
    """
    Analyzes on-chain data from Polymarket for informed trading signals.

    Key indicators from the README:
    1. Wallet age correlated with bet timing
    2. Success rate anomalies (>70% across 20+ predictions)
    3. Coordinated multi-wallet activity
    4. Position building patterns
    5. Order flow imbalance
    """

    # Polymarket contracts on Polygon
    CTF_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
    POLYGON_RPC = "https://polygon-rpc.com"

    # Thresholds for suspicious activity
    SUSPICIOUS_WIN_RATE = 0.70  # 70%+
    MIN_TRADES_FOR_ANALYSIS = 20
    FRESH_WALLET_DAYS = 7
    LARGE_POSITION_USD = 10000

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "NomNom/0.1.0",
            "Accept": "application/json"
        })

    def get_wallet_metrics(self, address: str) -> Optional[WalletMetrics]:
        """
        Get trading metrics for a wallet address.

        Note: Full implementation requires indexer access (The Graph, Dune, etc.)
        This provides the structure and demo data.
        """
        # In production, this would query:
        # - The Graph Polymarket subgraph
        # - Dune Analytics
        # - Direct RPC calls to Polygon

        # For demo purposes, return sample metrics
        return self._get_demo_wallet_metrics(address)

    def _get_demo_wallet_metrics(self, address: str) -> WalletMetrics:
        """Generate demo wallet metrics."""
        import hashlib

        # Use address hash to generate consistent pseudo-random metrics
        hash_val = int(hashlib.md5(address.encode()).hexdigest()[:8], 16)

        wallet_age = (hash_val % 365) + 1
        total_trades = (hash_val % 100) + 5
        win_rate = 0.4 + (hash_val % 40) / 100  # 40-80%
        total_volume = (hash_val % 500000) + 1000

        risk_factors = []
        risk_level = WalletRiskLevel.LOW

        # Check risk factors
        if wallet_age < self.FRESH_WALLET_DAYS:
            risk_factors.append(f"Fresh wallet ({wallet_age} days old)")
            risk_level = WalletRiskLevel.MEDIUM

        if win_rate > self.SUSPICIOUS_WIN_RATE and total_trades >= self.MIN_TRADES_FOR_ANALYSIS:
            risk_factors.append(f"High win rate ({win_rate:.0%} over {total_trades} trades)")
            risk_level = WalletRiskLevel.HIGH

        if total_volume > 100000 and wallet_age < 30:
            risk_factors.append(f"Large volume (${total_volume:,.0f}) from new wallet")
            risk_level = WalletRiskLevel.VERY_HIGH

        return WalletMetrics(
            address=address,
            wallet_age_days=wallet_age,
            total_trades=total_trades,
            win_rate=win_rate,
            total_volume_usd=total_volume,
            avg_position_size=total_volume / total_trades if total_trades > 0 else 0,
            markets_traded=(hash_val % 20) + 1,
            profitable_markets=int((hash_val % 20) * win_rate),
            largest_win=(hash_val % 50000) + 100,
            largest_loss=(hash_val % 10000) + 100,
            risk_level=risk_level,
            risk_factors=risk_factors,
            first_trade_date=datetime.now() - timedelta(days=wallet_age),
            last_trade_date=datetime.now() - timedelta(days=(hash_val % 7))
        )

    def get_market_onchain_signals(self, market_id: str) -> list[OnChainSignal]:
        """
        Get on-chain signals for a specific market.

        Analyzes:
        - Recent large trades
        - New wallet activity
        - Coordinated buying/selling
        - Order flow patterns
        """
        # In production, this would query on-chain data
        # For demo, return sample signals
        return self._get_demo_market_signals(market_id)

    def _get_demo_market_signals(self, market_id: str) -> list[OnChainSignal]:
        """Generate demo on-chain signals for a market."""
        import hashlib

        hash_val = int(hashlib.md5(market_id.encode()).hexdigest()[:8], 16)
        signals = []

        # Fresh wallet activity
        if hash_val % 3 == 0:
            signals.append(OnChainSignal(
                market_id=market_id,
                signal_type="fresh_wallet_activity",
                description="Multiple new wallets (<7 days) placing large bets",
                strength=0.7 + (hash_val % 20) / 100,
                wallets_involved=(hash_val % 5) + 2,
                total_volume=(hash_val % 100000) + 10000,
                detected_at=datetime.now() - timedelta(hours=hash_val % 24),
                details={
                    "avg_wallet_age_days": (hash_val % 5) + 1,
                    "avg_bet_size": (hash_val % 10000) + 1000,
                    "direction": "YES" if hash_val % 2 == 0 else "NO"
                }
            ))

        # High win-rate wallet activity
        if hash_val % 4 == 0:
            signals.append(OnChainSignal(
                market_id=market_id,
                signal_type="smart_money_accumulation",
                description="Wallets with >70% win rate accumulating positions",
                strength=0.65 + (hash_val % 25) / 100,
                wallets_involved=(hash_val % 3) + 1,
                total_volume=(hash_val % 50000) + 5000,
                detected_at=datetime.now() - timedelta(hours=hash_val % 48),
                details={
                    "avg_win_rate": 0.72 + (hash_val % 15) / 100,
                    "avg_trades": (hash_val % 50) + 20,
                    "direction": "YES" if hash_val % 2 == 0 else "NO"
                }
            ))

        # Coordinated activity
        if hash_val % 5 == 0:
            signals.append(OnChainSignal(
                market_id=market_id,
                signal_type="coordinated_activity",
                description="Multiple wallets trading in sync (possible single actor)",
                strength=0.6 + (hash_val % 30) / 100,
                wallets_involved=(hash_val % 8) + 3,
                total_volume=(hash_val % 200000) + 20000,
                detected_at=datetime.now() - timedelta(hours=hash_val % 12),
                details={
                    "time_correlation": 0.85 + (hash_val % 10) / 100,
                    "funding_pattern": "diffusion" if hash_val % 2 == 0 else "consolidation",
                    "direction": "YES" if hash_val % 2 == 0 else "NO"
                }
            ))

        # Large order imbalance
        if hash_val % 2 == 0:
            imbalance = (hash_val % 40 + 20) / 100  # 20-60%
            signals.append(OnChainSignal(
                market_id=market_id,
                signal_type="order_imbalance",
                description=f"Significant order flow imbalance ({imbalance:.0%})",
                strength=imbalance,
                wallets_involved=(hash_val % 20) + 5,
                total_volume=(hash_val % 300000) + 30000,
                detected_at=datetime.now() - timedelta(hours=hash_val % 6),
                details={
                    "buy_volume": (hash_val % 200000) + 20000,
                    "sell_volume": (hash_val % 100000) + 10000,
                    "imbalance_pct": imbalance,
                    "dominant_side": "BUY" if hash_val % 2 == 0 else "SELL"
                }
            ))

        return signals

    def get_top_wallets_for_market(self, market_id: str, limit: int = 10) -> list[WalletMetrics]:
        """Get top wallets by volume for a market."""
        # Demo implementation
        demo_addresses = [
            f"0x{''.join([hex(i)[2:] for i in range(j, j+20)])[:40]}"
            for j in range(limit)
        ]
        return [self.get_wallet_metrics(addr) for addr in demo_addresses]

    def calculate_smart_money_score(self, market_id: str) -> dict:
        """
        Calculate an overall "smart money" score for a market.

        Combines multiple on-chain signals into a single score.
        """
        signals = self.get_market_onchain_signals(market_id)

        if not signals:
            return {
                "score": 0,
                "direction": "NEUTRAL",
                "confidence": 0,
                "signals_count": 0,
                "details": "No significant on-chain signals detected"
            }

        # Calculate weighted score
        total_weight = 0
        weighted_strength = 0
        direction_votes = {"YES": 0, "NO": 0}

        signal_weights = {
            "fresh_wallet_activity": 1.5,
            "smart_money_accumulation": 2.0,
            "coordinated_activity": 1.8,
            "order_imbalance": 1.2,
        }

        for signal in signals:
            weight = signal_weights.get(signal.signal_type, 1.0)
            weighted_strength += signal.strength * weight
            total_weight += weight

            direction = signal.details.get("direction") or signal.details.get("dominant_side")
            if direction in ["YES", "BUY"]:
                direction_votes["YES"] += weight
            elif direction in ["NO", "SELL"]:
                direction_votes["NO"] += weight

        score = weighted_strength / total_weight if total_weight > 0 else 0

        if direction_votes["YES"] > direction_votes["NO"]:
            direction = "YES"
            confidence = direction_votes["YES"] / (direction_votes["YES"] + direction_votes["NO"])
        elif direction_votes["NO"] > direction_votes["YES"]:
            direction = "NO"
            confidence = direction_votes["NO"] / (direction_votes["YES"] + direction_votes["NO"])
        else:
            direction = "NEUTRAL"
            confidence = 0.5

        return {
            "score": round(score, 2),
            "direction": direction,
            "confidence": round(confidence, 2),
            "signals_count": len(signals),
            "details": f"{len(signals)} on-chain signals detected"
        }


# Demo data for the web UI
def get_demo_onchain_indicators() -> list[dict]:
    """Get demo on-chain indicators for display."""
    return [
        {
            "name": "Fresh Wallet Activity",
            "description": "New wallets (<7 days) placing large, accurate bets",
            "current_value": "12 wallets",
            "change": "+5 (24h)",
            "status": "warning",
            "details": "Avg wallet age: 3.2 days, Avg bet: $8,500"
        },
        {
            "name": "High Win-Rate Wallets",
            "description": "Wallets with >70% accuracy across 20+ trades",
            "current_value": "847 wallets",
            "change": "+23 (24h)",
            "status": "info",
            "details": "Top wallet: 78% win rate, 156 trades"
        },
        {
            "name": "Coordinated Activity",
            "description": "Wallet clusters trading in sync",
            "current_value": "3 clusters",
            "change": "0 (24h)",
            "status": "neutral",
            "details": "Largest cluster: 8 wallets, $450K volume"
        },
        {
            "name": "Order Imbalance",
            "description": "Net buy/sell pressure across markets",
            "current_value": "+$2.3M",
            "change": "Buy pressure",
            "status": "bullish",
            "details": "68% of volume is buying"
        },
        {
            "name": "Whale Movements",
            "description": "Large positions (>$50K) opened/closed",
            "current_value": "7 positions",
            "change": "+3 (24h)",
            "status": "warning",
            "details": "Net direction: YES ($890K)"
        },
        {
            "name": "Smart Money Flow",
            "description": "Volume from historically accurate wallets",
            "current_value": "$4.7M",
            "change": "+12% (24h)",
            "status": "bullish",
            "details": "Flowing into: Fed, NVDA, TikTok markets"
        }
    ]
