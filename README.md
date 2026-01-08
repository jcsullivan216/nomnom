Detecting informed money in prediction markets: A methodological framework
Prediction markets like Polymarket, Kalshi, and PredictIt have become significant venues where insider knowledge translates directly into tradeable positions—often before information disseminates publicly. This framework provides a systematic methodology for identifying when informed money is moving, combining on-chain behavioral analysis, cross-platform signal detection, public disclosure monitoring, OSINT tradecraft, and market microstructure approaches. The core insight is that informed traders leave detectable traces: fresh wallets with unusually high accuracy, options flow preceding corporate events, congressional trades clustering before policy announcements, and cross-platform price divergences that reveal information asymmetry.

The regulatory environment creates unique opportunities. Unlike securities markets, insider trading on prediction markets is not explicitly illegal under current CFTC jurisdiction—meaning informed actors face fewer constraints, leave more visible trails, and the detection framework operates in a legally ambiguous zone that rewards analytical sophistication over legal enforcement.

On-chain wallet analysis reveals informed trading patterns
Blockchain-based platforms like Polymarket (built on Polygon) expose every trade to public scrutiny, creating rich behavioral data. The most reliable red flags for informed trading include wallet age correlated with bet timing, success rate anomalies, and coordinated multi-wallet activity.

Wallet age analysis examines the temporal relationship between wallet creation and bet placement. The December 2025 "AlphaRaccoon" case demonstrates the pattern: wallet 0xafEe deposited $3 million on a Friday and immediately began placing large bets, achieving 22-of-23 correct predictions on Google Year in Search markets and previously nailing the exact Gemini 3.0 release date. Fresh wallets placing high-conviction, highly accurate bets within hours of funding represent the clearest informed trading signal.

Wallet clustering techniques identify coordinated activity or single actors using multiple wallets. Research from Nansen and blockchain forensics literature identifies two key funding patterns: diffusion funding (one wallet funding many in tree structures) and consolidation (multiple wallets funneling to collection points). DBSCAN and OPTICS clustering on transaction timing, contract interaction sequences, and position sizing distributions can group related wallets. The Louvain method enables community detection in transaction graphs, while Jaccard similarity measures behavioral overlap between wallet activity sequences.

Historical accuracy tracking is perhaps the most decisive signal. Wallets with success rates exceeding 70% across 20+ predictions warrant investigation—particularly when concentrated in specific market categories (e.g., a single company's events). Platforms like PolyWallet, Hashdive, and Parsec's "Insider Finder" provide these metrics. Key data access points include:

Polymarket Subgraphs (via The Graph/Goldsky): Core market data, positions, order fills, P&L calculations
Dune Analytics dashboards: dune.com/rchen8/polymarket for general analytics; dune.com/alexmccullough/how-accurate-is-polymarket for accuracy analysis
Bitquery GraphQL API: Direct querying of Polymarket contract events
CTF Exchange contract (0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E): All order fills and position changes on Polygon mainnet
Position building patterns distinguish accumulation from single large bets. Informed traders with long-lived information strategically spread orders (TWAP-like patterns) to minimize price impact, while those with urgent, short-lived information trade aggressively. Order flow imbalance—the signed difference between buy and sell volume—is the most robust predictor of informed trading according to empirical research.

Cross-platform price divergences signal information asymmetry
Information doesn't flow instantaneously across prediction markets, creating exploitable lead-lag relationships. A seminal 2025 SSRN paper provides the first empirical evidence: Polymarket leads Kalshi in price discovery, particularly during high liquidity periods, with net order imbalance of large trades significantly predicting subsequent returns.

The mechanism is structural. Polymarket's higher global liquidity ($3.2 billion traded on the 2024 election alone), lower fees (0.01% vs Kalshi's ~0.7%), 
PolyTrack
 and crypto-native user base create faster information incorporation. When the same event trades on multiple platforms, the first to move likely receives information first—or has better-informed traders.

