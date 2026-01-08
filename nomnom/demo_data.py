"""
Demo data for testing and demonstration when APIs are unavailable.

Provides realistic mock data based on actual Polymarket patterns.
"""

from datetime import datetime, timedelta
from .polymarket import Market
from .congress import CongressTrade


def get_demo_markets() -> list[Market]:
    """Return demo prediction markets."""
    now = datetime.now()

    return [
        Market(
            id="1",
            question="Will the Federal Reserve cut interest rates in Q1 2026?",
            slug="fed-rate-cut-q1-2026",
            yes_price=0.72,
            no_price=0.28,
            volume_24h=847000,
            total_volume=12500000,
            liquidity=1200000,
            end_date=now + timedelta(days=45),
            category="Economics",
            url="https://polymarket.com/event/fed-rate-cut-q1-2026",
            tokens=[{"outcome": "Yes", "token_id": "demo1", "price": 0.72}]
        ),
        Market(
            id="2",
            question="Will Bitcoin reach $150,000 by March 2026?",
            slug="bitcoin-150k-march-2026",
            yes_price=0.34,
            no_price=0.66,
            volume_24h=1250000,
            total_volume=28000000,
            liquidity=3500000,
            end_date=now + timedelta(days=60),
            category="Crypto",
            url="https://polymarket.com/event/bitcoin-150k-march-2026",
            tokens=[{"outcome": "Yes", "token_id": "demo2", "price": 0.34}]
        ),
        Market(
            id="3",
            question="Will NVIDIA stock close above $200 by end of January 2026?",
            slug="nvda-200-jan-2026",
            yes_price=0.58,
            no_price=0.42,
            volume_24h=523000,
            total_volume=8700000,
            liquidity=890000,
            end_date=now + timedelta(days=23),
            category="Stocks",
            url="https://polymarket.com/event/nvda-200-jan-2026",
            tokens=[{"outcome": "Yes", "token_id": "demo3", "price": 0.58}]
        ),
        Market(
            id="4",
            question="Will there be a new COVID variant of concern declared in 2026?",
            slug="covid-variant-2026",
            yes_price=0.23,
            no_price=0.77,
            volume_24h=156000,
            total_volume=4200000,
            liquidity=450000,
            end_date=now + timedelta(days=357),
            category="Science",
            url="https://polymarket.com/event/covid-variant-2026",
            tokens=[{"outcome": "Yes", "token_id": "demo4", "price": 0.23}]
        ),
        Market(
            id="5",
            question="Will TikTok be banned in the US by July 2026?",
            slug="tiktok-ban-july-2026",
            yes_price=0.41,
            no_price=0.59,
            volume_24h=892000,
            total_volume=15600000,
            liquidity=1800000,
            end_date=now + timedelta(days=180),
            category="Politics",
            url="https://polymarket.com/event/tiktok-ban-july-2026",
            tokens=[{"outcome": "Yes", "token_id": "demo5", "price": 0.41}]
        ),
        Market(
            id="6",
            question="Will Apple announce AR glasses at WWDC 2026?",
            slug="apple-ar-glasses-wwdc-2026",
            yes_price=0.67,
            no_price=0.33,
            volume_24h=234000,
            total_volume=5100000,
            liquidity=620000,
            end_date=now + timedelta(days=150),
            category="Tech",
            url="https://polymarket.com/event/apple-ar-glasses-wwdc-2026",
            tokens=[{"outcome": "Yes", "token_id": "demo6", "price": 0.67}]
        ),
        Market(
            id="7",
            question="Will SpaceX complete a successful Starship orbital flight in Q1 2026?",
            slug="starship-orbital-q1-2026",
            yes_price=0.81,
            no_price=0.19,
            volume_24h=445000,
            total_volume=9800000,
            liquidity=1100000,
            end_date=now + timedelta(days=82),
            category="Space",
            url="https://polymarket.com/event/starship-orbital-q1-2026",
            tokens=[{"outcome": "Yes", "token_id": "demo7", "price": 0.81}]
        ),
        Market(
            id="8",
            question="Will the SEC approve a Solana ETF in 2026?",
            slug="solana-etf-2026",
            yes_price=0.45,
            no_price=0.55,
            volume_24h=678000,
            total_volume=11200000,
            liquidity=1400000,
            end_date=now + timedelta(days=340),
            category="Crypto",
            url="https://polymarket.com/event/solana-etf-2026",
            tokens=[{"outcome": "Yes", "token_id": "demo8", "price": 0.45}]
        ),
        Market(
            id="9",
            question="Will unemployment rate exceed 5% by mid-2026?",
            slug="unemployment-5-pct-2026",
            yes_price=0.28,
            no_price=0.72,
            volume_24h=312000,
            total_volume=6700000,
            liquidity=780000,
            end_date=now + timedelta(days=180),
            category="Economics",
            url="https://polymarket.com/event/unemployment-5-pct-2026",
            tokens=[{"outcome": "Yes", "token_id": "demo9", "price": 0.28}]
        ),
        Market(
            id="10",
            question="Will GPT-5 be released by OpenAI in H1 2026?",
            slug="gpt-5-h1-2026",
            yes_price=0.53,
            no_price=0.47,
            volume_24h=567000,
            total_volume=13400000,
            liquidity=1650000,
            end_date=now + timedelta(days=175),
            category="AI",
            url="https://polymarket.com/event/gpt-5-h1-2026",
            tokens=[{"outcome": "Yes", "token_id": "demo10", "price": 0.53}]
        ),
    ]


