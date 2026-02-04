"""
Visualization Tools

Custom tools for creating charts and building HTML dashboards.
Used EXCLUSIVELY by the Dashboard Builder Subagent.
"""

from typing import Any, Dict
from claude_agent_sdk import tool
import json
from pathlib import Path


@tool(
    "create_chart",
    "Creates an HTML chart from data. Returns HTML snippet with embedded Chart.js visualization. Input should be JSON with chart_type, data, and options.",
    {"chart_config": str}
)
async def create_chart(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates an HTML/JavaScript chart using Chart.js.

    Expected input format (JSON string):
    {
        "chart_type": "bar",  # bar, line, pie, doughnut
        "title": "Performance Comparison",
        "labels": ["AAPL", "MSFT", "GOOGL"],
        "datasets": [
            {
                "label": "Returns (%)",
                "data": [15.2, 12.8, 18.5],
                "backgroundColor": ["#4CAF50", "#2196F3", "#FF9800"]
            }
        ]
    }
    """
    try:
        config = json.loads(args["chart_config"])
    except json.JSONDecodeError:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Invalid JSON format for chart configuration."
            }]
        }

    chart_type = config.get("chart_type", "bar")
    title = config.get("title", "Chart")
    labels = config.get("labels", [])
    datasets = config.get("datasets", [])

    # Generate unique chart ID
    import hashlib
    chart_id = f"chart_{hashlib.md5(title.encode()).hexdigest()[:8]}"

    # Create Chart.js configuration
    chart_html = f"""
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
                    title: {{
                        display: true,
                        text: '{title}',
                        font: {{
                            size: 18,
                            weight: 'bold'
                        }}
                    }},
                    legend: {{
                        display: true,
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
    """

    result = f"✅ Chart created: {title}\n"
    result += f"Type: {chart_type.capitalize()}\n"
    result += f"Chart ID: {chart_id}\n"
    result += f"Data points: {len(labels)}\n\n"
    result += "HTML snippet generated (stored in variable for dashboard assembly)"

    return {
        "content": [{
            "type": "text",
            "text": result
        }],
        "_chart_html": chart_html  # Internal use for dashboard builder
    }


@tool(
    "build_dashboard",
    "Assembles a complete HTML dashboard from sections and charts. Input should be JSON with title, sections, and chart references.",
    {"dashboard_config": str, "output_path": str}
)
async def build_dashboard(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Builds a complete HTML dashboard file.

    Expected input format (JSON string):
    {
        "title": "Investment Research Report",
        "company": "Apple Inc. (AAPL)",
        "date": "2025-02-04",
        "sections": [
            {
                "title": "Executive Summary",
                "content": "<p>Analysis text here...</p>"
            },
            {
                "title": "Financial Metrics",
                "content": "<div>Metrics content...</div>",
                "chart": "<div>...chart html...</div>"
            }
        ],
        "summary": {
            "sentiment": "Positive",
            "valuation": "Fairly Valued",
            "recommendation": "Hold"
        }
    }
    """
    try:
        config = json.loads(args["dashboard_config"])
    except json.JSONDecodeError:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Invalid JSON format for dashboard configuration."
            }]
        }

    output_path = args.get("output_path", "output/dashboard.html")

    title = config.get("title", "Investment Research Dashboard")
    company = config.get("company", "Unknown Company")
    date = config.get("date", "")
    sections = config.get("sections", [])
    summary = config.get("summary", {})

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .company {{
            font-size: 1.5em;
            opacity: 0.9;
        }}

        .header .date {{
            font-size: 1em;
            opacity: 0.8;
            margin-top: 10px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}

        .card h3 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}

        .card .value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}

        .section {{
            background: white;
            padding: 30px;
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .section h2 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}

        .section-content {{
            margin-top: 20px;
        }}

        .positive {{ color: #4CAF50; }}
        .negative {{ color: #f44336; }}
        .neutral {{ color: #FF9800; }}

        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            margin-top: 40px;
        }}

        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.8em; }}
            .summary-cards {{ grid-template-columns: 1fr; }}
        }}
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

    # Add summary cards if provided
    if summary:
        html += """
        <div class="summary-cards">
"""
        for key, value in summary.items():
            # Determine color class
            color_class = ""
            if "positive" in str(value).lower() or "buy" in str(value).lower():
                color_class = "positive"
            elif "negative" in str(value).lower() or "sell" in str(value).lower():
                color_class = "negative"
            else:
                color_class = "neutral"

            html += f"""
            <div class="card">
                <h3>{key.replace('_', ' ').title()}</h3>
                <div class="value {color_class}">{value}</div>
            </div>
"""
        html += """
        </div>
"""

    # Add sections
    for section in sections:
        section_title = section.get("title", "Section")
        section_content = section.get("content", "")
        section_chart = section.get("chart", "")

        html += f"""
        <div class="section">
            <h2>{section_title}</h2>
            <div class="section-content">
                {section_content}
            </div>
            {section_chart}
        </div>
"""

    html += """
    </div>

    <div class="footer">
        <p>Generated by Investment Research System (Module 3)</p>
        <p>Powered by Claude Agent SDK</p>
    </div>
</body>
</html>
"""

    # Write to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html)

    result = f"✅ Dashboard built successfully!\n\n"
    result += f"Output file: {output_path}\n"
    result += f"Total sections: {len(sections)}\n"
    result += f"Summary cards: {len(summary)}\n\n"
    result += f"Open the dashboard in your browser:\n"
    result += f"  file://{output_file.absolute()}"

    return {
        "content": [{
            "type": "text",
            "text": result
        }]
    }
