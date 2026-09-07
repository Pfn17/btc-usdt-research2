from pathlib import Path

root = Path(__file__).resolve().parents[1]
html_path = root / "dashboard" / "index.html"
html = html_path.read_text(encoding="utf-8")
old = "const researchEndpoint='/api/v1/research/hfb1';const researchUrl=$('start').value?researchEndpoint+'?oos_start_ms='+Date.parse($('start').value):researchEndpoint;"
new = "const researchEndpoint='/api/v1/research/hfb1';const researchUrl=researchEndpoint;"
if old not in html:
    raise SystemExit("dashboard research request fragment not found")
html_path.write_text(html.replace(old, new, 1), encoding="utf-8")

api_path = root / "src" / "btc_research" / "api.py"
api = api_path.read_text(encoding="utf-8")
needle = "def freshness(row:dict[str,Any]|None)->dict[str,Any]:\n"
helper = '''PUBLIC_AGGREGATE_FIELDS = (\n    "gross_profit", "gross_loss", "net_profit", "closed_observations",\n    "wins", "losses", "win_rate", "average_outcome", "profit_factor",\n    "maximum_drawdown", "status", "trading_enabled",\n)\n\ndef public_aggregate_metrics(row:dict[str,Any]|None)->dict[str,Any]:\n    """Allow only persisted aggregate performance fields into a public view.\n\n    Strategy identity, feature definitions, parameters, direction, timing,\n    rationale, and per-trade evidence are intentionally excluded. Missing\n    persisted metrics remain unavailable rather than being fabricated.\n    """\n    if row is None:\n        return {"status": "UNAVAILABLE", "trading_enabled": False}\n    return {key: row[key] for key in PUBLIC_AGGREGATE_FIELDS if key in row}\n\n'''
if needle not in api:
    raise SystemExit("freshness function not found")
if "def public_aggregate_metrics" not in api:
    api = api.replace(needle, helper + needle, 1)
api_path.write_text(api, encoding="utf-8")
print("public aggregate contract enforced")