Cross-platform arbitrage detection follows a simple framework: when YES price (Platform A) + NO price (Platform B) < $1.00, risk-free profit exists minus fees. Automated bots executing this strategy generated $40 million in arbitrage profits between April 2024-April 2025, with over $4.2 million from a single bot executing 10,200+ bets. Critical caveat: resolution differences create risk—the 2024 government shutdown market resolved "Yes" on Polymarket but "No" on Kalshi for the same event.

Data access for cross-platform analysis:

Polymarket API: clob.polymarket.com (REST), wss://clob.polymarket.com/ws (WebSocket), 100 req/min public rate limit 
Predictorsbest
Kalshi API: api.kalshi.com/v1, OAuth 2.0 authentication, FIX protocol for institutional integration
Unified aggregators: FinFeedAPI (Polymarket, Kalshi, Myriad), PredictionData.dev (10B+ tick-level updates, 3 years history)
EventArb.com: Real-time arbitrage calculator across Kalshi, Polymarket, Robinhood, IBKR
The correlation between prediction markets and traditional financial markets provides additional signal sources. Research shows financial markets take 3-5 days to fully reflect information that prediction markets price immediately. During the 2024 election, DJT stock showed cumulative abnormal returns of ±50% while betting odds moved ±1.5%—prediction markets responded within hours while equity markets required days. Currency markets show similar patterns: geopolitical risk prediction models predict 88% of currency returns in out-of-sample tests across 17 countries.

Political disclosure databases expose regulatory insider signals
Congressional trading disclosures, lobbying filings, and revolving door patterns create public records that correlate with policy prediction market movements. The STOCK Act requires Members of Congress to disclose transactions within 30-45 days—this mandatory delay creates predictable information lags.

Congressional trading anomalies persist despite regulation. Academic research documents that senators' portfolios beat the market by ~10% annually (Ziobrowski et al., 2004), with post-STOCK Act studies showing senators still earn 4.9% abnormal returns over 3 months. Committee members trading in sectors they regulate provide the strongest correlation with policy outcomes.

Primary data sources:

Senate Financial Disclosures: efdsearch.senate.gov (searchable by filer, year, form type)
House Financial Disclosures: disclosures-clerk.house.gov/FinancialDisclosure
Third-party aggregators with APIs: Quiver Quantitative (integrates with QuantConnect for algorithmic strategies), Capitol Trades, Financial Modeling Prep (Senate/House Disclosure API endpoints)
Lobbying disclosure analysis provides leading indicators for policy outcomes. The Senate Lobbying Disclosure System (lda.senate.gov) offers a REST API for programmatic access to LD-1 (registration), LD-2 (quarterly activity), and LD-203 (contribution) filings. Bulk quarterly downloads available in XML/JSON. Spikes in lobbying spending on specific issues often precede policy action—correlate issue codes and bill numbers with prediction market contracts on related legislation.

Regulatory calendar analysis identifies pre-announcement positioning windows:

Federal Register API (federalregister.gov/developers/documentation/api/v1): All Federal Register contents since 1994, 
CRAN
 no API key required
OIRA review tracking (reginfo.gov): Real-time status of rules under Office of Information and Regulatory Affairs review; average 50 days, trending longer
Public Inspection: Documents appear one business day before Federal Register publication—creating a narrow but predictable advance window
The revolving door between government and private sector creates predictive patterns. OpenSecrets.org tracks officials moving between federal government and private sector, though data is not available for bulk download. Track personnel announcements in regulatory agencies, departures from key congressional committees, and correlate with prediction market movements on related policy outcomes.

OSINT tradecraft adapted for prediction market intelligence
Open source intelligence provides leading indicators across political, corporate, and geopolitical prediction markets. The most valuable sources combine real-time tracking (flight data, social media) with archival analysis (court filings, patent databases).

Flight tracking via ADS-B Exchange (adsbexchange.com) provides unique value: it does not honor FAA block requests, tracking military, government, and private aircraft that commercial services hide. Academic research demonstrated that tracking corporate jets visiting potential acquisition targets provided early M&A indicators; researchers identified 47 public and 18 non-public meetings by clustering 542 government aircraft movements over 18 months. 
ResearchGate
 API access available via RapidAPI; commercial licensing required for business use. 
ADS-B Exchange

