from __future__ import annotations
from pathlib import Path
import html
import pandas as pd


def build_markdown(title: str, metrics: dict, assumptions: list[str] | None = None) -> str:
    assumptions=assumptions or []
    lines=[f"# {title}","","> Synthetic engineering analysis. Not flight-test or certified navigation performance.","","## Summary metrics",""]
    for k,v in metrics.items():
        if k=="config": continue
        if isinstance(v,float): v=f"{v:.3f}"
        lines.append(f"- **{k.replace('_',' ')}:** {v}")
    if assumptions:
        lines += ["","## Assumptions and limitations",""]+[f"- {a}" for a in assumptions]
    return "\n".join(lines)+"\n"


def markdown_to_simple_html(markdown: str) -> str:
    # Deliberately tiny dependency-free renderer for generated reports.
    out=[]
    for line in markdown.splitlines():
        e=html.escape(line)
        if line.startswith("# "): out.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "): out.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("> "): out.append(f"<blockquote>{html.escape(line[2:])}</blockquote>")
        elif line.startswith("- "): out.append(f"<p>{e}</p>")
        elif line: out.append(f"<p>{e}</p>")
    return "<!doctype html><meta charset='utf-8'><title>Assured PNT Report</title><body>"+"\n".join(out)+"</body>"


def write_report(path: str | Path, title: str, metrics: dict, assumptions=None):
    path=Path(path)
    md=build_markdown(title,metrics,assumptions)
    path.write_text(md,encoding="utf-8")
    html_path=path.with_suffix(".html")
    html_path.write_text(markdown_to_simple_html(md),encoding="utf-8")
    return path,html_path
