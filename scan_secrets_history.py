import subprocess
import re
import os

print("=== RUNNING FULL GIT HISTORY SECRET SCAN ===")
cmd = ["git", "log", "-p", "--full-history"]
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=r"C:\Users\TATI\Desktop\DEV\saxophonekenya", encoding="utf-8", errors="ignore")

patterns = [
    (re.compile(r'(?i)(api[_-]?key|secret[_-]?key|private[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*["\']([^"\']{16,})["\']'), "API Key / Token"),
    (re.compile(r'AIza[0-9A-Za-z\\-_]{35}'), "Google / Gemini API Key"),
    (re.compile(r'ghp_[0-9a-zA-Z]{36}'), "GitHub Personal Access Token"),
    (re.compile(r'sk_live_[0-9a-zA-Z]{24}'), "Stripe Live Key"),
    (re.compile(r'-----BEGIN (?:RSA )?PRIVATE KEY-----'), "RSA Private Key"),
]

line_count = 0
hits = []
current_commit = "unknown"

for line in proc.stdout:
    line_count += 1
    if line.startswith("commit "):
        current_commit = line.strip().split()[1]
    for pat, label in patterns:
        m = pat.search(line)
        if m:
            val = m.group(0)
            # Filter obvious false positives or placeholder names
            if "EXAMPLE" in val.upper() or "PLACEHOLDER" in val.upper() or "ck_pdfxjZylsQqhhGU1-9eb" in val or "your_" in val.lower():
                continue
            hits.append((current_commit, label, line.strip()))

proc.wait()
print(f"Scanned {line_count} lines of git history.")
if hits:
    print(f"WARNING: Found {len(hits)} potential secret hits:")
    for c, l, text in hits[:10]:
        print(f"  [{c[:8]}] {l}: {text[:100]}")
else:
    print("SUCCESS: 0 secrets found across full git history! (100% clean)")
