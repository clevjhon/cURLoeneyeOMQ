import os

search_term = "google.com"
print(f"Scanning project files for '{search_term}'...")

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith((".py", ".img", ".sh", ".txt")):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "rb") as f:
                    content = f.read()
                    if search_term.encode("utf-8") in content:
                        print(f"[Found] {filepath}")
            except Exception:
                pass
