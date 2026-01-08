"""
Informed money signal detection engine.

Combines multiple weak signals through ensemble methods to detect
informed trading in prediction markets.

Based on research from the methodological framework:
- Order imbalance is the most robust predictor
- Multiple signals increase confidence (ensemble approach)
- False positive management through consensus requirements
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import math

from .polymarket import Market, PolymarketClient
from .congress import CongressTrade, CongressTradingClient


@dataclass
class InsiderSignal:
    """
    Represents a detected informed money signal.

    Combines evidence from multiple sources with a confidence score.
    """
    market: Market
    signal_type: str
    confidence: float  # 0.0 to 1.0
    description: str
    evidence: list[str]
    detected_at: datetime
    recommended_position: str  # "YES", "NO", or "ABSTAIN"
    expected_edge: float  # Estimated probability edge

    @property
    def trade_url(self) -> str:
        """Direct link to execute the trade."""
        return self.market.trade_url


class SignalDetector:
    """
    Detects informed money signals in prediction markets.

    Uses multiple signal sources:
    1. Market microstructure (volume, order imbalance, spreads)
    2. Congressional trading correlation
    3. Cross-platform divergence
    4. Timing patterns (regulatory calendar, announcement windows)
    """

    # Signal weights based on empirical robustness from research
    WEIGHTS = {
        "order_imbalance": 0.30,      # Most robust predictor
        "volume_spike": 0.20,          # Volume anomalies
        "congress_correlation": 0.25,  # Congressional trading
        "price_momentum": 0.15,        # Price movement patterns
        "timing_pattern": 0.10,        # Calendar-based signals
    }

    # Thresholds for signal detection
    VOLUME_SPIKE_THRESHOLD = 2.0      # 2x normal volume
    ORDER_IMBALANCE_THRESHOLD = 0.3   # 30% imbalance
    CONFIDENCE_THRESHOLD = 0.5        # Minimum for recommendation

    def __init__(self):
        self.poly_client = PolymarketClient()
        self.congress_client = CongressTradingClient()

    def scan_markets(self, limit: int = 50) -> list[InsiderSignal]:
        """
        Scan active markets for informed money signals.

        Args:
            limit: Maximum number of markets to scan

        Returns:
            List of detected signals, sorted by confidence
        """
        signals = []
        markets = self.poly_client.get_markets(limit=limit)

        # Get recent congressional trades for correlation
        congress_trades = self.congress_client.get_recent_trades(days=30)

        for market in markets:
            signal = self._analyze_market(market, congress_trades)
            if signal and signal.confidence >= self.CONFIDENCE_THRESHOLD:
                signals.append(signal)

        # Sort by confidence (highest first)
        signals.sort(key=lambda s: s.confidence, reverse=True)

        return signals

    def _analyze_market(
        self,
        market: Market,
        congress_trades: list[CongressTrade]
    ) -> Optional[InsiderSignal]:
        """
        Analyze a single market for informed money signals.

        Combines multiple signal types with weighted scoring.
        """
        evidence = []
        scores = {}

        # 1. Volume analysis
        volume_score, volume_evidence = self._analyze_volume(market)
        scores["volume_spike"] = volume_score
        evidence.extend(volume_evidence)

        # 2. Order imbalance analysis
        imbalance_score, imbalance_evidence, direction = self._analyze_order_imbalance(market)
        scores["order_imbalance"] = imbalance_score
        evidence.extend(imbalance_evidence)

        # 3. Congressional correlation
        congress_score, congress_evidence = self._analyze_congress_correlation(
            market, congress_trades
        )
        scores["congress_correlation"] = congress_score
        evidence.extend(congress_evidence)

        # 4. Price momentum
        momentum_score, momentum_evidence = self._analyze_price_momentum(market)
        scores["price_momentum"] = momentum_score
        evidence.extend(momentum_evidence)

        # 5. Timing patterns
        timing_score, timing_evidence = self._analyze_timing(market)
        scores["timing_pattern"] = timing_score
        evidence.extend(timing_evidence)

        # Calculate weighted confidence score
        confidence = sum(
            scores[key] * self.WEIGHTS[key]
            for key in scores
        )

        if confidence < 0.2:  # Too low to report
            return None

        # Determine recommended position based on signals
        if direction > 0:
            recommended = "YES"
            expected_edge = min(direction * 0.1, 0.15)  # Cap at 15% edge
        elif direction < 0:
            recommended = "NO"
            expected_edge = min(abs(direction) * 0.1, 0.15)
        else:
            recommended = "ABSTAIN"
            expected_edge = 0.0

        # Determine signal type
        max_signal = max(scores, key=scores.get)
        signal_descriptions = {
            "volume_spike": "Unusual volume activity detected",
            "order_imbalance": "Significant order flow imbalance",
            "congress_correlation": "Congressional trading correlation",
            "price_momentum": "Strong price momentum pattern",
            "timing_pattern": "Timing aligned with disclosure windows",
        }

        return InsiderSignal(
            market=market,
            signal_type=max_signal,
            confidence=min(confidence, 1.0),
            description=signal_descriptions.get(max_signal, "Multiple signals detected"),
            evidence=evidence,
            detected_at=datetime.now(),
            recommended_position=recommended,
            expected_edge=expected_edge
        )

    def _analyze_volume(self, market: Market) -> tuple[float, list[str]]:
        """
        Analyze volume patterns for anomalies.

        High 24h volume relative to total volume suggests unusual activity.
        """
        evidence = []
        score = 0.0

        if market.total_volume == 0:
            return (0.0, [])

        # Calculate volume ratio (24h vs expected daily average)
        # Assume market has been active ~30 days on average
        expected_daily = market.total_volume / 30
        if expected_daily > 0:
            volume_ratio = market.volume_24h / expected_daily

            if volume_ratio > self.VOLUME_SPIKE_THRESHOLD:
                score = min((volume_ratio - 1) / 5, 1.0)  # Scale to 0-1
                evidence.append(
                    f"Volume spike: {volume_ratio:.1f}x normal "
                    f"(${market.volume_24h:,.0f} in 24h)"
                )

        # High absolute volume is also a signal
        if market.volume_24h > 100000:
            score = max(score, 0.3)
            evidence.append(f"High absolute volume: ${market.volume_24h:,.0f}")

        return (score, evidence)

    def _analyze_order_imbalance(
        self,
        market: Market
    ) -> tuple[float, list[str], float]:
        """
        Analyze order book imbalance.

        Order imbalance is the most robust predictor of informed trading.
        """
        evidence = []
        score = 0.0
        direction = 0.0

        # Get orderbook for YES token
        for token in market.tokens:
            if token.get("outcome", "").lower() == "yes":
                token_id = token.get("token_id")
                if token_id:
                    orderbook = self.poly_client.get_orderbook(token_id)
                    imbalance = self.poly_client.calculate_order_imbalance(orderbook)

                    if abs(imbalance) > self.ORDER_IMBALANCE_THRESHOLD:
                        score = min(abs(imbalance) / 0.5, 1.0)  # Scale to 0-1
                        direction = imbalance

                        if imbalance > 0:
                            evidence.append(
                                f"Strong buy pressure: {imbalance:.1%} order imbalance"
                            )
                        else:
                            evidence.append(
                                f"Strong sell pressure: {abs(imbalance):.1%} order imbalance"
                            )
                break

        return (score, evidence, direction)

    def _analyze_congress_correlation(
        self,
        market: Market,
        congress_trades: list[CongressTrade]
    ) -> tuple[float, list[str]]:
        """
        Check for correlation with congressional trading activity.

        Committee members trading in sectors they regulate is a strong signal.
        """
        evidence = []
        score = 0.0

        # Extract keywords from market question
        question_lower = market.question.lower()

        # Political keywords that might correlate with congressional knowledge
        political_keywords = {
            "president": ["policy", "executive", "administration"],
            "congress": ["bill", "legislation", "law"],
            "fed": ["interest", "rate", "monetary"],
            "sec": ["securities", "regulation", "crypto"],
            "trade": ["tariff", "import", "export"],
            "defense": ["military", "pentagon", "war"],
            "healthcare": ["medicare", "medicaid", "drug"],
            "tech": ["antitrust", "regulation", "privacy"],
        }

        # Check for relevant congressional trades
        relevant_trades = []
        for trade in congress_trades:
            trade_relevant = False

            # Check if trade sector matches market topic
            for category, keywords in political_keywords.items():
                if any(kw in question_lower for kw in keywords):
                    # Check if congress member trades in related sectors
                    if any(kw in trade.company.lower() for kw in keywords):
                        trade_relevant = True
                        break

            # Large trades are more significant
            if trade_relevant and trade.amount_high >= 50000:
                relevant_trades.append(trade)

        if relevant_trades:
            # More relevant trades = higher confidence
            score = min(len(relevant_trades) * 0.2, 1.0)

            for trade in relevant_trades[:3]:  # Show top 3
                evidence.append(
                    f"Congressional trade: {trade.politician} ({trade.party}) "
                    f"{trade.trade_type} ${trade.amount_midpoint:,.0f} in {trade.ticker}"
                )

        return (score, evidence)

    def _analyze_price_momentum(self, market: Market) -> tuple[float, list[str]]:
        """
        Analyze price momentum patterns.

        Extreme prices (near 0 or 1) with high volume suggest conviction.
        """
        evidence = []
        score = 0.0

        # Check for strong conviction (prices near extremes)
        if market.yes_price > 0.85 or market.yes_price < 0.15:
            # High conviction market
            conviction = abs(market.yes_price - 0.5) * 2  # 0 to 1 scale
            if market.volume_24h > 10000:
                score = conviction * 0.5
                evidence.append(
                    f"High conviction: {market.yes_price:.0%} YES "
                    f"with ${market.volume_24h:,.0f} volume"
                )

        # Price at exactly 50% with high volume is also interesting
        # (suggests active disagreement/new information)
        if 0.45 <= market.yes_price <= 0.55 and market.volume_24h > 50000:
            score = max(score, 0.3)
            evidence.append(
                f"Active price discovery: {market.yes_price:.0%} with high volume"
            )

        return (score, evidence)

    def _analyze_timing(self, market: Market) -> tuple[float, list[str]]:
        """
        Analyze timing patterns relative to disclosure windows.

        Pre-announcement windows create predictable information advantages.
        """
        evidence = []
        score = 0.0

        if not market.end_date:
            return (0.0, [])

        now = datetime.now(market.end_date.tzinfo) if market.end_date.tzinfo else datetime.now()
        days_to_resolution = (market.end_date - now).days

        # Markets close to resolution with unusual activity are suspicious
        if 0 < days_to_resolution <= 7:
            score = 0.4
            evidence.append(
                f"Near resolution: {days_to_resolution} days remaining"
            )

            # Even more suspicious with high volume
            if market.volume_24h > 50000:
                score = 0.7
                evidence.append("High volume near resolution")

        return (score, evidence)


def calculate_kelly_fraction(edge: float, odds: float) -> float:
    """
    Calculate Kelly Criterion bet sizing.

    Kelly fraction = (p * odds - (1-p)) / odds

    Where p = true probability (our estimate with edge)

    Args:
        edge: Our estimated probability edge (e.g., 0.05 for 5%)
        odds: Decimal odds for the bet

    Returns:
        Optimal fraction of bankroll to bet (0 to 1)
    """
    if edge <= 0 or odds <= 1:
        return 0.0

    # Implied probability from market
    market_prob = 1 / odds

    # Our estimated true probability
    true_prob = market_prob + edge

    # Kelly formula
    kelly = (true_prob * odds - 1) / (odds - 1)

    # Half-Kelly is more conservative
    return max(0.0, min(kelly * 0.5, 0.25))  # Cap at 25%
