# sql-skill 项目 — 会话交接 handoff

> 会话结束日期: 2026-10-13
> 当前阶段: **Phase 1 完成 / Phase 2 待启动**
> 接力目标: 启动 Phase 2 知识抽取,产出 sql-skill v0.1 骨架

---

## 一、项目定位与用户场景

### 1.1 项目目标

构建一个面向 **企业 PostgreSQL + Evidence BI** 场景的 **SQL 编写专业度 Skill**,让 Claude/OpenClaw agent 在以下场景更专业、更准确:
- 编写 Evidence BI 报表调用的大量 PG SQL 语句
- 处理中文 schema 列名(evidence-skill 已有覆盖)
- 编写高性能 SQL(索引 / JOIN / 窗口函数 / CTE)
- 避免常见反模式(SQL Antipatterns 范畴)

### 1.2 用户技术栈

- **数据库**: 企业 PostgreSQL(中文 schema,列名如 `"店铺"` `"订单日期"`)
- **BI 工具**: Evidence BI (Core 2026,生产在跑)
- **Agent 平台**: Claude Code / OpenClaw(已装 evidence-skill 自建 skill)
- **凭据**: 通过环境变量管理(CLAUDE.md 硬编码红线)

### 1.3 与现有 skill 的关系

| Skill | 状态 | 关系 |
|---|---|---|
| evidence-skill | **已部署** | 业务落地知识(中文列名/date 类型/PG 陷阱) |
| sql-skill (本项目) | **建设中** | 通用 SQL 知识(语法/性能/反模式/PG 特性) |
| 两者联动 | Phase 4 目标 | sql-skill ch01-09 + evidence-skill ch05 互补 |

---

## 二、已完成内容 (本会话)

### 2.1 调研阶段 (Round 1-2)

| 文档 | 路径 | 用途 |
|---|---|---|
| GitHub SQL Agent 调研 | `F:/soft/00selfmade/sql-skill/_knowledge_base/research-github-sql-agent-20261013.md` | 12 字段对比矩阵 + 7 大启发 + 3 候选定位 |
| OpenClaw 生态补遗 | 同上文档末尾 | 391k⭐ OpenClaw 平台 + 5400+ skills 注册表 |

**关键结论**:
- 通用 SQL 编写专业度 skill **市场空白**
- 头部项目(eosphoros-ai/DB-GPT 20k⭐, Canner/WrenAI 17.8k⭐)都是产品/框架,不是教程
- 自建 sql-skill 走 **"基于权威教程抽提"** 路线是正确的

### 2.2 Phase 1 资料沉淀 (本会话主交付)

#### F:/soft/00selfmade/sql-skill/resource/ (工作副本, 213M)

| 资源 | 大小 | 文件数 | 用途 |
|---|---|---|---|
| awesome-postgres/ | 172K | 34 | PG 资源汇总 ch07 引用 |
| awesome-text2sql/ | 261K | 37 | Text2SQL 汇总 ch10 |
| awesome-llm-text2sql/ | 940K | 35 | LLM-Text2SQL 论文 |
| nl2sql-handbook/ | 199M | 105 | TKDE/VLDB 综述 + slides |
| sql-style-guide/ | 106K | 30 | Matt Mazur 风格 |
| sql-tutorial-civilian7/ | 13M | 428 | 30 表 750K 行教程 + 1065 题 |
| online/ | 600K | 70 | use-the-index-luke + SQLBolt + pg-docs |

#### E:/obsidian/SQL/ (长期沉淀, 214M / 740 文件) — **主沉淀地**

```
E:/obsidian/SQL/                              214M
├── 00-索引.md                  ← 主索引
├── 01-nl2sql-handbook/         199M
├── 02-sql-tutorial-civilian7/  13M
├── 03-use-the-index-luke/      1.8M
│   ├── README.md
│   ├── luke/        (48 章节)
│   ├── sqlbolt/     (17 课程)
│   └── pg-docs/     (5 章节)
├── 04-awesome-postgres/        164K
├── 05-sql-style-guide/         102K
├── 06-awesome-text2sql/        254K
└── 07-awesome-llm-text2sql/    932K
```

### 2.3 测试证据 (后台任务全部 exit 0)

