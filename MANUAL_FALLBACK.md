# Manual fallback — Weekly digest without code

Use this if (a) the GitHub Actions setup feels like too much, or (b) the automation breaks and you need a digest this week anyway.

## Setup (one-time, 15 minutes)

1. Set up Google Alerts for each holding. For each ticker name (Zalando, Duolingo, On Holding, Nike, Coca-Cola, Vanguard S&P 500, McDonald's, Microsoft, Procter & Gamble, Spotify, MercadoLibre, Disney):
   - Go to google.com/alerts
   - Search term: e.g. `"Microsoft" stock`
   - Frequency: **Once a week**
   - Sources: News
   - Deliver to: your email
2. Set up a Yahoo Finance watchlist:
   - Go to finance.yahoo.com → sign in (free Google account works)
   - Create a watchlist with all 12 tickers
   - Bookmark it

## Each Monday morning (10 minutes)

1. Open your Yahoo Finance watchlist. Note the 7-day price changes.
2. Open the Google Alerts emails from the past week.
3. Open Claude.ai (or your Project) and paste the prompt below, filling in the data sections.

---

## The prompt (copy-paste into Claude.ai)

```
You are writing a weekly investing digest for a 16-year-old learner-investor.

His portfolio (12 holdings) — 7-day price moves and recent headlines:

### ZAL.DE — Zalando
7-day move: [+X.X% / -X.X%]
Recent headlines:
- [date] [headline]
- [date] [headline]

### DUOL — Duolingo
7-day move: [...]
Recent headlines:
- [...]

[... repeat for: ONON On Holding, NKE Nike, KO Coca-Cola, VOO S&P 500 ETF,
     MCD McDonald's, MSFT Microsoft, PG Procter & Gamble, SPOT Spotify,
     MELI MercadoLibre, DIS Disney ...]

If you have no headlines for a ticker, write "Recent headlines: none."
If you don't know the price move, write "7-day move: unknown."

Produce a digest in this exact structure:

## Movers
The 2 biggest up moves and 2 biggest down moves this week. One line each.
If news plausibly explains the move, name it. If not, do NOT speculate.

## Newsworthy
Only items that materially affect a holding: earnings results, product launches,
executive changes, regulatory actions, M&A, major customer wins/losses.
Maximum 5 bullets total. SKIP price-target changes, analyst notes, hype pieces.

## Action flags
Only fill this if something appears to challenge a long-term thesis.
Most weeks the answer is "None — quiet week." That is preferred output.

## One thing worth reading
The single most useful article from the headlines. One bullet.
If nothing qualifies, write "Nothing essential this week."

RULES (strict):
- Brevity over completeness. 5 bullets per section maximum.
- No price predictions.
- No hedge words ("could," "might," "may"). Either say it or skip it.
- No financial advice.
- "Quiet week — no action needed" is a great output.
- Never invent news that isn't in the data.
```

---

## Why the manual version might actually be better for you

- **Zero infrastructure.** Nothing to break, debug, or maintain.
- **Engaging.** The act of pasting headlines forces you to skim them — which builds market intuition faster than reading an AI summary.
- **Free with no API key.** Just uses Claude.ai (or a Project) directly.
- **Easy to evolve.** Want to change the format? Edit the prompt in 30 seconds. No code, no commit, no deploy.

The automated version is more impressive. The manual version is more useful for someone who's 16 and learning. Pick honestly.
