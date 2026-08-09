"""Build the manuscript PDF from manuscript.md with weasyprint.

Tables are already written as markdown in the manuscript, so nothing is rebuilt
from CSV here. The "Figure Legends" section is removed from the flowing text and
re-emitted at the end with the actual images attached to their captions.

Figure order follows the manuscript:
- Figure 1 = km_survival.png      (Kaplan-Meier, three panels)
- Figure 2 = hazard_by_year.png   (discrete-time hazard; the seven-year spike)
- Figure 3 = km_by_sex.png        (survival by sex)
"""

import re
from pathlib import Path

import markdown
import weasyprint

PROJECT_DIR = Path(__file__).parent
PLOTS_DIR = PROJECT_DIR / "plots"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
MANUSCRIPT_MD = PROJECT_DIR / "manuscript.md"

FIGURES = {
    "Figure 1": "km_survival.png",
    "Figure 2": "hazard_by_year.png",
    "Figure 3": "km_by_sex.png",
}

CSS = """
@page {
    size: A4;
    margin: 2.5cm 2cm;
    @bottom-center { content: counter(page); font-size: 10pt; color: #666; }
}
body {
    font-family: "Times New Roman", "DejaVu Serif", Georgia, serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #111;
}
h1 { font-size: 16pt; margin-top: 0; margin-bottom: 8pt; line-height: 1.3;
     page-break-after: avoid; }
h2 { font-size: 13pt; margin-top: 20pt; margin-bottom: 6pt;
     border-bottom: 1px solid #ccc; padding-bottom: 3pt;
     page-break-after: avoid; }
h3 { font-size: 11.5pt; margin-top: 14pt; margin-bottom: 4pt;
     page-break-after: avoid; }
h4 { font-size: 11pt; margin-top: 12pt; margin-bottom: 4pt;
     page-break-after: avoid; }
p { margin: 6pt 0; text-align: justify; widows: 3; orphans: 3; }
ol li, ul li { margin: 6pt 0; widows: 2; orphans: 2; }
blockquote { margin: 8pt 0 8pt 14pt; padding-left: 10pt;
             border-left: 3px solid #ccc; color: #333; }
sup { font-size: 0.75em; }
table {
    border-collapse: collapse; width: 100%; margin: 10pt 0;
    font-size: 9pt;
    page-break-inside: avoid;
}
th, td { border: 1px solid #999; padding: 3pt 5pt; text-align: left; }
th { background: #e8e8e8; font-weight: bold; }
hr { border: none; border-top: 1px solid #ccc; margin: 16pt 0; }
img { max-width: 100%; height: auto; margin: 10pt 0; }
strong { font-weight: bold; }
em { font-style: italic; }
.figure-block {
    page-break-inside: avoid;
    page-break-before: always;
    margin: 1.5em 0;
    text-align: center;
}
.figure-block img {
    display: block;
    margin: 0 auto;
    max-width: 95%;
    max-height: 78vh;
}
.figure-caption {
    font-size: 10pt;
    text-align: justify;
    margin-top: 0.5em;
}
"""


def extract_figure_legends(md_text: str) -> dict[str, str]:
    """Pull each figure's caption out of the Figure Legends section.

    Captions are written as `**Figure N. Short title.** Body text...`, so the
    bold run holds the title and everything up to the next figure is the body.
    """
    legends = {}
    pattern = r"\*\*Figure (\d+)\.\s*(.*?)\*\*\s*(.*?)(?=\n\n\*\*Figure |\n\nAll figure labels|\Z)"
    for m in re.finditer(pattern, md_text, re.DOTALL):
        number, title, body = m.group(1), m.group(2).strip(), m.group(3).strip()
        legends[f"Figure {number}"] = (title, " ".join(body.split()))
    return legends


def render_figure_block(label: str, filename: str, title: str, body: str) -> str:
    path = PLOTS_DIR / filename
    if not path.exists():
        print(f"[WARN] {path} not found, skipping {label}")
        return ""
    return (
        '<div class="figure-block">'
        f'<img src="file://{path.resolve()}" alt="{label}">'
        f'<p class="figure-caption"><strong>{label}. {title}</strong> {body}</p>'
        "</div>\n"
    )


def convert():
    md_text = MANUSCRIPT_MD.read_text(encoding="utf-8")
    legends = extract_figure_legends(md_text)

    missing = [k for k in FIGURES if k not in legends]
    if missing:
        print(f"[WARN] no legend text found for: {', '.join(missing)}")

    # Drop the legend section from the flowing text; it is re-emitted with images.
    md_text = re.sub(r"## Figure Legends.*\Z", "", md_text, flags=re.DOTALL)

    # pandoc-style superscripts (^1^) -> <sup>
    md_text = re.sub(r"\^([^^]+?)\^", r"<sup>\1</sup>", md_text)

    html_body = markdown.markdown(md_text, extensions=["tables", "smarty"])

    figures_html = ""
    for label, filename in FIGURES.items():
        title, body = legends.get(label, ("", ""))
        figures_html += render_figure_block(label, filename, title, body)

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{html_body}{figures_html}</body></html>"""

    out_path = OUTPUT_DIR / "manuscript.pdf"
    weasyprint.HTML(string=html, base_url=str(PROJECT_DIR)).write_pdf(str(out_path))
    print(f"[OK] {out_path} ({out_path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    convert()
