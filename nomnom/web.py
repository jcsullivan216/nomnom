"""
NomNom Web UI - Flask-based front-end for informed money detection.

Provides a web interface for viewing trade recommendations,
market data, and congressional trading activity.
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime

from .recommendations import RecommendationEngine, TradeRecommendation
from .polymarket import PolymarketClient
from .congress import CongressTradingClient
from .demo_data import get_demo_markets, get_demo_congress_trades, get_demo_signals


app = Flask(__name__)


def get_recommendations_data(use_demo: bool = True, min_confidence: float = 0.3):
    """Get recommendations data for the UI."""
    recommendations = []

    if use_demo:
        demo_signals = get_demo_signals()
        for sig in demo_signals:
            if sig["confidence"] >= min_confidence:
                recommendations.append({
                    "market": sig["market"],
                    "position": sig["position"],
                    "confidence": sig["confidence"],
                    "confidence_pct": int(sig["confidence"] * 100),
                    "price": sig["price"],
                    "edge": sig["edge"],
                    "edge_pct": round(sig["edge"] * 100, 1),
                    "size_pct": round(sig["edge"] * 50, 1),
                    "signal_type": sig["signal_type"],
                    "signal_label": format_signal_type(sig["signal_type"]),
                    "evidence": sig["evidence"],
                    "trade_url": sig["url"],
                    "is_buy_yes": "YES" in sig["position"],
                })
    else:
        try:
            engine = RecommendationEngine()
            recs = engine.get_recommendations(min_confidence=min_confidence)
            for rec in recs:
                recommendations.append({
                    "market": rec.market_question,
                    "position": rec.position,
                    "confidence": rec.confidence,
                    "confidence_pct": int(rec.confidence * 100),
                    "price": rec.current_price,
                    "edge": rec.expected_edge,
                    "edge_pct": round(rec.expected_edge * 100, 1),
                    "size_pct": round(rec.suggested_size_pct, 1),
                    "signal_type": rec.signal_type,
                    "signal_label": format_signal_type(rec.signal_type),
                    "evidence": rec.evidence,
                    "trade_url": rec.trade_url,
                    "is_buy_yes": "YES" in rec.position,
                })
        except Exception:
            # Fallback to demo
            return get_recommendations_data(use_demo=True, min_confidence=min_confidence)

    return recommendations


def get_markets_data(use_demo: bool = True, limit: int = 20):
    """Get markets data for the UI."""
    if use_demo:
        markets = get_demo_markets()[:limit]
    else:
        try:
            client = PolymarketClient()
            markets = client.get_markets(limit=limit)
            if not markets:
                markets = get_demo_markets()[:limit]
        except Exception:
            markets = get_demo_markets()[:limit]

    return [
        {
            "question": m.question,
            "yes_price": m.yes_price,
            "no_price": m.no_price,
            "yes_pct": int(m.yes_price * 100),
            "no_pct": int(m.no_price * 100),
            "volume_24h": f"${m.volume_24h:,.0f}",
            "total_volume": f"${m.total_volume:,.0f}",
            "liquidity": f"${m.liquidity:,.0f}",
            "category": m.category or "General",
            "trade_url": m.trade_url,
            "end_date": m.end_date.strftime("%Y-%m-%d") if m.end_date else None,
        }
        for m in markets
    ]


def get_congress_data(use_demo: bool = True, days: int = 30):
    """Get congressional trading data for the UI."""
    if use_demo:
        trades = get_demo_congress_trades()
    else:
        try:
            client = CongressTradingClient()
            trades = client.get_recent_trades(days=days)
            if not trades:
                trades = get_demo_congress_trades()
        except Exception:
            trades = get_demo_congress_trades()

    return [
        {
            "politician": t.politician,
            "party": t.party,
            "chamber": t.chamber,
            "state": t.state,
            "ticker": t.ticker or "N/A",
            "company": t.company,
            "trade_type": t.trade_type,
            "is_buy": t.trade_type == "buy",
            "amount": f"${t.amount_midpoint:,.0f}",
            "amount_raw": t.amount_midpoint,
            "trade_date": t.trade_date.strftime("%Y-%m-%d"),
            "disclosure_delay": t.disclosure_delay_days,
            "is_unusual": t.amount_high >= 100000 or t.disclosure_delay_days <= 3,
        }
        for t in trades
    ]


def format_signal_type(signal_type: str) -> str:
    """Format signal type for display."""
    labels = {
        "order_imbalance": "Order Flow Imbalance",
        "volume_spike": "Volume Spike",
        "congress_correlation": "Congressional Correlation",
        "price_momentum": "Price Momentum",
        "timing_pattern": "Timing Pattern",
    }
    return labels.get(signal_type, signal_type.replace("_", " ").title())


@app.route("/")
def index():
    """Main dashboard page."""
    recommendations = get_recommendations_data()
    return render_template("index.html", recommendations=recommendations)


@app.route("/markets")
def markets():
    """Markets listing page."""
    markets_data = get_markets_data()
    return render_template("markets.html", markets=markets_data)


@app.route("/congress")
def congress():
    """Congressional trading page."""
    trades = get_congress_data()
    return render_template("congress.html", trades=trades)


@app.route("/api/recommendations")
def api_recommendations():
    """API endpoint for recommendations."""
    min_conf = request.args.get("min_confidence", 0.3, type=float)
    use_demo = request.args.get("demo", "true").lower() == "true"
    data = get_recommendations_data(use_demo=use_demo, min_confidence=min_conf)
    return jsonify({"recommendations": data, "count": len(data)})


@app.route("/api/markets")
def api_markets():
    """API endpoint for markets."""
    limit = request.args.get("limit", 20, type=int)
    use_demo = request.args.get("demo", "true").lower() == "true"
    data = get_markets_data(use_demo=use_demo, limit=limit)
    return jsonify({"markets": data, "count": len(data)})


@app.route("/api/congress")
def api_congress():
    """API endpoint for congressional trades."""
    days = request.args.get("days", 30, type=int)
    use_demo = request.args.get("demo", "true").lower() == "true"
    data = get_congress_data(use_demo=use_demo, days=days)
    return jsonify({"trades": data, "count": len(data)})


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Run the Flask development server."""
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server(debug=True)
