# openskills

我的个人 agent skills 集合，遵循 Agent Skills 开放标准（agentskills.io），Codex、Claude Code、Gemini CLI、Cursor 等工具通用。

## 结构规范

每个 skill 一个目录，目录名即 skill 名：

```
skills/<skill-name>/
└── SKILL.md        必需，唯一必需文件
    scripts/        可选，可执行脚本
    references/     可选，参考文档
    assets/         可选，静态资源
```

SKILL.md 必须以 YAML frontmatter 开头：

```yaml
---
name: brief-write
description: 做什么 + 什么时候用 + 什么时候不用（agent 靠这一行决定是否加载）
---
```

- `name`：全小写、数字、短横线，不超过 64 字符，必须和目录名一致；命名用名词-动词顺序（如 `brief-write`）。
- `description`：不超过 1024 字符，必须写清做什么、何时使用、何时不用。
- 正文写指令本身，建议 500 行以内，长材料放 `references/`。
- 不使用 skill.yaml 等标准之外的元数据文件。

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
