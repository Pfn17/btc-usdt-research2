from pathlib import Path

s = (Path(__file__).resolve().parents[1] / "dashboard/index.html").read_text(encoding="utf-8")
checks = [
    ("if(k==='H-MR1')", "if(k==='H-VOL1')", "research_hmr1_readiness", "research_hmr1_scan_frozen"),
    ("if(k==='H-VOL1')", "if(k==='HC2_CONDITIONAL_STATE')", "research_hvol1_readiness", "research_hvol1_scan_public"),
]
for start, end, required, forbidden in checks:
    part = s[s.index(start):s.index(end)]
    assert required in part, required
    assert forbidden not in part, forbidden
assert "document.getElementById('binancePrice').textContent=Number(x.lastPrice)" in s
assert "textContent='</html>" not in s
print("readiness-only and Binance runtime guards passed")
