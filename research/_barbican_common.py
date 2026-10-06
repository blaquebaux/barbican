#!/usr/bin/python3
# =============================================================================
# _barbican_common.py — shared helpers for Blaque Baux BARBICAN (tax-loss / turn-of-the-year reversal).
# Alpaca SIP daily bars (adjustment=all → total return); env keys. Read-only.
#
# The turn-of-the-year / "January effect": stocks hammered all year get dumped in December for tax losses, then
# rebound in January — classically strongest in small, retail-held, illiquid names. BARBICAN tests Kareem's null:
# is the January bounce just repackaged mean-reversion that doesn't survive transaction costs and bid-ask bounce in
# illiquid names? TWO DATA LIMITS, stated up front: (1) no institutional-ownership feed, so the "low-inst / retail-
# driven" filter can't be built; (2) the effect lives in SMALL caps, where a survivorship-free universe isn't
# available here — so we test the clean, index-level JANUARY SIZE EFFECT (IWM−SPY) and a December-loser reversal
# within the large-cap universe (where the effect is weakest). brief already found seasonals decayed; this is the
# specific January/tax-loss case. Dates carry calendar month for seasonal grouping.
# =============================================================================
import os, json, urllib.request, math, datetime
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
START, END = "2016-01-01", "2026-08-01"
_cache = {}

def bars(s):
    if s in _cache: return _cache[s]
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={s}&timeframe=1Day"
         f"&start={START}&end={END}&adjustment=all&feed=sip&limit=10000")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
        _cache[s] = {b["t"][:10]: b["c"] for b in d.get("bars", {}).get(s, [])}
    except Exception:
        _cache[s] = {}
    return _cache[s]

def panel(syms):
    D = {s: bars(s) for s in syms}; D = {s: v for s, v in D.items() if len(v) > 250}
    if not D: return {}, []
    u = [s for s in syms if s in D]; dates = sorted(set.intersection(*[set(D[s]) for s in u]))
    return {s: np.array([D[s][d] for d in dates], float) for s in u}, dates

def rets(px): return px[1:] / px[:-1] - 1

def stats(r, ppy=252):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 10 or r.std() == 0: return dict(sh=float('nan'), mean=float('nan'), t=float('nan'))
    return dict(sh=r.mean()/r.std()*math.sqrt(ppy), mean=float(r.mean()), t=float(r.mean()/(r.std()/math.sqrt(len(r)))))

def monthly(px, dates):
    """Calendar-month returns: list of (year, month, ret)."""
    out = {}
    for i in range(1, len(px)):
        y, m, _ = dates[i].split("-"); key = (int(y), int(m))
        out.setdefault(key, 1.0); out[key] *= px[i]/px[i-1]
    return [(y, m, v-1) for (y, m), v in sorted(out.items())]