- 6 个 GitHub 仓库 `git clone --depth 1` 成功
- 1 个 awesome-postgres 首次 TLS 错误,重试成功(避坑记)
- 48 个 use-the-index-luke 章节 curl 下载成功
- 17/18 SQLBolt 课程(1 个 HTTP 500)
- 5 个 PG 官方文档章节
- 6 个 cp -r 后台任务全部 exit 0
- 1 个全章节补全后台任务 exit 0
- 7 个 ls/du 验证全部通过

### 2.4 文件清单 (本会话所有产出,未 commit)

| 路径 | 类型 | 说明 |
|---|---|---|
| `F:/soft/00selfmade/sql-skill/_knowledge_base/research-github-sql-agent-20261013.md` | 调研笔记 | 280+ 行,GitHub SQL Agent 全景 |
| `F:/soft/00selfmade/sql-skill/resource/README.md` | 索引 | Phase 1 resource 索引 |
| `F:/soft/00selfmade/sql-skill/resource/DOWNLOAD_LOG.md` | 日志 | 详细下载记录 |
| `E:/obsidian/SQL/00-索引.md` | 主索引 | vault 沉淀主入口 |
| `E:/obsidian/SQL/03-use-the-index-luke/README.md` | 子索引 | 3 个在线教程章节清单 |

> **未做 git init** (项目根没有 .git)。下个会话如需版本管理,先 `git init`。

---

## 三、必读顺序 (新会话第一件事)

按这个顺序读,最快 5 分钟掌握全貌:

1. **本文件** (handoff) — 整体框架
2. **`E:/obsidian/SQL/00-索引.md`** — 资源全景
3. **`F:/soft/00selfmade/sql-skill/_knowledge_base/research-github-sql-agent-20261013.md` 末尾 "对 sql-skill 项目的启发与差异化定位建议"** — 章节设计依据
4. **`E:/obsidian/SQL/03-use-the-index-luke/README.md`** — ch08 核心素材清单
5. (按需) **`F:/soft/00selfmade/sql-skill/resource/README.md`** — resource 索引

---

## 四、下一步必交付 (Phase 2 — 知识抽取 → sql-skill v0.1)

### 4.1 核心目标

把已沉淀的 7 个资料源,**手工抽取**形成 sql-skill 的 **10 chapter 骨架**(v0.1):

| 章节 | 主题 | 主要素材源 |
|---|---|---|
| ch01 | SQL 语法铁律 | SQLBolt + civilian7 + sql-style-guide |
| ch02 | JOIN 7 种 + 性能差异 | SQLBolt joins + luke sql-join-* + civilian7 |
| ch03 | 窗口函数 (OVER/PARTITION BY/RANK/lead-lag) | luke sql-partial-results-window-functions + civilian7 advanced |
| ch04 | CTE / 递归 CTE / 物化 | civilian7 advanced + nl2sql-handbook chapter |
| ch05 | 聚合 / GROUP BY / HAVING / FILTER | SQLBolt aggregates + civilian7 |
| ch06 | 集合操作 (UNION/INTERSECT/EXCEPT) | civilian7 + PG docs |
| **ch07** | **PG 特有 (JSONB / GIN / array / FDW)** | **awesome-postgres + pg-docs + evidence-skill 联动** |
| **ch08** | **索引与性能 (B-Tree / Hash / GIN / BRIN / EXPLAIN)** | **luke 48 章核心 + pg-docs indexes/performance-tips** |
| ch09 | 反模式 (25+ SQL Antipatterns) | civilian7 实战 + evidence-skill ch05 联动 |
| ch10 | 与 evidence-skill 协作 / 范式 | nl2sql-handbook + awesome-text2sql |

### 4.2 Phase 2 建议执行路径

1. **先做 ch08 索引与性能** — 素材最丰富(luke 48 章),最体现"专业度"
2. **再做 ch01 语法铁律** — SQLBolt 17 课结构清晰
3. **再做 ch07 PG 特有** — 与用户实际 PG 环境对齐
4. **最后 ch09 反模式** — 与 evidence-skill ch05 形成完整反模式图谱

### 4.3 skill 形态要求 (按 evidence-skill 模式)

每个 chapter 输出:
- `chapters/ch0X-<topic>.md` (Markdown 源)
- 包含: 核心心智模型 / 通用规则 / 实战示例 / 反模式 / 跨引用
- 顶层 `SKILL.md` 入口
- 顶层 `glossary.md` + `patterns.md` + `cheatsheet.md`

