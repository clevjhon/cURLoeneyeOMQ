with open("oeneye_ecosystem_stream.html", "r", encoding="utf-8") as f:
    html = f.read()

# Insert live telemetry console container and SSE script before </body>
telemetry_widget = """
    <div class="asset-card" style="grid-column: 1 / -1; border-color: #00ff66; background: #020503;">
        <h3>OENEYE Kernel Telemetry Stream <span class="badge" style="background:#ff5555; color:#fff;">LIVE</span></h3>
        <div class="meta">Connected to endpoint: /live-stream</div>
        <pre id="log-console" style="height: 150px; background: #000; color: #00ff66; overflow-y: auto;">Initializing telemetry stream...</pre>
    </div>

    <script>
        const consoleEl = document.getElementById('log-console');
        const evtSource = new EventSource('/live-stream');
        
        evtSource.onopen = function() {
            consoleEl.textContent = "[*] Telemetry stream connected successfully.\\n";
        };

        evtSource.onmessage = function(event) {
            consoleEl.textContent += event.data + "\\n";
            consoleEl.scrollTop = consoleEl.scrollHeight;
        };

        evtSource.onerror = function(err) {
            consoleEl.textContent += "[-] Stream connection lost. Retrying...\\n";
        };
    </script>
</body>
</html>
"""

# Replace closing body tag with our widget + closing tags
if "</body>" in html:
    html = html.replace("</body>", telemetry_widget)
    with open("oeneye_ecosystem_stream.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("[+] Successfully injected live SSE telemetry widget into oeneye_ecosystem_stream.html")
else:
    print("[-] Error: Could not find closing body tag in HTML template.")
