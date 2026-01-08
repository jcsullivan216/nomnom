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
from .feeds import get_feed_manager, HealthStatus
from .onchain import OnChainAnalyzer, get_demo_onchain_indicators


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


@app.route("/onchain")
def onchain():
    """On-chain analysis page."""
    analyzer = OnChainAnalyzer()

    # Get demo indicators
    indicators = get_demo_onchain_indicators()

    # Get signals for demo markets
    all_signals = []
    demo_market_ids = ["fed-rate-cut", "nvda-200", "tiktok-ban", "btc-150k"]
    for market_id in demo_market_ids:
        signals = analyzer.get_market_onchain_signals(market_id)
        all_signals.extend(signals)

    # Sort by strength
    all_signals.sort(key=lambda s: s.strength, reverse=True)

    # Get notable wallets
    wallets = analyzer.get_top_wallets_for_market("demo", limit=10)
    # Sort by risk level
    risk_order = {"very_high": 0, "high": 1, "medium": 2, "low": 3}
    wallets.sort(key=lambda w: risk_order.get(w.risk_level.value, 4))

    return render_template(
        "onchain.html",
        indicators=indicators,
        signals=all_signals[:10],
        wallets=wallets
    )


@app.route("/feeds")
def feeds():
    """Data feeds monitoring page."""
    manager = get_feed_manager()
    categories = manager.get_feeds_by_category()
    summary = manager.get_feed_summary()

    # Get last check time from any feed
    last_check = None
    for feed in manager.feeds.values():
        if feed.last_check:
            if last_check is None or feed.last_check > last_check:
                last_check = feed.last_check

    return render_template(
        "feeds.html",
        categories=categories,
        summary=summary,
        last_check=last_check.strftime("%Y-%m-%d %H:%M:%S") if last_check else None
    )


@app.route("/api/feeds")
def api_feeds():
    """API endpoint for data feeds status."""
    manager = get_feed_manager()
    feeds_data = []

    for feed in manager.feeds.values():
        feeds_data.append({
            "id": feed.id,
            "name": feed.name,
            "category": feed.category,
            "status": feed.status.value,
            "response_time_ms": feed.response_time_ms,
            "last_check": feed.last_check.isoformat() if feed.last_check else None,
            "error_message": feed.error_message,
            "requires_auth": feed.requires_auth,
            "is_free": feed.is_free,
        })

    return jsonify({
        "feeds": feeds_data,
        "summary": manager.get_feed_summary()
    })


@app.route("/api/feeds/check")
def api_feeds_check():
    """Trigger health check for all feeds."""
    manager = get_feed_manager()
    manager.check_all_feeds()
    return jsonify({
        "status": "ok",
        "summary": manager.get_feed_summary(),
        "checked_at": datetime.now().isoformat()
    })


@app.route("/api/feeds/<feed_id>/check")
def api_feed_check(feed_id: str):
    """Check health of a specific feed."""
    manager = get_feed_manager()
    try:
        feed = manager.check_feed_health(feed_id)
        return jsonify({
            "id": feed.id,
            "name": feed.name,
            "status": feed.status.value,
            "response_time_ms": feed.response_time_ms,
            "error_message": feed.error_message,
            "checked_at": datetime.now().isoformat()
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """Run the Flask development server."""
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server(debug=True)
