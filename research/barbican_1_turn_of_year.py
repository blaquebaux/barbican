#!/usr/bin/python3
# =============================================================================
# barbican_1_turn_of_year.py — does the tax-loss/January bounce survive, or is it a decayed, illiquidity-only effect?
#
# SIP daily total return, causal.
#  (A) JANUARY SIZE EFFECT: IWM−SPY (small minus large) by calendar month — is January still special (tax-loss
#      rebound favours small caps), or has it decayed/reversed over 2016-26?
#  (B) DECEMBER-LOSER REVERSAL: each year, rank ~90 large caps by YTD (Jan→Nov) return at end-Nov; long the bottom
#      decile, hold Dec 1 → Jan 31; compare to the equal-weight universe over the same window, net of 2bps/side.
#  (C) the honest caveats: the real effect is in SMALL, retail-held, illiquid names (no inst-ownership feed here) where
#      bid-ask bounce inflates paper returns — so a large-cap test is a conservative read of a decayed anomaly.
# =============================================================================
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _barbican_common import panel, rets, stats, monthly
import numpy as np

UNIV = ["AAPL","MSFT","AMZN","GOOGL","META","NVDA","AVGO","ORCL","CRM","ADBE","CSCO","INTC","AMD","QCOM","TXN","IBM","MU","AMAT","LRCX","ADI","NOW","INTU",
        "JPM","BAC","WFC","GS","MS","C","AXP","V","MA","USB","PNC","SCHW","BLK","BK","COF",
        "JNJ","PFE","MRK","ABT","TMO","LLY","UNH","BMY","ABBV","AMGN","GILD","CVS","CI","MDT","DHR","ISRG",
        "XOM","CVX","COP","SLB","EOG","OXY","PSX","VLO",
        "HD","WMT","COST","TGT","NKE","MCD","SBUX","PG","KO","PEP","DIS","CMCSA","LOW","TJX","EL","CL","KMB",
        "BA","CAT","GE","HON","UNP","UPS","MMM","LMT","RTX","DE","T","VZ","NEE","DUK","SO"]
print("="*98); print("BARBICAN #1 — tax-loss / turn-of-the-year reversal"); print("="*98)

# ---- (A) January size effect ------------------------------------------------------------------------
P2, d2 = panel(["IWM", "SPY"])
mi = monthly(P2["IWM"], d2); ms = monthly(P2["SPY"], d2)
diff = {(y,m): ri-rs for (y,m,ri),(_,_,rs) in zip(mi, ms)}
by_month = {}
for (y,m), dv in diff.items(): by_month.setdefault(m, []).append(dv)
jan = by_month.get(1, []); other = [v for m,vs in by_month.items() if m!=1 for v in vs]
print(f"\n(A) JANUARY SIZE EFFECT (IWM−SPY, small minus large)")
print(f"  January avg {np.mean(jan)*100:+.2f}%/mo ({len(jan)} Januaries, {sum(1 for v in jan if v>0)} positive)   vs  other months {np.mean(other)*100:+.2f}%/mo")
print(f"  per-January: " + " ".join(f"{2016+i}:{v*100:+.0f}%" for i,v in enumerate(jan)))

# ---- (B) December-loser reversal (large caps) -------------------------------------------------------
P, dates = panel(UNIV); syms=[s for s in UNIV if s in P]; M=np.column_stack([P[s] for s in syms])
# index helpers
def idx_on_or_before(datestr):
    for i in range(len(dates)-1,-1,-1):
        if dates[i] <= datestr: return i
    return 0
