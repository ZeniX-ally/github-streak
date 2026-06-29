# GitHub Streak Keeper

每天自动提交到 GitHub，保持贡献热力图活跃。

## 安装

### 1. 编辑配置

```bash
# 复制并编辑 config.json
cp config.example.json config.json
```

填入你的 GitHub Token（需 `repo` 权限）。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 注册计划任务

以管理员身份运行：

```batch
setup_task.bat
```

或手动创建计划任务：

- 触发器：每天 10:00（及任意时间）
- 操作：`python F:\Programe\github-streak\streak.py`
- 附加：可添加多个触发器（如 10:00、14:00、20:00）增加提交密度

## 提交规律

自动模拟真实开发者的提交规律：

| 每日提交数 | 概率 | 热力图颜色 |
|-----------|------|-----------|
| 0 | ~12% | 空白（休息日） |
| 1-2 | ~23% | 浅绿 |
| 3-5 | ~30% | 中绿 |
| 6-8 | ~20% | 深绿 |
| 1-4 | ~15% | 随机 |

提交时间分布在 9:00~21:00 的自然时间点，非固定整点。
