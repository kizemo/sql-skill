# sql-skill 接力 prompt

承接 handoff: `F:/soft/00selfmade/sql-skill/handoff-sql-skill-2026-10-13.md`

## 当前状态
- 项目根: `F:/soft/00selfmade/sql-skill/` (无 git)
- Phase 1 完成: 7 份权威 SQL 资料已沉淀到 `E:/obsidian/SQL/` (214M / 740 文件)
- Phase 2 待启动: 抽取知识形成 sql-skill v0.1 的 10 chapter 骨架
- 已有: evidence-skill (用户自建,已部署), 用户场景是企业 PG + Evidence BI

## 必交付 (Phase 2)
- 产出 `E:/obsidian/SQL/08-sql-skill/` 下的 skill 目录, 含 SKILL.md + chapters/ch0X-*.md
- 至少完成 ch01 / ch07 / ch08 三章 (ch08 优先, luke 48 章素材最丰富)
- 形态参照 evidence-skill: 10 chapter + glossary + patterns + cheatsheet

## 必读顺序
1. handoff 第 1-7 节
2. `E:/obsidian/SQL/00-索引.md`
3. `F:/soft/00selfmade/sql-skill/_knowledge_base/research-github-sql-agent-20261013.md` 末尾"启发与定位"
4. `E:/obsidian/SQL/03-use-the-index-luke/README.md` (ch08 核心素材清单)
5. (按需) `E:/Users/Duanyi/.claude/skills/evidence-skill/SKILL.md` 参考 skill 形态

## 必做动作
- 启动前调用 `superpowers:brainstorming` 与用户对齐第一个 chapter 选哪个
- 写 plan 调用 `superpowers:writing-plans`
- 每章完成前 `superpowers:verification-before-completion`

## 禁止事项
- 禁止 rm / Remove-Item / del 任何文件 (CLAUDE.md 红线)
- 禁止 git reset --hard / git clean -fd / git checkout -- / git stash drop
- 禁止 DROP / TRUNCATE / DELETE FROM 不带 WHERE
- 禁止在 E:/obsidian/SQL/ 文件名用 `\ / : * ? " < > |` 或 emoji
- 临时文件写 `C:\Temp\`, 不要写 `~/.tmp/`
- 不要重造 BI 产品 (DB-GPT/WrenAI/SQLBot 已堵死赛道), 定位 "Skill/库"
- 不要重复 handoff 内容, 直接读 handoff 文件

## 加速模式
无; 严格按 evidence-skill 形态产出, 不急不糙。
