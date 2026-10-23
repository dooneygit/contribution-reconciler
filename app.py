import json
import os
import subprocess
import webbrowser
from datetime import date, datetime, time, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO_URL = "https://github.com/dooneygit/contrib-recon-logs.git"
REPO_DIR = Path(__file__).resolve().parent.parent / "contrib-recon-logs"
PORT = 8000
MAX_COUNT = 1000

PAGE = """<!doctype html>
<meta charset="utf-8">
<title>Contribution Reconciler</title>
<style>
  body { font-family: sans-serif; max-width: 320px; margin: 40px auto; }
  input, button { display: block; width: 100%; margin: 8px 0; padding: 6px; box-sizing: border-box; }
</style>
<h3>Add contributions</h3>
<input id="date" type="date">
<input id="count" type="number" min="1" max="1000" value="1">
<input id="message" type="text" placeholder="Commit message (default: contribution)">
<button id="commit">Commit</button>
<button id="push">Push</button>
<div id="result"></div>
<script>
  document.getElementById("date").valueAsDate = new Date();
  document.getElementById("push").onclick = async () => {
    if (!confirm("Push all local commits to GitHub?")) return;
    const res = await fetch("/push", { method: "POST" });
    document.getElementById("result").textContent = await res.text();
  };
  document.getElementById("commit").onclick = async () => {
    const res = await fetch("/add", {
      method: "POST",
      body: JSON.stringify({
        date: document.getElementById("date").value,
        count: document.getElementById("count").value,
        message: document.getElementById("message").value,
      }),
    });
    document.getElementById("result").textContent = await res.text();
  };
</script>
"""


def add_commits(day, count, message):
    # Noon plus one second per commit keeps every commit on the same day in any timezone.
    start = datetime.combine(day, time(12))
    for i in range(count):
        stamp = (start + timedelta(seconds=i)).isoformat()
        env = {**os.environ, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp}
        subprocess.run(
            ["git", "-C", str(REPO_DIR), "commit", "--allow-empty", "-q", "-m", message],
            env=env, check=True, capture_output=True, text=True,
        )


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.reply(200, PAGE, "text/html")

    def do_POST(self):
        if self.path == "/push":
            return self.push()
        if self.path != "/add":
            return self.reply(404, "Not found")
        try:
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            day = date.fromisoformat(body["date"])
            count = int(body["count"])
            message = str(body.get("message", "")).strip() or "contribution"
            if not 1 <= count <= MAX_COUNT:
                raise ValueError(f"count must be 1-{MAX_COUNT}")
        except (ValueError, KeyError, TypeError) as e:
            return self.reply(400, f"Invalid input: {e}")
        try:
            add_commits(day, count, message)
        except subprocess.CalledProcessError as e:
            return self.reply(500, f"git failed: {e.stderr.strip()}")
        self.reply(200, f"Added {count} commit(s) on {day} (local only, not pushed)")

    def push(self):
        try:
            # -u origin HEAD also works for the first push to an empty remote.
            subprocess.run(
                ["git", "-C", str(REPO_DIR), "push", "-u", "origin", "HEAD"],
                check=True, capture_output=True, text=True,
            )
        except subprocess.CalledProcessError as e:
            return self.reply(500, f"git push failed: {e.stderr.strip()}")
        self.reply(200, "Pushed to GitHub")

    def reply(self, status, text, content_type="text/plain"):
        data = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    if not REPO_DIR.exists():
        subprocess.run(["git", "clone", REPO_URL, str(REPO_DIR)], check=True)
    print(f"Committing to {REPO_DIR}\nServing on http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
