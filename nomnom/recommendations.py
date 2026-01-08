"""
Trade recommendation system.

Converts detected signals into actionable trade recommendations
with direct links to execute trades.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .signals import InsiderSignal, SignalDetector, calculate_kelly_fraction


@dataclass
class TradeRecommendation:
    """
    Actionable trade recommendation based on detected signals.
    """
    market_question: str
    position: str  # "BUY YES" or "BUY NO"
    confidence: float
    current_price: float
    expected_edge: float
    suggested_size_pct: float  # % of bankroll (Kelly-derived)
    signal_type: str
    evidence: list[str]
    trade_url: str
    polymarket_url: str
    expires: Optional[datetime]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "market": self.market_question,
            "position": self.position,
            "confidence": round(self.confidence, 2),
            "current_price": round(self.current_price, 2),
            "expected_edge": round(self.expected_edge, 3),
            "suggested_size_pct": round(self.suggested_size_pct, 3),
            "signal_type": self.signal_type,
            "evidence": self.evidence,
            "trade_url": self.trade_url,
            "polymarket_url": self.polymarket_url,
            "expires": self.expires.isoformat() if self.expires else None,
        }


class RecommendationEngine:
    """
    Generates trade recommendations from detected signals.

    Provides:
    - Position recommendations (YES/NO)
    - Confidence scores
    - Kelly-derived position sizing
    - Direct trade links
    """

    def __init__(self):
        self.detector = SignalDetector()

    def get_recommendations(
        self,
        min_confidence: float = 0.5,
        max_results: int = 10
    ) -> list[TradeRecommendation]:
        """
        Scan markets and generate trade recommendations.

        Args:
            min_confidence: Minimum confidence threshold (0-1)
            max_results: Maximum recommendations to return

        Returns:
            List of TradeRecommendation objects, sorted by confidence
        """
        # Scan for signals
        signals = self.detector.scan_markets(limit=100)

        # Convert to recommendations
        recommendations = []
        for signal in signals:
            if signal.confidence < min_confidence:
                continue

            if signal.recommended_position == "ABSTAIN":
                continue

            rec = self._signal_to_recommendation(signal)
            recommendations.append(rec)

            if len(recommendations) >= max_results:
                break

        return recommendations

    def _signal_to_recommendation(self, signal: InsiderSignal) -> TradeRecommendation:
        """Convert a signal to a trade recommendation."""
        market = signal.market

        # Determine position and price
        if signal.recommended_position == "YES":
            position = "BUY YES"
            current_price = market.yes_price
        else:
            position = "BUY NO"
            current_price = market.no_price

        # Calculate Kelly-derived position size
        if current_price > 0 and current_price < 1:
            odds = 1 / current_price
            suggested_size = calculate_kelly_fraction(signal.expected_edge, odds)
        else:
            suggested_size = 0.0

        return TradeRecommendation(
            market_question=market.question,
            position=position,
            confidence=signal.confidence,
            current_price=current_price,
            expected_edge=signal.expected_edge,
            suggested_size_pct=suggested_size * 100,  # Convert to percentage
            signal_type=signal.signal_type,
            evidence=signal.evidence,
            trade_url=market.trade_url,
            polymarket_url=market.url,
            expires=market.end_date
        )

    def format_recommendation(self, rec: TradeRecommendation) -> str:
        """Format a recommendation for display."""
        lines = [
            f"{'=' * 70}",
            f"TRADE RECOMMENDATION",
            f"{'=' * 70}",
            f"",
            f"Market: {rec.market_question}",
            f"",
            f"Position:     {rec.position}",
            f"Confidence:   {rec.confidence:.0%}",
            f"Current Price: ${rec.current_price:.2f}",
            f"Expected Edge: {rec.expected_edge:.1%}",
            f"Suggested Size: {rec.suggested_size_pct:.1f}% of bankroll",
            f"",
            f"Signal Type: {rec.signal_type}",
            f"",
            f"Evidence:",
        ]

        for evidence in rec.evidence:
            lines.append(f"  - {evidence}")

        lines.extend([
            f"",
            f"TRADE NOW: {rec.trade_url}",
            f"",
        ])

        if rec.expires:
            lines.append(f"Expires: {rec.expires.strftime('%Y-%m-%d %H:%M UTC')}")

        lines.append(f"{'=' * 70}")

        return "\n".join(lines)

    def format_summary(self, recommendations: list[TradeRecommendation]) -> str:
        """Format a summary of all recommendations."""
        if not recommendations:
            return "No trade recommendations found matching criteria."

        lines = [
            "=" * 70,
            "NOMNOM TRADE RECOMMENDATIONS",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            "",
            f"Found {len(recommendations)} opportunities with smart money signals:",
            "",
        ]

        for i, rec in enumerate(recommendations, 1):
            confidence_bar = "#" * int(rec.confidence * 10)
            lines.extend([
                f"{i}. {rec.position} @ ${rec.current_price:.2f}",
                f"   {rec.market_question[:60]}{'...' if len(rec.market_question) > 60 else ''}",
                f"   Confidence: [{confidence_bar:<10}] {rec.confidence:.0%}",
                f"   Edge: {rec.expected_edge:.1%} | Size: {rec.suggested_size_pct:.1f}%",
                f"   Signal: {rec.signal_type}",
                f"   TRADE: {rec.trade_url}",
                "",
            ])

        lines.extend([
            "-" * 70,
            "DISCLAIMER: This tool detects potential informed money patterns.",
            "All trading involves risk. Do your own research before trading.",
            "-" * 70,
        ])

        return "\n".join(lines)
