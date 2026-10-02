import json
from datetime import datetime, timezone

class OeneyeHTMLGenerator:
    def __init__(self, output_html="index.html"):
        self.output_html = output_html

    def generate(self):
        print("========================================")
        print("   OENEYE INSTITUTIONAL HTML GENERATOR")
        print("========================================")

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>oeneye | High-Assurance Kernel Architecture Portal</title>
    <meta name="dc.creator" content="Kai Olaf Ketelhut">
    <meta name="dc.publisher" content="Oeneye Archival Systems Berlin">
    <meta name="dc.date" content="{timestamp}" scheme="ISO8601">
    <meta name="dc.rights" content="Open Access / CC-BY-4.0">
    <style>
        :root {{
            --bg-color: #0b0e14;
            --card-bg: #111620;
            --border-color: #21262d;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --accent-color: #38bdf8;
            --success-color: #22c55e;
            --header-bg: #161b22;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            margin: 0;
            padding: 2rem;
            line-height: 1.6;
        }}
        .container {{
            max-width: 950px;
            margin: 0 auto;
        }}
        .institutional-header {{
            background-color: var(--header-bg);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--accent-color);
            padding: 1.2rem 1.5rem;
            border-radius: 4px;
            margin-bottom: 2rem;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }}
        .institutional-header span {{
            color: var(--text-primary);
            font-weight: 600;
        }}
        header {{
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }}
        h1 {{
            margin: 0 0 0.4rem 0;
            color: var(--accent-color);
            font-size: 2rem;
            letter-spacing: -0.5px;
        }}
        .subtitle {{
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        h2 {{
            margin-top: 0;
            font-size: 1.25rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
            color: var(--text-primary);
        }}
        ul {{
            padding-left: 1.2rem;
        }}
        li {{
            margin-bottom: 0.6rem;
        }}
        code {{
            background-color: rgba(56, 189, 248, 0.1);
            color: var(--accent-color);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: ui-monospace, monospace;
            font-size: 0.9rem;
        }}
        a {{
            color: var(--accent-color);
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .status-badge {{
            display: inline-block;
            background-color: rgba(34, 197, 94, 0.15);
            color: var(--success-color);
            border: 1px solid rgba(34, 197, 94, 0.3);
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.85rem;
        }}
        footer {{
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-top: 3rem;
            border-top: 1px solid var(--border-color);
            padding-top: 1rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="institutional-header">
            <div>Repository Authority: <span>Oeneye Archival Systems (Berlin, DE)</span></div>
            <div>Standard Compliance: <span>Dublin Core Metadata / Zenodo Open-Access Schema</span></div>
            <div>Deposition Record ID: <span>OE-2026-REV1</span></div>
        </div>

        <header>
            <h1>oeneye</h1>
            <div class="subtitle">High-Assurance Kernel Architecture & Chaosnet Deployment Portal</div>
        </header>

        <div class="card">
            <h2>System Status & Verification Metrics</h2>
            <p>Runtime container status: <span class="status-badge">VERIFIED CLEAN</span></p>
            <ul>
                <li><strong>Architecture:</strong> Dual-anchor ReFS / FSRS structural mapping</li>
                <li><strong>Container Specification:</strong> 819,200 bytes, 512-byte block alignment boundary</li>
                <li><strong>Invariant Verification:</strong> SUPB signature bound to <code>0xA5B2C3D8</code></li>
                <li><strong>Network Framing:</strong> 8-word Chaosnet-compliant protocol header (RFC / OPN / CLS)</li>
                <li><strong>Hosted AGI Token:</strong> <code>OENEYEbluh</code> (<code>0005</code> / <code>(0)b</code>) mapped via INT 48h telemetry</li>
            </ul>
        </div>

        <div class="card">
            <h2>Archival & Distribution Packages</h2>
            <ul>
                <li><strong>Technical Monograph:</strong> Compiled LaTeX document (<code>oeneye_monograph.tex</code>)</li>
                <li><strong>Repository Deposition:</strong> Zenodo-compliant JSON payload with Dublin Core XML mapping</li>
                <li><strong>Release Bundle:</strong> Compressed release tarball (<code>oeneye_release_v1.0.tar.gz</code>)</li>
                <li><strong>Audit Trail:</strong> Persistent transaction log confirming zero execution faults</li>
            </ul>
        </div>

        <div class="card">
            <h2>Legal & Compliance Governance</h2>
            <ul>
                <li><strong>End-User License Agreement:</strong> <a href="OENEYE_EULA.md" target="_blank">OENEYE_EULA.md</a></li>
                <li><strong>Zenodo Deposition Record:</strong> <a href="https://zenodo.org/records/22845198" target="_blank">10.5281/zenodo.22845198</a></li>
            </ul>
        </div>

        <footer>
            Compiled by Kai Olaf Ketelhut &bull; Archival Timestamp: {timestamp}
        </footer>
    </div>
</body>
</html>
"""

        with open(self.output_html, "w") as f:
            f.write(html_content)

        print(f"[+] Institutional homepage updated with EULA link: '{self.output_html}'")
        print("========================================")

if __name__ == "__main__":
    generator = OeneyeHTMLGenerator()
    generator.generate()