Maritime AIS data enables supply chain and commodity market prediction. MarineTraffic 
MarineTraffic
Venntel
 (now part of Kpler) covers 
MarineTraffic
 550,000+ active vessels 
Kpler
 with APIs for live positions, historical movements, port calls, 
Marinetraffic
 and critically, AIS gap detection indicating potential dark activity 
Kpler
 (sanctions evasion, illicit trade). Kpler's container tracking achieves 87% predictive ETA accuracy 7-10 days out— 
Kpler
valuable for retail inventory and port congestion predictions.

Satellite imagery costs have decreased dramatically:

Sentinel Hub/Copernicus: FREE imagery for environmental and agricultural monitoring
Use cases: Factory parking lot activity, military movements, crop conditions, construction progress
Court docket monitoring through RECAP/CourtListener (courtlistener.com, operated by Free Law Project) provides "Google Alerts for federal courts"—real-time alerts when new filings match saved searches. The platform crowdsources PACER documents via browser extension, creating a free searchable archive. 
 As stated in their documentation: "Investors can monitor for mentions of publicly traded companies in court documents, potentially catching important litigation before it becomes widely known." 
 Pricing: free tier (5 daily alerts) to $100/month for unlimited real-time alerts.

Corporate intelligence signals:

Job postings as leading indicators: Coresignal Jobs API (231M+ records, updated every 6 hours); hiring for specific technical skills indicates R&D direction; M&A integration roles signal upcoming deals
Certificate Transparency logs (crt.sh): New SSL certificates reveal upcoming product launches, acquisitions, or new services before public announcement
SEC EDGAR APIs: Free real-time access 
SEC
 to 8-K material events, Form 4 insider trades (2-day filing deadline), 13D activist positions
Market microstructure metrics detect informed flow
Statistical approaches from market microstructure literature provide quantitative frameworks for anomaly detection. The foundational insight: informed traders interact with liquidity in detectable patterns.

VPIN (Volume-Synchronized Probability of Informed Trading) overcomes limitations of traditional PIN models for real-time detection. 
Quantresearch
 Using volume-clock buckets rather than time windows, VPIN measures order flow toxicity as |Vbuy - Vsell| / (Vbuy + Vsell). 
GitHub
 VPIN rose to historically high levels one hour before the 2010 Flash Crash. 
Quantresearch
 Research shows DeFi markets exhibit 3.88x higher toxicity than centralized exchanges—prediction markets on blockchain may show similar patterns.

Kyle's Lambda measures price impact per unit of order flow (Δp = λ · S + u). Higher λ indicates greater price impact and potentially more informed trading. 
 However, empirical research (Ahern, 2018) found that only absolute order imbalance and autocorrelation of order flows are statistically robust predictors when controlling for strategic timing—many sophisticated traders time their trades to minimize detectable footprints.

Machine learning approaches have achieved high accuracy in detecting informed trading:

Isolation Forest: Based on principle that anomalies are easier to isolate; 
 successfully assigns higher anomaly scores to convicted insiders 
Transformer autoencoders for limit order book data: 93% accuracy, F1-Score 0.91, AUC-ROC 0.95 
GAN-based detection: 94.7% accuracy with sub-3ms latency, processing 150,000 transactions/second
Hybrid Autoencoder + Isolation Forest: 0.98-0.99 accuracy in anomaly detection benchmarks 
Signal combination through Bayesian ensembles provides the most robust detection. The principle: two algorithms of different nature unlikely to agree on false positives. Only output high anomaly scores when multiple models agree. 
 Bayesian Ensemble for Anomaly Detection (Yu et al.) provides theoretical foundation—posterior distributions interpreted as probability of anomalies, fully unsupervised with no labeled training data required.

Corporate event signals from options and credit markets
Options flow anomalies represent perhaps the most documented informed trading signal. Academic research from NYU/McGill found that 25% of M&A deals showed unusual options activity in the month before announcement—odds of coincidence: 3 in 1 trillion.

Key indicators for unusual options activity:

