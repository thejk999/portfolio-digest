"""
weekly_digest.py
================
Weekly portfolio digest for a 12-stock portfolio.
Runs every Monday morning, fetches news + price data, asks Claude to summarize,
saves the result as a markdown file.

Designed for a 16-year-old learner-investor, deployable via GitHub Actions.
"""

import os
import sys
from datetime import datetime, timedelta
from urllib.parse import quote

import yfinance as yf
import feedparser
import anthropic

# === CONFIG ============================================================
# Edit this dict to add/remove holdings. Format: "TICKER": "Display Name"
# Use Yahoo Finance ticker conventions (e.g. ZAL.DE for German stocks).

PORTFOLIO = {
    "ZAL.DE":  "Zalando",
    "DUOL":    "Duolingo",
    "ONON":    "On Holding",
    "NKE":     "Nike",
    "KO":      "Coca-Cola",
    "VOO":     "Vanguard S&P 500 ETF",
    "MCD":     "McDonald's",
    "MSFT":    "Microsoft",
    "PG":      "Procter & Gamble",
    "SPOT":    "Spotify",
    "MELI":    "MercadoLibre",
    "DIS":     "Disney",
}

CLAUDE_MODEL = "claude-sonnet-4-6"
NEWS_PER_TICKER = 4
LOOKBACK_DAYS = 7

# === DATA FETCH ========================================================

def get_price_snapshot(ticker: str) -> dict | None:
    """Fetch last 7-day price move for a ticker."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="7d")
        if hist.empty or len(hist) < 2:
            return None
        current = float(hist['Close'].iloc[-1])
        week_ago = float(hist['Close'].iloc[0])
        change_pct = ((current - week_ago) / week_ago) * 100
        return {'current': round(current, 2), 'change_pct': round(change_pct, 2)}
    except Exception as e:
        print(f"[warn] price fetch failed for {ticker}: {e}", file=sys.stderr)
        return None


def get_news_rss(name: str, days: int = LOOKBACK_DAYS) -> list[dict]:
    """Fetch recent news headlines from Google News RSS."""
    query = f"{name} stock"
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"
    try:
        feed = feedparser.parse(url)
        cutoff = datetime.now() - timedelta(days=days)
        items = []
        for entry in feed.entries[:NEWS_PER_TICKER * 3]:
            try:
                published = datetime(*entry.published_parsed[:6])
                if published < cutoff:
                    continue
                items.append({
                    'title': entry.title,
                    'date': published.strftime('%Y-%m-%d'),
                })
                if len(items) >= NEWS_PER_TICKER:
                    break
            except Exception:
                continue
        return items
    except Exception as e:
        print(f"[warn] news fetch failed for '{name}': {e}", file=sys.stderr)
        return []


# === CLAUDE SYNTHESIS ==================================================

def build_prompt(data: dict) -> str:
    sections = []
    for ticker, info in data.items():
        name = PORTFOLIO[ticker]
        block = f"### {ticker} — {name}\n"
        if info['price']:
            p = info['price']
            block += f"7-day move: {p['change_pct']:+.1f}%  (current: {p['current']})\n"
        else:
            block += "Price data: unavailable\n"
        if info['news']:
            block += "Recent headlines:\n"
            for n in info['news']:
                block += f"  - [{n['date']}] {n['title']}\n"
        else:
            block += "Recent headlines: none in past week\n"
        sections.append(block)
    portfolio_summary = "\n".join(sections)

    return f"""You are writing a weekly investing digest for a 16-year-old learner-investor.

His portfolio (12 holdings):
{portfolio_summary}

Produce a digest in this exact structure:

## Movers
The 2 biggest up moves and 2 biggest down moves this week. One line each.
For each move, state ONLY: ticker, % change, direction.
Explanation rule: ONLY add an explanation if a specific headline in the data above directly names
the cause (e.g. an earnings result, product launch, executive change). If no headline directly
explains the move, write "(no specific catalyst in news)" and stop.
DO NOT speculate. DO NOT use phrases like "analysts suggest," "rotation into/out of," "macro pressure,"
"sector weakness," or any other generic framing. If the news doesn't say it, you don't say it.

## Newsworthy
Only items that materially affect a holding: earnings results, product launches, executive changes,
regulatory actions, M&A, major customer wins/losses. Maximum 5 bullets total across the whole portfolio.
SKIP: price-target changes, analyst notes, hype pieces, repackaged old stories, "stock to watch" lists.

## Action flags
DEFAULT OUTPUT: "None — quiet week."

Only deviate from the default if a holding shows ALL THREE of the following:
  (a) a specific, business-fundamental event named in the news data above
      (NOT price action, NOT analyst opinion, NOT short interest, NOT generic legal/HR matters
      unless they threaten core operations or are existential),
  (b) the event materially threatens long-term earnings power or the moat
      (a single bad quarter, a stock decline, or an HR investigation does NOT meet this bar),
  (c) a clear named driver in this week's news headlines, not your own interpretation
      or assembled inference from multiple weak signals.

If any of (a) (b) (c) is missing, output "None — quiet week."
"Worth watching" or "worth monitoring" is NOT an action flag — that is just normal holding behavior.
Action flags are reserved for events that would make a long-term holder reconsider the position.

## One thing worth reading
The single most useful article from the headlines above for a learner-investor.
One bullet. If nothing qualifies, write "Nothing essential this week."

RULES (strict):
- Brevity over completeness. 5 bullets per section maximum.
- No price predictions.
- No hedge words: "could," "might," "may," "potentially." Either say it plainly or skip it.
- No financial advice. This is a digest, not a recommendation.
- "Quiet week — no action needed" is a great output and means the system is working correctly.
- Never invent news that isn't in the data.
"""


def synthesize(data: dict) -> str:
    client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY env var
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": build_prompt(data)}],
    )
    return response.content[0].text


# === MAIN ==============================================================

def main():
    print(f"Fetching data for {len(PORTFOLIO)} holdings...")
    data = {}
    for ticker, name in PORTFOLIO.items():
        print(f"  {ticker} ({name})")
        data[ticker] = {
            'price': get_price_snapshot(ticker),
            'news': get_news_rss(name),
        }

    print("\nSynthesizing with Claude...")
    digest = synthesize(data)

    today = datetime.now().strftime("%Y-%m-%d")
    output = f"# Weekly Portfolio Digest — {today}\n\n{digest}\n\n---\n\n"
    output += "*Generated automatically. Not financial advice. Always verify before acting.*\n"

    # Save dated copy + 'latest' for convenience
    with open(f"digest_{today}.md", "w", encoding="utf-8") as f:
        f.write(output)
    with open("digest_latest.md", "w", encoding="utf-8") as f:
        f.write(output)

    print(f"\nDigest saved: digest_{today}.md")
    print("\n----- PREVIEW -----")
    print(digest[:500] + "...")


if __name__ == "__main__":
    main()
