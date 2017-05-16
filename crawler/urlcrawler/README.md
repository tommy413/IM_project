# urlcrawler
expects urlcrawler.log to exist

expects config.toml to exist


avoid checking in private data
```
git update-index --skip-worktree config.toml
git update-index --skip-worktree urlcrawler.log
```