Volume-to-open interest ratio exceeding 5-10x average
Sweep trades (orders split across multiple exchanges executed near-simultaneously)
Above-ask purchases indicating urgency and conviction
Out-of-the-money calls on cash acquisition targets
Platforms for monitoring: Unusual Whales ($50/month), Market Chameleon ($99/month), FlowAlgo ($99-149/month), Barchart (free tier available). All pull from OPRA consolidated options trade data.

SEC filings create predictable information events:

Form 4 (insider trading): 2-day filing deadline; cluster buying by multiple insiders is strongest signal
13D filings (activist positions): Harvard Business School study found 10.3% excess return in 18 months following filing
8-K (material events): 4-day filing deadline; real-time monitoring via SEC EDGAR streaming API or sec-api.io
Short interest and securities lending data from S3 Partners and ORTEX (daily updates by 7:30am ET) provide signals for corporate event positioning. Key metrics: shares on loan, cost to borrow (spikes indicate hard-to-borrow), utilization (% of lendable shares currently lent). The SEC publishes fails-to-deliver data bi-monthly; 2023 research confirmed T+35 FTD cycles correlate with price volatility.

CDS spreads as corporate health indicators anticipate rating downgrades and lead corporate bond markets in price discovery. A 2022 Journal of Banking & Finance study found CDS spreads statistically significant in predicting corporate default 1-12 months ahead. 
 Data from Markit/IHS (end-of-day composite spreads), DTCC Trade Information Warehouse (weekly activity), or Bloomberg Terminal (real-time).

Integrating signals into a detection system
The optimal detection framework combines multiple weak signals through ensemble methods, addresses false positive management through consensus requirements, and validates against known insider events.

Recommended architecture:

Layer	Function	Primary Data Sources
Real-time ingestion	Stream market activity	Polymarket/Kalshi WebSockets, OPRA options feed
Behavioral analysis	Wallet/trader clustering, success rate tracking	On-chain data via The Graph, Dune
Cross-platform monitoring	Lead-lag detection, arbitrage signals	FinFeedAPI, custom aggregation
Public disclosure integration	Congressional trades, lobbying, regulatory calendar	EDGAR, lda.senate.gov, Federal Register APIs
OSINT enrichment	Flight tracking, court filings, corporate intelligence	ADS-B Exchange, RECAP, Coresignal
Anomaly detection	VPIN, Isolation Forest, ensemble models	Custom implementation
Signal weighting hierarchy (based on empirical robustness):

Order imbalance and order flow autocorrelation (most robust across conditions)
Wallet success rate anomalies (>70% across 20+ predictions)
Cross-platform price divergence (Polymarket leading Kalshi)
Options flow preceding corporate events (25% of M&A deals show signal)
Disclosure timing (congressional trades, 13D filings)
False positive management requires consensus across heterogeneous signals. The ensemble principle: unlikely that two different algorithms agree on false positives. 
ScienceDirect
 Conservative thresholds (require 3+ signal types) dramatically reduce false positive rates while maintaining detection power for genuine informed trading.

Backtesting against known events: Use SEC/DOJ enforcement actions, M&A announcements with convicted insider cases, and resolved prediction markets with documented manipulation attempts (AlphaRaccoon, Maduro capture bet, Nobel Peace Prize investigation) as ground truth. Ahern (2018) methodology provides 410 hand-collected illegal insider trading events covering 312 firms with specific trading dates.

Conclusion: The informed money detection opportunity
The prediction market ecosystem in 2026 presents a unique analytical opportunity. Regulatory ambiguity means informed actors face fewer constraints than in traditional markets, leaving more visible trails. Blockchain transparency exposes behavioral patterns impossible to detect in traditional venues. Cross-platform fragmentation creates exploitable information asymmetries.

The most actionable signals combine wallet-level behavioral anomalies (fresh wallets, abnormal success rates, clustering patterns) with cross-market lead-lag analysis (Polymarket leading Kalshi by minutes to hours) and traditional financial market correlation (options flow, SEC filings, CDS spreads preceding prediction market movements).

The methodological frontier involves combining these heterogeneous signals through ensemble machine learning approaches—Bayesian frameworks that weight signal quality by historical predictive power while managing false positive rates through consensus requirements. 
 The firms that operationalize this framework first will capture significant edge before the market matures and arbitrages these inefficiencies away.