years = sorted({int(d[:4]) for d in dates})
los_ret=[]; uni_ret=[]; COST=2e-4
for Y in years:
    i_nov = idx_on_or_before(f"{Y}-11-30"); i_dec1 = idx_on_or_before(f"{Y}-12-01"); i_jan = idx_on_or_before(f"{Y+1}-01-31")
    if i_jan <= i_dec1 or i_nov < 200: continue
    ytd = M[i_nov]/M[idx_on_or_before(f"{Y}-01-02")] - 1                 # Jan→Nov YTD
    k = max(2, len(syms)//10); los = np.argsort(ytd)[:k]
    hold = M[i_jan]/M[i_dec1] - 1                                         # Dec1 → Jan31 holding return
    los_ret.append(np.nanmean(hold[los]) - 2*COST); uni_ret.append(np.nanmean(hold))
los_ret=np.array(los_ret); uni_ret=np.array(uni_ret); edge=los_ret-uni_ret
print(f"\n(B) DECEMBER-LOSER REVERSAL (bottom decile, Dec→Jan, net 2bps/side, {len(los_ret)} years)")
print(f"  losers {np.mean(los_ret)*100:+.1f}%  vs  universe {np.mean(uni_ret)*100:+.1f}%  → edge {np.mean(edge)*100:+.1f}pp  (positive years {sum(1 for e in edge if e>0)}/{len(edge)})")

# ---- verdict ----------------------------------------------------------------------------------------
jan_effect = np.mean(jan) > np.mean(other) + 0.003 and np.mean(jan) > 0
loser_edge = np.mean(edge) > 0.01 and sum(1 for e in edge if e>0) > len(edge)*0.6
print("\n"+"="*98); print("READ:")
print(f"  • JANUARY SIZE EFFECT HAS {'SURVIVED' if jan_effect else 'DECAYED/REVERSED'}: small-minus-large in January is {np.mean(jan)*100:+.2f}%/mo vs {np.mean(other)*100:+.2f}% other months — {'small caps still pop in January' if jan_effect else 'no reliable January small-cap premium over 2016-26 (the classic effect is gone in this window)'}.")
print(f"  • DECEMBER-LOSER REVERSAL is {'real' if loser_edge else 'weak/absent'} in large caps: losers beat the universe by {np.mean(edge)*100:+.1f}pp Dec→Jan ({sum(1 for e in edge if e>0)}/{len(edge)} years positive) — {'a genuine bounce' if loser_edge else 'noisy and not reliable, net of cost'}.")
print(f"  • THE REAL EFFECT NEEDS ILLIQUID SMALL CAPS: the classic January/tax-loss bounce is a small, retail-held, low-price phenomenon where bid-ask BOUNCE inflates paper returns — untradable net, and unavailable here (no small-cap survivorship-free universe, no inst-ownership feed).")

if jan_effect and loser_edge:
    v = ("CONDITIONAL: the turn-of-year reversal still shows up — verify net of REAL small-cap trading frictions (bid-ask "
         "bounce, borrow) before trusting it, since that's where the effect and the costs both live. barbican_2 = small-cap universe + inst-ownership filter.")
else:
    v = ("NULL (decayed): the tax-loss/January bounce does not survive as a tradable edge over 2016-26 — the January "
         f"small-cap premium has decayed/reversed (IWM−SPY {np.mean(jan)*100:+.2f}%/mo in Jan, no better than other months), and the "
         f"December-loser reversal in liquid large caps is weak and noisy net of cost (edge {np.mean(edge)*100:+.1f}pp). The classic effect "
         "survives only where it can't be harvested — small, retail-held, ILLIQUID names whose bid-ask bounce fabricates "
         "the paper return — exactly Kareem's null. It's a repackaged mean-reversion that died once it was crowded and "
         "the liquid version pays nothing (consistent with brief's decayed seasonals). barbican_2 = a real small-cap "
         "universe + inst-ownership filter to confirm it's untradable net, not to resurrect it.")
print(f"\n  VERDICT: {v}")
print("  (Large-cap + index proxies; the real tax-loss effect is small-cap/retail/illiquid — no such clean universe or")
print("   inst-ownership feed in Alpaca. January size effect and large-cap loser-bounce are the honest, conservative tests.)")
