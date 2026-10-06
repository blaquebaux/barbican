# Blaque Baux Barbican

**Tax-loss / turn-of-the-year reversal (the January effect) — a real edge, or a decayed anomaly that lives only in untradable illiquid names?**

The turn-of-year "January effect": stocks hammered all year are dumped in December for tax losses, then rebound in
January — classically strongest in small, retail-held, illiquid names. Barbican tests Kareem's null: is the January
bounce just repackaged mean-reversion that doesn't survive transaction costs and bid-ask bounce in illiquid names? **Two
data limits up front:** no institutional-ownership feed (can't build the "retail-driven / low-inst" filter), and no clean
small-cap survivorship-free universe (where the effect lives). So we test the index-level **January size effect**
(IWM−SPY) and a **December-loser reversal** in the large-cap universe, net of cost.

> **Not investment advice.** Educational/research software. See [DISCLAIMER](DISCLAIMER.md) and [LICENSE](LICENSE).

```bash
python3 research/barbican_1_turn_of_year.py   # needs Alpaca data keys in the environment
```

## The finding (decayed)

[`research/barbican_1_turn_of_year.py`](research/barbican_1_turn_of_year.py) — SIP daily total return, causal.

- **January size effect is gone/reversed** — IWM−SPY is **−0.35%/mo in January** (only 4/11 Januaries positive),
  *worse* than the −0.20% other-month average. No January small-cap premium over 2016-26.
- **December-loser reversal in large caps is weak/noisy** — the bottom-decile YTD losers beat the universe by just
  **+1.4pp** Dec→Jan (6/10 years), not reliable net of 2bps/side cost.
- **The real effect needs illiquid small caps** — the classic bounce is a small, retail-held, low-price phenomenon where
  bid-ask *bounce* inflates paper returns. That's untradable net, and unavailable here (no small-cap universe, no
  inst-ownership feed).

## Verdict

**NULL (decayed) — Kareem's null confirmed.** The tax-loss / January bounce doesn't survive as a tradable edge over
2016-26: the small-cap January premium has decayed or reversed, and the large-cap loser reversal is noise net of cost.
The anomaly survives only where it can't be harvested — small, retail-held, *illiquid* names whose bid-ask bounce
fabricates the paper return. It's a repackaged mean-reversion that died once it was crowded (consistent with `brief`'s
decayed seasonals). A `barbican_2` (small-cap universe + inst-ownership filter) would confirm it's untradable net, not
resurrect it.

## Status

**Research.** Honest null — a classic seasonal checked at the index and large-cap level and found decayed, with the
illiquid-small-cap caveat (where the effect and its fatal costs both live) stated plainly. January-size-effect test,
December-loser reversal, cost-aware, Alpaca SIP daily total return. No live capital.
