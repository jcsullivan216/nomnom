"""
NomNom CLI - Informed Money Signal Detection

Command-line interface for detecting informed money in prediction markets
and generating trade recommendations.
"""

import json
import click
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from .recommendations import RecommendationEngine, TradeRecommendation
from .polymarket import PolymarketClient
from .congress import CongressTradingClient
from .demo_data import get_demo_markets, get_demo_congress_trades, get_demo_signals


console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="nomnom")
def cli():
    """
    NomNom - Detect informed money signals in prediction markets.

    Scans prediction markets for signs of informed money and generates
    trade recommendations with direct links to execute trades.
    """
    pass


@cli.command()
@click.option(
    "--min-confidence", "-c",
    default=0.5,
    type=float,
    help="Minimum confidence threshold (0-1)"
)
@click.option(
    "--max-results", "-n",
    default=10,
    type=int,
    help="Maximum number of recommendations"
)
@click.option(
    "--json", "output_json",
    is_flag=True,
    help="Output as JSON"
)
@click.option(
    "--demo",
    is_flag=True,
    help="Use demo data (for testing without API access)"
)
def scan(min_confidence: float, max_results: int, output_json: bool, demo: bool):
    """
    Scan markets for informed money signals.

    Analyzes active prediction markets for patterns indicating informed trading:
    - Order flow imbalance
    - Volume anomalies
    - Congressional trading correlation
    - Price momentum
    - Timing patterns

    Generates trade recommendations with direct links.
    """
    recommendations = []

    if demo:
        # Use demo data
        console.print("[dim]Using demo data...[/]")
        demo_signals = get_demo_signals()
        for sig in demo_signals[:max_results]:
            if sig["confidence"] >= min_confidence:
                rec = TradeRecommendation(
                    market_question=sig["market"],
                    position=sig["position"],
                    confidence=sig["confidence"],
                    current_price=sig["price"],
                    expected_edge=sig["edge"],
                    suggested_size_pct=sig["edge"] * 50,  # Simple sizing
                    signal_type=sig["signal_type"],
                    evidence=sig["evidence"],
                    trade_url=sig["url"],
                    polymarket_url=sig["url"],
                    expires=None
                )
                recommendations.append(rec)
    else:
        # Try live data
        with console.status("[bold green]Scanning markets for informed money signals...[/]"):
            try:
                engine = RecommendationEngine()
                recommendations = engine.get_recommendations(
                    min_confidence=min_confidence,
                    max_results=max_results
                )
            except Exception as e:
                console.print(f"[yellow]API unavailable: {e}[/]")
                console.print("[dim]Falling back to demo data. Use --demo flag explicitly.[/]")
                demo_signals = get_demo_signals()
                for sig in demo_signals[:max_results]:
                    if sig["confidence"] >= min_confidence:
                        rec = TradeRecommendation(
                            market_question=sig["market"],
                            position=sig["position"],
                            confidence=sig["confidence"],
                            current_price=sig["price"],
                            expected_edge=sig["edge"],
                            suggested_size_pct=sig["edge"] * 50,
                            signal_type=sig["signal_type"],
                            evidence=sig["evidence"],
                            trade_url=sig["url"],
                            polymarket_url=sig["url"],
                            expires=None
                        )
                        recommendations.append(rec)

    if output_json:
        output = {
            "recommendations": [r.to_dict() for r in recommendations],
            "count": len(recommendations)
        }
        click.echo(json.dumps(output, indent=2))
        return

    if not recommendations:
        console.print(Panel(
            "[yellow]No significant signals detected.[/]\n\n"
            "Try lowering the confidence threshold with --min-confidence 0.3\n"
            "Or use --demo to see example output",
            title="NomNom Scan Results"
        ))
        return

    # Display header
    console.print()
    console.print(Panel.fit(
        "[bold cyan]NOMNOM SMART MONEY DETECTION[/]\n"
        f"[dim]Found {len(recommendations)} trade opportunities[/]",
        box=box.DOUBLE
    ))
    console.print()

    # Display each recommendation
    for i, rec in enumerate(recommendations, 1):
        display_recommendation(rec, i)

    # Display footer
    console.print()
    console.print(Panel(
        "[bold yellow]DISCLAIMER[/]\n"
        "This tool detects potential informed money patterns.\n"
        "All trading involves risk. Do your own research before trading.",
        box=box.ROUNDED
    ))


