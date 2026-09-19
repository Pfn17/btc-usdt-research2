from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.parts = []
        self.current = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.active = True
            self.current = []

    def handle_endtag(self, tag):
        if tag == "script" and self.active:
            self.parts.append("".join(self.current))
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.current.append(data)


html = Path(__file__).resolve().parents[1] / "dashboard/index.html"
parser = Scripts()
parser.feed(html.read_text(encoding="utf-8"))
assert parser.parts, "no script blocks found"
for i, source in enumerate(parser.parts):
    with tempfile.NamedTemporaryFile("w", suffix=f"-{i}.js", delete=False) as fh:
        fh.write(source)
        name = fh.name
    subprocess.run(["node", "--check", name], check=True)
print(f"checked {len(parser.parts)} dashboard script blocks")
