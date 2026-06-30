#!/usr/bin/env python3
"""
Dashboard Report Builder Helper Script

Assembles a complete interactive HTML dashboard (Chart.js) from a JSON config.
Renders chart specs into Chart.js snippets and writes a single HTML file. This
replaces the previous in-process visualization custom tools with a skill-driven
helper script.

Passing a compact JSON config (instead of having the agent emit the full HTML)
keeps the model's output small and avoids dashboard truncation on large reports.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path


def render_chart(spec: dict) -> str:
    """Render a chart spec into a Chart.js HTML snippet."""
    chart_type = spec.get("chart_type", "bar")
    title = spec.get("title", "Chart")
    labels = spec.get("labels", [])
    datasets = spec.get("datasets", [])
    chart_id = f"chart_{hashlib.md5(title.encode()).hexdigest()[:8]}"

    return f"""
    <div class="chart-container" style="position: relative; height:400px; margin: 20px 0;">
        <canvas id="{chart_id}"></canvas>
    </div>
    <script>
        new Chart(document.getElementById('{chart_id}'), {{
            type: '{chart_type}',
            data: {{
                labels: {json.dumps(labels)},
                datasets: {json.dumps(datasets)}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{ display: true, text: '{title}', font: {{ size: 18, weight: 'bold' }} }},
                    legend: {{ display: true, position: 'bottom' }}
                }}
            }}
        }});
    </script>
    """


def section_chart_html(section: dict) -> str:
    """Return chart HTML for a section, from raw 'chart' html, a single
    'chart_spec', or a list of 'chart_specs'."""
    if section.get("chart"):
        return section["chart"]
    if section.get("chart_specs"):
        return "\n".join(render_chart(spec) for spec in section["chart_specs"])
    if section.get("chart_spec"):
        return render_chart(section["chart_spec"])
    return ""


def build_html(config: dict) -> str:
    title = config.get("title", "Investment Research Dashboard")
    company = config.get("company", "Unknown Company")
    date = config.get("date", "")
    sections = config.get("sections", [])
    summary = config.get("summary", {})

    head = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header .company {{ font-size: 1.5em; opacity: 0.9; }}
        .header .date {{ font-size: 1em; opacity: 0.8; margin-top: 10px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .summary-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
        .card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); transition: transform 0.3s; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 4px 20px rgba(0,0,0,0.15); }}
        .card h3 {{ color: #667eea; margin-bottom: 10px; font-size: 1.2em; }}
        .card .value {{ font-size: 1.8em; font-weight: bold; color: #333; }}
        .section {{ background: white; padding: 30px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .section h2 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; margin-bottom: 20px; font-size: 1.8em; }}
        .section-content {{ margin-top: 20px; }}
        .positive {{ color: #4CAF50; }}
        .negative {{ color: #f44336; }}
        .neutral {{ color: #FF9800; }}
        .footer {{ text-align: center; padding: 30px; color: #666; margin-top: 40px; }}
        @media (max-width: 768px) {{ .header h1 {{ font-size: 1.8em; }} .summary-cards {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="company">{company}</div>
        <div class="date">Generated: {date}</div>
    </div>

    <div class="container">
"""

    body = ""
    if summary:
        body += '        <div class="summary-cards">\n'
        for key, value in summary.items():
            value_str = str(value).lower()
            if "positive" in value_str or "buy" in value_str:
                color_class = "positive"
            elif "negative" in value_str or "sell" in value_str:
                color_class = "negative"
            else:
                color_class = "neutral"
            label = key.replace("_", " ").title()
            body += (
                f'            <div class="card"><h3>{label}</h3>'
                f'<div class="value {color_class}">{value}</div></div>\n'
            )
        body += "        </div>\n"

    for section in sections:
        section_title = section.get("title", "Section")
        content = section.get("content", "")
        chart_html = section_chart_html(section)
        body += f"""        <div class="section">
            <h2>{section_title}</h2>
            <div class="section-content">
                {content}
            </div>
            {chart_html}
        </div>
"""

    footer = """    </div>

    <div class="footer">
        <p>Generated by Investment Research System (Module 3)</p>
        <p>Powered by Claude Agent SDK</p>
    </div>
</body>
</html>
"""
    return head + body + footer


def main():
    parser = argparse.ArgumentParser(
        description="Assemble an HTML investment dashboard from a JSON config"
    )
    parser.add_argument("--input", required=True, help="Path to JSON dashboard config")
    parser.add_argument("--output", required=True, help="Path to write the HTML dashboard")
    args = parser.parse_args()

    try:
        config = json.loads(Path(args.input).read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: could not read JSON config: {e}", file=sys.stderr)
        sys.exit(1)

    html = build_html(config)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)

    sections = config.get("sections", [])
    summary = config.get("summary", {})
    print("Dashboard built successfully.")
    print(f"Output file: {out}")
    print(f"Sections: {len(sections)} | Summary cards: {len(summary)}")
    print(f"Open in your browser: file://{out.absolute()}")


if __name__ == "__main__":
    main()