def display_recommendation(rec: TradeRecommendation, index: int):
    """Display a single recommendation with rich formatting."""
    # Confidence color
    if rec.confidence >= 0.7:
        conf_color = "green"
    elif rec.confidence >= 0.5:
        conf_color = "yellow"
    else:
        conf_color = "red"

    # Position color
    pos_color = "green" if "YES" in rec.position else "red"

    # Build the recommendation table
    table = Table(box=box.ROUNDED, show_header=False, expand=True)
    table.add_column("Field", style="dim")
    table.add_column("Value")

    table.add_row(
        "Position",
        Text(rec.position, style=f"bold {pos_color}")
    )
    table.add_row(
        "Confidence",
        Text(f"{rec.confidence:.0%}", style=f"bold {conf_color}")
    )
    table.add_row("Current Price", f"${rec.current_price:.2f}")
    table.add_row("Expected Edge", f"{rec.expected_edge:.1%}")
    table.add_row("Suggested Size", f"{rec.suggested_size_pct:.1f}% of bankroll")
    table.add_row("Signal Type", rec.signal_type)

    # Evidence
    evidence_text = "\n".join(f"  - {e}" for e in rec.evidence)
    table.add_row("Evidence", evidence_text)

    # Trade link - make it prominent
    table.add_row(
        "[bold cyan]TRADE NOW[/]",
        f"[bold blue]{rec.trade_url}[/]"
    )

    # Expiration
    if rec.expires:
        table.add_row("Expires", rec.expires.strftime("%Y-%m-%d %H:%M UTC"))

    # Market question as title
    title = f"#{index}: {rec.market_question[:70]}{'...' if len(rec.market_question) > 70 else ''}"

    console.print(Panel(table, title=title, title_align="left", box=box.DOUBLE_EDGE))
    console.print()


@cli.command()
@click.option(
    "--limit", "-n",
    default=20,
    type=int,
    help="Number of markets to display"
)
@click.option(
    "--demo",
    is_flag=True,
    help="Use demo data"
)
def markets(limit: int, demo: bool):
    """
    List active prediction markets.

    Shows current prices, volumes, and direct trade links.
    """
    if demo:
        market_list = get_demo_markets()[:limit]
    else:
        with console.status("[bold green]Fetching active markets...[/]"):
            client = PolymarketClient()
            market_list = client.get_markets(limit=limit)

        if not market_list:
            console.print("[yellow]No markets found. Try --demo for example data.[/]")
            market_list = get_demo_markets()[:limit]

    table = Table(title="Active Prediction Markets", box=box.ROUNDED)
    table.add_column("#", style="dim")
    table.add_column("Market", max_width=50)
    table.add_column("YES", justify="right")
    table.add_column("NO", justify="right")
    table.add_column("24h Vol", justify="right")
    table.add_column("Trade Link", overflow="fold")

    for i, market in enumerate(market_list, 1):
        table.add_row(
            str(i),
            market.question[:50] + ("..." if len(market.question) > 50 else ""),
            f"${market.yes_price:.2f}",
            f"${market.no_price:.2f}",
            f"${market.volume_24h:,.0f}",
            f"[blue]{market.trade_url}[/]"
        )

    console.print(table)