def get_demo_congress_trades() -> list[CongressTrade]:
    """Return demo congressional trades."""
    now = datetime.now()

    return [
        CongressTrade(
            politician="Nancy Pelosi",
            party="D",
            chamber="House",
            state="CA",
            ticker="NVDA",
            company="NVIDIA Corporation",
            trade_type="buy",
            amount_low=500001,
            amount_high=1000000,
            trade_date=now - timedelta(days=5),
            disclosure_date=now - timedelta(days=2),
            committees=["Financial Services"],
            source_url="https://disclosures-clerk.house.gov/"
        ),
        CongressTrade(
            politician="Tommy Tuberville",
            party="R",
            chamber="Senate",
            state="AL",
            ticker="LMT",
            company="Lockheed Martin",
            trade_type="buy",
            amount_low=100001,
            amount_high=250000,
            trade_date=now - timedelta(days=8),
            disclosure_date=now - timedelta(days=3),
            committees=["Armed Services"],
            source_url="https://efdsearch.senate.gov/"
        ),
        CongressTrade(
            politician="Dan Crenshaw",
            party="R",
            chamber="House",
            state="TX",
            ticker="XOM",
            company="Exxon Mobil Corporation",
            trade_type="buy",
            amount_low=50001,
            amount_high=100000,
            trade_date=now - timedelta(days=12),
            disclosure_date=now - timedelta(days=7),
            committees=["Energy and Commerce"],
            source_url="https://disclosures-clerk.house.gov/"
        ),
        CongressTrade(
            politician="Mark Kelly",
            party="D",
            chamber="Senate",
            state="AZ",
            ticker="BA",
            company="Boeing Company",
            trade_type="sell",
            amount_low=250001,
            amount_high=500000,
            trade_date=now - timedelta(days=3),
            disclosure_date=now - timedelta(days=1),
            committees=["Armed Services", "Commerce"],
            source_url="https://efdsearch.senate.gov/"
        ),
        CongressTrade(
            politician="Josh Gottheimer",
            party="D",
            chamber="House",
            state="NJ",
            ticker="AAPL",
            company="Apple Inc.",
            trade_type="buy",
            amount_low=15001,
            amount_high=50000,
            trade_date=now - timedelta(days=15),
            disclosure_date=now - timedelta(days=10),
            committees=["Financial Services"],
            source_url="https://disclosures-clerk.house.gov/"
        ),
        CongressTrade(
            politician="Michael McCaul",
            party="R",
            chamber="House",
            state="TX",
            ticker="RTX",
            company="RTX Corporation",
            trade_type="buy",
            amount_low=100001,
            amount_high=250000,
            trade_date=now - timedelta(days=7),
            disclosure_date=now - timedelta(days=4),
            committees=["Foreign Affairs", "Homeland Security"],
            source_url="https://disclosures-clerk.house.gov/"
        ),
        CongressTrade(
            politician="Ro Khanna",
            party="D",
            chamber="House",
            state="CA",
            ticker="GOOGL",
            company="Alphabet Inc.",
            trade_type="sell",
            amount_low=50001,
            amount_high=100000,
            trade_date=now - timedelta(days=20),
            disclosure_date=now - timedelta(days=15),
            committees=["Armed Services", "Oversight"],
            source_url="https://disclosures-clerk.house.gov/"
        ),
        CongressTrade(
            politician="Marsha Blackburn",
            party="R",
            chamber="Senate",
            state="TN",
            ticker="META",
            company="Meta Platforms Inc.",
            trade_type="buy",
            amount_low=15001,
            amount_high=50000,
            trade_date=now - timedelta(days=10),
            disclosure_date=now - timedelta(days=6),
            committees=["Commerce", "Judiciary"],
            source_url="https://efdsearch.senate.gov/"
        ),
    ]


