"""GitHub Streak Keeper — 自动提交保持热力图活跃"""

import json
import os
import random
import subprocess
import sys
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"
LOG_FILE = BASE_DIR / "streak.log"
DATA_FILE = BASE_DIR / "data.json"
CONTENT_DIR = BASE_DIR / "content"


# ─── 默认配置 ──────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "repo_url": "https://github.com/ZeniX-ally/github-streak.git",
    "repo_dir": str(BASE_DIR / "repo"),
    "commit_interval": (9, 22),
    "max_commits_per_run": 8,
    "enabled": True,
}

COMMIT_MESSAGES = [
    "chore: update daily log",
    "chore: auto-commit {date}",
    "docs: update timestamp",
    "refactor: minor cleanup",
    "style: format content",
    "chore: bump tracker",
    "docs: add daily entry",
    "chore: sync progress",
    "test: verify pipeline",
    "chore: maintenance",
    "docs: record activity",
    "chore: regular update",
]

CONTENT_TEMPLATES = [
    "Activity log entry for {date}.\nCommit count today: {count}\n",
    "Daily checkpoint: {date}\nSequence: #{seq}\n",
    "Progress update - {date}\nBatch: {batch}\n",
    "Development log: {date}\nTask tracking entry #{seq}\n",
]


def log(msg: str) -> None:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        log("配置文件已创建，请编辑 config.json 填入 GitHub Token")
        sys.exit(0)

    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def weighted_commit_count() -> int:
    """生成自然的提交数量分布"""
    r = random.random()
    if r < 0.12:
        return 0
    elif r < 0.35:
        return random.randint(1, 2)
    elif r < 0.65:
        return random.randint(3, 5)
    elif r < 0.85:
        return random.randint(6, 8)
    else:
        return random.randint(1, 4)


def ensure_repo(cfg: dict) -> str:
    repo_dir = Path(cfg["repo_dir"])
    token = cfg.get("token", "")

    if not token:
        log("错误: config.json 中缺少 token")
        sys.exit(1)

    if repo_dir.exists() and (repo_dir / ".git").exists():
        return str(repo_dir)

    log("克隆仓库...")
    auth_url = cfg["repo_url"].replace("https://", f"https://{token}@")
    subprocess.run(
        ["git", "clone", auth_url, str(repo_dir)],
        check=True, capture_output=True, text=True,
    )
    subprocess.run(
        ["git", "-C", str(repo_dir), "config", "user.name", "streak-bot"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo_dir), "config", "user.email", "streak-bot@users.noreply.github.com"],
        check=True, capture_output=True,
    )
    log("仓库克隆完成")
    return str(repo_dir)


def make_commits(repo_path: str, count: int) -> list[str]:
    """创建 count 次提交，返回 commit hash 列表"""
    today = datetime.date.today().isoformat()
    content_dir = Path(repo_path) / "content"
    content_dir.mkdir(exist_ok=True)

    hashes = []
    for i in range(count):
        msg = random.choice(COMMIT_MESSAGES).format(date=today)
        template = random.choice(CONTENT_TEMPLATES)
        entry = template.format(
            date=today, count=count, seq=i + 1, batch=random.randint(1000, 9999),
        )

        file_path = content_dir / f"{today}.md"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)

        commit_time = _random_commit_time()
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = commit_time
        env["GIT_COMMITTER_DATE"] = commit_time

        subprocess.run(
            ["git", "-C", repo_path, "add", "."],
            check=True, capture_output=True,
        )
        result = subprocess.run(
            ["git", "-C", repo_path, "commit", "--allow-empty", "-m", msg],
            check=True, capture_output=True, text=True, env=env,
        )
        hashes.append(result.stdout.strip())

    return hashes


def _random_commit_time() -> str:
    """在当天的工作时间内随机挑选提交时间"""
    h = random.randint(9, 21)
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return datetime.datetime.now().replace(hour=h, minute=m, second=s, microsecond=0).isoformat()


def push(repo_path: str, token: str) -> bool:
    auth_url = f"https://{token}@github.com/ZeniX-ally/github-streak.git"
    result = subprocess.run(
        ["git", "-C", repo_path, "push", auth_url, "master"],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        log("推送成功")
        return True
    log(f"推送失败: {result.stderr.strip()[:200]}")
    return False


def main():
    cfg = load_config()
    if not cfg.get("enabled", True):
        log("已禁用，跳过")
        return

    repo_path = ensure_repo(cfg)
    count = weighted_commit_count()

    if count == 0:
        log("今日跳过（随机决定不提交）")
        return

    log(f"本日计划提交 {count} 次")
    hashes = make_commits(repo_path, count)
    log(f"已完成 {len(hashes)} 次提交")

    push(repo_path, cfg.get("token", ""))


if __name__ == "__main__":
    main()