@cli.command()
@click.option(
    "--days", "-d",
    default=30,
    type=int,
    help="Days of history to fetch"
)
@click.option(
    "--chamber",
    type=click.Choice(["all", "house", "senate"]),
    default="all",
    help="Filter by chamber"
)
@click.option(
    "--demo",
    is_flag=True,
    help="Use demo data"
)
def congress(days: int, chamber: str, demo: bool):
    """
    View recent congressional trading activity.

    Shows trades by members of Congress that may correlate with policy outcomes.
    """
    if demo:
        trades = get_demo_congress_trades()
    else:
        with console.status("[bold green]Fetching congressional trades...[/]"):
            client = CongressTradingClient()
            trades = client.get_recent_trades(days=days)

        if not trades:
            console.print("[yellow]No trades found via API. Using demo data.[/]")
            trades = get_demo_congress_trades()

    if chamber != "all":
        trades = [t for t in trades if t.chamber.lower() == chamber]

    if not trades:
        console.print("[yellow]No trades found.[/]")
        return

    table = Table(title=f"Congressional Trades (Last {days} Days)", box=box.ROUNDED)
    table.add_column("Date", style="dim")
    table.add_column("Politician")
    table.add_column("Party")
    table.add_column("Ticker", style="cyan")
    table.add_column("Type")
    table.add_column("Amount", justify="right")
    table.add_column("Delay", justify="right")

    for trade in trades[:50]:  # Limit display
        type_style = "green" if trade.trade_type == "buy" else "red"
        table.add_row(
            trade.trade_date.strftime("%Y-%m-%d"),
            trade.politician[:20],
            trade.party,
            trade.ticker or "N/A",
            Text(trade.trade_type.upper(), style=type_style),
            f"${trade.amount_midpoint:,.0f}",
            f"{trade.disclosure_delay_days}d"
        )

    console.print(table)

    # Find unusual trades
    unusual = [t for t in trades if t.amount_high >= 100000 or t.disclosure_delay_days <= 7]
    if unusual:
        console.print()
        console.print(Panel(
            f"[bold yellow]Found {len(unusual)} potentially unusual trades[/]\n"
            "Large amounts or quick disclosures may indicate time-sensitive information.",
            title="Unusual Activity"
        ))


@cli.command()
@click.argument("market_slug")
@click.option("--demo", is_flag=True, help="Use demo data")
def analyze(market_slug: str, demo: bool):
    """
    Analyze a specific market for smart money signals.

    Provide the market slug from the Polymarket URL.
    Example: nomnom analyze fed-rate-cut-q1-2026 --demo
    """
    market = None

    if demo:
        # Find in demo data
        for m in get_demo_markets():
            if m.slug == market_slug:
                market = m
                break
    else:
        with console.status(f"[bold green]Analyzing market: {market_slug}[/]"):
            client = PolymarketClient()
            market = client.get_market_by_slug(market_slug)

    if not market:
        # Try demo data
        for m in get_demo_markets():
            if m.slug == market_slug:
                market = m
                break

    if not market:
        console.print(f"[red]Market not found: {market_slug}[/]")
        console.print("[dim]Available demo markets:[/]")
        for m in get_demo_markets():
            console.print(f"  - {m.slug}")
        return

    # Display market info
    console.print(Panel.fit(
        f"[bold]{market.question}[/]",
        title="Market Analysis"
    ))

    info_table = Table(box=box.SIMPLE, show_header=False)
    info_table.add_column("Field", style="dim")
    info_table.add_column("Value")

    info_table.add_row("YES Price", f"${market.yes_price:.2f}")
    info_table.add_row("NO Price", f"${market.no_price:.2f}")
    info_table.add_row("24h Volume", f"${market.volume_24h:,.0f}")
    info_table.add_row("Total Volume", f"${market.total_volume:,.0f}")
    info_table.add_row("Liquidity", f"${market.liquidity:,.0f}")
    info_table.add_row("Category", market.category or "N/A")

    if market.end_date:
        info_table.add_row("End Date", market.end_date.strftime("%Y-%m-%d"))

    info_table.add_row("[bold cyan]Trade URL[/]", f"[bold blue]{market.trade_url}[/]")

    console.print(info_table)


@cli.command()
@click.option(
    "--host", "-h",
    default="0.0.0.0",
    help="Host to bind to"
)
@click.option(
    "--port", "-p",
    default=5000,
    type=int,
    help="Port to bind to"
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode"
)
def web(host: str, port: int, debug: bool):
    """
    Start the web UI server.

    Launches a web interface for viewing trade recommendations,
    markets, and congressional trading data.
    """
    from .web import run_server

    console.print(Panel.fit(
        f"[bold cyan]NomNom Web UI[/]\n"
        f"[dim]Starting server at http://{host}:{port}[/]",
        box=box.DOUBLE
    ))
    console.print()
    console.print("[dim]Press Ctrl+C to stop the server[/]")
    console.print()

    run_server(host=host, port=port, debug=debug)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
