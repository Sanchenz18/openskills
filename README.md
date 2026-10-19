# openskills

我的个人 agent skills 集合。每个 skill 放在 `skills/<名称>/` 下，包含 `SKILL.md` 和 `skill.yaml`。

命名规范：全小写短横线分隔，名词-动词顺序（例如 `brief-write`）。

## 安装

clone 到任意目录，然后运行：

```
python install.py
```

Windows 下用 `py install.py`。会安装到 `~/.agents/skills`（优先软链；Windows 没开开发者模式时自动降级为复制，复制安装的话 `git pull` 更新后重跑一遍脚本即可）。

## Skills

| Skill | 说明 |
|---|---|
| `brief-write` | 把想法或任务写成背景/任务/范围/验收标准/约束五段式简报，用于 agent 交接或写方案计划时明确可交付事项。 |
