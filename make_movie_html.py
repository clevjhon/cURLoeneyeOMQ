import os

def generate_html_movie():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OENEYE DOS Ecosystem - Virtual Volume Stream</title>
    <style>
        body { background-color: #000; color: #00ff00; font-family: monospace; padding: 20px; }
        .screen { border: 2px solid #00ff00; padding: 20px; max-width: 800px; margin: auto; }
        h1 { font-size: 1.2rem; border-bottom: 1px dashed #00ff00; padding-bottom: 10px; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <div class="screen">
        <h1>OENEYE HTML Movie Maker [THX Presentation Stream]</h1>
        <p><strong>MIME Type:</strong> text/html; charset=utf-8</p>
        <hr>
        <h2>Volume Directory: A:\\</h2>
        <pre>
Volume in drive A is MOSFETQ
README.TXT    106 bytes
HELLO.TXT      22 bytes
LONG.TXT     2240 bytes
FRAG.TXT     2800 bytes
PAD.BIN      3760 bytes
BIG.TXT     70000 bytes
DOCS &lt;DIR&gt;
        </pre>
        <h2>File Content Preview: README.TXT</h2>
        <pre>MOSFETQ DOS 0.2 reads this file from a real FAT12 volume.
The kernel walks the FAT cluster chain itself.</pre>
    </div>
</body>
</html>
"""
    with open("oeneye_movie.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Generated HTML movie asset successfully: oeneye_movie.html")

if __name__ == "__main__":
    generate_html_movie()
