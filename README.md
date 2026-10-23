Reconcile broken contribution counts on GitHub
## Usage

```
python app.py
```

Opens http://localhost:8000. Pick a date, a count and an optional commit message, then click **Commit**. Click **Push** (and confirm) to push all local commits to GitHub.

- On first run it clones `contrib-recon-logs` next to this folder (`../contrib-recon-logs`).
- **Commit** never pushes; nothing reaches GitHub until you click **Push**.
- For GitHub to count them, your git `user.email` must be verified on your account, and the commits must be on the default branch.