# NomNom - Insider Signal Detection App

An application that detects informed trading patterns in prediction markets and generates trade recommendations with direct links. Built on the methodological framework described above.

## Features

- **Multi-Signal Detection Engine**: Combines order flow imbalance, volume spikes, congressional trading correlation, price momentum, and timing patterns
- **Trade Recommendations**: Actionable signals with confidence scores, expected edge, and Kelly-derived position sizing
- **Direct Trade Links**: One-click links to execute trades on Polymarket
- **Congressional Trading Monitor**: Track trades by members of Congress for policy insider signals
- **Web UI & CLI**: Both a modern web interface and command-line tools
- **API Endpoints**: JSON APIs for integration with other tools

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nomnom.git
cd nomnom

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Requirements

- Python 3.10+
- Dependencies: requests, pandas, numpy, flask, rich, click

### Running the Web UI

```bash
# Start the web server
python main.py web

# Or with custom host/port
python main.py web --host 127.0.0.1 --port 8080

# Enable debug mode for development
python main.py web --debug
```

Then open http://localhost:5000 in your browser.

### Using the CLI

```bash
# Scan for insider signals (use --demo if no network access)
python main.py scan --demo

# Scan with custom confidence threshold
python main.py scan --min-confidence 0.6 --max-results 5

# Output as JSON for integration
python main.py scan --demo --json

# List active markets with trade links
python main.py markets --demo

# View congressional trading activity
python main.py congress --demo

# Filter by chamber
python main.py congress --demo --chamber senate

# Analyze a specific market
python main.py analyze fed-rate-cut-q1-2026 --demo
```

## Project Structure

```
nomnom/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── setup.py               # Package setup
└── nomnom/
    ├── __init__.py
    ├── cli.py             # CLI interface
    ├── web.py             # Flask web app
    ├── polymarket.py      # Polymarket API client
    ├── congress.py        # Congressional trading data
    ├── signals.py         # Signal detection engine
    ├── recommendations.py # Trade recommendations
    ├── demo_data.py       # Demo data for testing
    └── templates/         # HTML templates
        ├── base.html
        ├── index.html
        ├── markets.html
        └── congress.html
```

## Signal Types

The detection engine analyzes multiple signals, weighted by empirical robustness:

| Signal | Weight | Description |
|--------|--------|-------------|
| Order Imbalance | 30% | Buy/sell pressure from order book analysis |
| Congressional Correlation | 25% | Trades by Congress members in related sectors |
| Volume Spike | 20% | Unusual 24h volume relative to historical average |
| Price Momentum | 15% | Conviction patterns near price extremes |
| Timing Pattern | 10% | Activity near resolution or disclosure windows |

## API Endpoints

The web server exposes JSON APIs:

```bash
# Get trade recommendations
GET /api/recommendations?min_confidence=0.5&demo=true

# Get active markets
GET /api/markets?limit=20&demo=true

# Get congressional trades
GET /api/congress?days=30&demo=true
```

## Example Output

```
TRADE RECOMMENDATION
====================
Market: Will the Federal Reserve cut interest rates in Q1 2026?

Position:     BUY YES
Confidence:   78%
Current Price: $0.72
Expected Edge: 8.0%
Suggested Size: 4.0% of bankroll

Signal Type: Order Flow Imbalance

Why This Recommendation:
  1. Strong buy pressure: 42% order imbalance
  2. Volume spike: 3.2x normal ($847K in 24h)
  3. Congressional trade: Tommy Tuberville (R) buy $175K in financial sector

TRADE NOW: https://polymarket.com/event/fed-rate-cut-q1-2026
```

## Data Sources

- **Polymarket**: gamma-api.polymarket.com for market data, clob.polymarket.com for order books
- **Congressional Trading**: House Stock Watcher and Senate Stock Watcher public APIs
- **Demo Mode**: Built-in realistic demo data for testing without network access

## Disclaimer

This tool detects potential insider activity patterns for educational and research purposes only. All trading involves risk. The signals generated are probabilistic indicators, not guarantees. Do your own research before making any trades. This is not financial advice.

---

## Methodological Framework