def get_demo_signals():
    """
    Return pre-computed demo signals for demonstration.

    These simulate detected informed money patterns.
    """
    return [
        {
            "market": "Will the Federal Reserve cut interest rates in Q1 2026?",
            "signal_type": "order_imbalance",
            "confidence": 0.78,
            "position": "BUY YES",
            "price": 0.72,
            "edge": 0.08,
            "evidence": [
                "Strong buy pressure: 42% order imbalance",
                "Volume spike: 3.2x normal ($847K in 24h)",
                "Congressional trade: Tommy Tuberville (R) buy $175K in financial sector"
            ],
            "url": "https://polymarket.com/event/fed-rate-cut-q1-2026"
        },
        {
            "market": "Will NVIDIA stock close above $200 by end of January 2026?",
            "signal_type": "congress_correlation",
            "confidence": 0.71,
            "position": "BUY YES",
            "price": 0.58,
            "edge": 0.07,
            "evidence": [
                "Congressional trade: Nancy Pelosi (D) buy $750K in NVDA",
                "Quick disclosure: 3 days (unusual urgency)",
                "Volume spike: 2.4x normal"
            ],
            "url": "https://polymarket.com/event/nvda-200-jan-2026"
        },
        {
            "market": "Will TikTok be banned in the US by July 2026?",
            "signal_type": "volume_spike",
            "confidence": 0.65,
            "position": "BUY YES",
            "price": 0.41,
            "edge": 0.06,
            "evidence": [
                "Volume spike: 4.1x normal ($892K in 24h)",
                "Multiple congressional trades in tech sector",
                "High conviction with price momentum"
            ],
            "url": "https://polymarket.com/event/tiktok-ban-july-2026"
        },
        {
            "market": "Will the SEC approve a Solana ETF in 2026?",
            "signal_type": "order_imbalance",
            "confidence": 0.62,
            "position": "BUY NO",
            "price": 0.55,
            "edge": 0.05,
            "evidence": [
                "Strong sell pressure: -35% order imbalance",
                "Regulatory signal pattern detected",
                "Similar to pre-rejection ETF patterns"
            ],
            "url": "https://polymarket.com/event/solana-etf-2026"
        },
        {
            "market": "Will SpaceX complete a successful Starship orbital flight in Q1 2026?",
            "signal_type": "price_momentum",
            "confidence": 0.58,
            "position": "BUY YES",
            "price": 0.81,
            "edge": 0.04,
            "evidence": [
                "High conviction: 81% YES with $445K volume",
                "Near resolution: 82 days remaining",
                "Consistent accumulation pattern"
            ],
            "url": "https://polymarket.com/event/starship-orbital-q1-2026"
        },
    ]