### 4.4 工具链 (推荐)

- `superpowers:brainstorming` — Phase 2 启动前
- `superpowers:writing-skills` — skill 写作规范
- `superpowers:verification-before-completion` — 每章完成前验证
- `superpowers:writing-plans` — Phase 2 任务分解(可选)
- `huashu-info-search` — 补充最新文章(可选)

---

## 五、避坑提示

### 5.1 文件名/路径红线 (vault 规则)

`E:/obsidian/AGENTS.md` 强制:
- Windows 禁用字符: `\ / : * ? " < > |` 绝对禁止
- Emoji 不用,中文【】替代
- 文件名 ≤150 字符,完整路径 ≤200 字符
- 编号格式 `00-` `01-` 等

### 5.2 CLAUDE.md 红线

- **禁止删除用户文件** (rm / Remove-Item / del / rmdir / rd / Move-Item 丢回收站)
- **禁止单条命令触碰多个用户文件** (rm *.txt)
- **禁止清理 .claude / .claude-mem / .config 下任何文件**
- **禁止写危险 SQL** (DROP / TRUNCATE / DELETE FROM 不带 WHERE / DROP DATABASE)
- **禁止 git reset --hard / git clean -fd / git checkout -- / git stash drop** 在用户仓库下要 ask
- 临时文件必须写 `C:\Temp\`(不要写 `~/.tmp/`)

### 5.3 工具使用注意

- **WebFetch 报 400** → 用 `gh` CLI 替代(本会话已验证)
- **git clone 大仓库慢** → 用 `git clone --depth 1` (浅克隆)
- **curl 失败 1-2 个** → skip 即可(本次 SQLBolt 1 个 500,其他成功)

### 5.4 skill 设计陷阱

- 不要重造 BI 产品(已被 DB-GPT/WrenAI/SQLBot 堵死赛道)
- 不要把 sql-skill 做成"产品"形态,定位 **"Skill / Engine / 库"**
- ch10 不要重复 evidence-skill 内容,做"协作与范式"层

---

## 六、环境/基线状态

| 项 | 状态 |
|---|---|
| 工作目录 | `F:/soft/00selfmade/sql-skill/` |
| Git 仓库 | **未 init** (新会话可按需 `git init`) |
| Phase | 1 完成 / 2 待启动 |
| 长期沉淀 | `E:/obsidian/SQL/` (740 文件 / 214M) |
| 工作副本 | `F:/soft/00selfmade/sql-skill/resource/` (213M,可清理) |
| 调研笔记 | `_knowledge_base/research-github-sql-agent-20261013.md` (280+ 行) |
| evidence-skill | 用户已部署,内容在 `E:/Users/Duanyi/.claude/skills/evidence-skill/` |
| 网络环境 | GitHub `gh` CLI 正常,curl 大部分正常 |
| Claude 模型 | 当前会话为 MiniMax-M3,新会话可能不同 |

---

## 七、可能的扩展方向 (Phase 3+)

1. **评测集** — civilian7 1065 题筛选 100-200 题作为 sql-skill 评测
2. **联动测试** — sql-skill + evidence-skill 双加载场景测试
3. **PDF/EPUB 处理** — 用户购买 SQL Antipatterns / SQL Performance Explained 后,用 `book-to-skill` 处理
4. **多语言** — 国际化版本(目前 sql-style-guide 有中文版可参考)
5. **CI 集成** — sql-skill 自身用 TDD 维护(用 `superpowers:test-driven-development`)
6. **OpenClaw 适配** — 把 sql-skill 发布到 clawhub,供社区使用

---

## 八、验收清单 (新会话用)

新会话启动 Phase 2 时,自我验证:

- [ ] 已读 handoff + 00-索引 + 03/README + 调研笔记末尾"启发与定位"
- [ ] 已确认 E:/obsidian/SQL/ 7 个目录就绪
- [ ] 已明确 Phase 2 第一个 chapter 选哪个 (建议 ch08 索引与性能)
- [ ] 已调用 `superpowers:brainstorming` 与用户对齐 chapter 设计
- [ ] 已 `superpowers:writing-plans` 写 Phase 2 详细任务
- [ ] skill 文件输出在 `E:/obsidian/SQL/` (按 vault 规则) 而非 F 盘
- [ ] 每个 chapter 完成前 `superpowers:verification-before-completion` 验证
