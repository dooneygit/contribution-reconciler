Reconcile broken contribution counts on GitHub
## Usage

```
python app.py
```

Opens http://localhost:8000. Pick a date, a count and an optional commit message, then click **Add**.

- On first run it clones `contrib-recon-logs` next to this folder (`../contrib-recon-logs`).
- Commits are local only. Run `git push` in that folder when you want them on GitHub.
- For GitHub to count them, your git `user.email` must be verified on your account, and the commits must be on the default branch.
