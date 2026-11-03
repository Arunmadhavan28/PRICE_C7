from pathlib import Path

dist_dir = Path(__file__).resolve().parent / "dist"
html_path = dist_dir / "index.html"
css_files = list((dist_dir / "assets").glob("*.css"))

if css_files and html_path.exists():
    css_text = css_files[0].read_text(encoding="utf-8")
    html_text = html_path.read_text(encoding="utf-8")
    if "<style id=\"inlined-theme\">" not in html_text:
        inlined = f"<style id=\"inlined-theme\">\n{css_text}\n</style>\n</head>"
        html_text = html_text.replace("</head>", inlined)
        html_path.write_text(html_text, encoding="utf-8")
        print(f"Successfully inlined {len(css_text)} bytes of CSS into {html_path}")
