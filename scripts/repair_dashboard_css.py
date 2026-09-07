from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
current_path = root / "dashboard" / "index.html"
current = current_path.read_text(encoding="utf-8")
base = subprocess.check_output(
    ["git", "show", "1dd9299:dashboard/index.html"],
    cwd=root,
    text=True,
)

def css(html: str) -> str:
    start = html.index("<style>") + len("<style>")
    end = html.index("</style>", start)
    return html[start:end]

def replace_css(html: str, content: str) -> str:
    start = html.index("<style>") + len("<style>")
    end = html.index("</style>", start)
    return html[:start] + content + html[end:]

current_css = css(current)
dynamic_css = current_css.split(".system-map,.lifecycle", 1)[1]
dynamic_css = ".system-map,.lifecycle" + dynamic_css
full_css = css(base).rstrip() + dynamic_css
repaired = replace_css(current, full_css)
current_path.write_text(repaired, encoding="utf-8")
print(f"restored_css_chars={len(full_css)}")
