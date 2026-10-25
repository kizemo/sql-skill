# sql-skill

> **把「企业级 SQL 工程知识」压进 agent 的上下文里 —— 而且只花 2,105 token。**
> PostgreSQL / MySQL / Oracle / SQL Server · 11 章 + 5 辅助文件 · 4,375 行章节正文 · 全库 5,648 行
> 配套 [evidence-skill](https://github.com/kizemo/evidence-skill) 业务侧,两者严格互补。

[![GitHub](https://img.shields.io/badge/GitHub-kizemo%2Fsql--skill-blue)](https://github.com/kizemo/sql-skill)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)](https://www.python.org/)
[![Claude Code](https://img.shields.io/badge/Claude_Code-compatible-blueviolet)](https://claude.com/claude-code)
[![Tokens](https://img.shields.io/badge/trigger_cost-2%2C105_tok-success)](https://github.com/kizemo/sql-skill)

---

## TL;DR

通用大模型写 SQL 有三个系统性问题:**语法会写,语义会错;记住了却找不到;知道了却塞不下。**

`sql-skill` 对这三件事各给一个答案:

| 问题 | 解法 | 实测 |
|---|---|---|
| 不知道该用哪种索引 / JOIN / 窗口函数 | 11 章结构化知识 + 13 张决策表 + 25+ 反模式 | 覆盖 civilian7 **1090 题 100%** |
| 通用知识库一次性灌进上下文 = 烧钱 | **渐进式披露**:index 层只留路由,正文按需读 | 单次触发 **5,734 → 2,105 tok(-63%)** |
| 知识写完就过期 | 4 通道自动同步进 gbrain,写完即同步 | **写文件 → brain 可查 ≈ 1 秒** |

> 这不是一个「更大的 prompt」,而是一份**被测量过、被评测过、能自我更新的** SQL 知识资产。

---

## 一、它解决什么

不是「教模型写 SQL」,而是补上模型**恰好最弱**的那一段:工程判断。

| 通用模型的典型失败 | sql-skill 的答案 | 在哪 |
|---|---|---|
| `WHERE col = NULL` 恒 0 行,模型不报错直接给答案 | NULL 三值逻辑 + `IS NULL` 改写 | [ch01 §3](sql-skill/chapters/ch01-grammar.md) |
| `OFFSET 100000` 深分页,模型照抄不质疑 | keyset 分页 + 为什么 OFFSET 会线性变慢 | [ch08 §5](sql-skill/chapters/ch08-indexes-perf.md) |
| 索引建了但没走 —— 列上套了函数 | WHERE 索引失效 3 类 + 各自修法 | [ch08 §2](sql-skill/chapters/ch08-indexes-perf.md) |
| 迁移到 Oracle 后 `= ''` 静默丢数据 | 四方言语义地雷对照表 | [ch11](sql-skill/chapters/ch11-multi-db.md) |
| 中文列名不双引号 → `column does not exist` | 中文 schema 雷区 + 假名修复流程 | [ch07 §5](sql-skill/chapters/ch07-pg-specific.md) |
| `EXPLAIN` 读不懂,只看 estimated rows | 估算 ≠ 实际,rows mismatch 怎么办 | [ch08 §6](sql-skill/chapters/ch08-indexes-perf.md) |

**边界很诚实**:只讲「通用 SQL 工程判断」。业务侧(Evidence BI / nginx / FDW 部署 / 中文 schema 假名映射明细 / MCP)归 [evidence-skill](https://github.com/kizemo/evidence-skill),ch10 把这条边界固化成铁律。

---

## 二、内容结构:渐进式披露

这是本项目**最核心的设计**。多数「知识库 skill」失败在两点:要么正文太长(每次触发都烧钱),要么拆得太碎(agent 找不到该读哪页)。

```
┌─ index 层 ─────────────────────────────────────────────┐
│  frontmatter:description + triggers + 元数据            │  每会话都付
│  100 tok  ← 预算 ~100                                  │
└────────────────────────────────────────────────────────┘
                        ↓ 触发时
┌─ load 层 ──────────────────────────────────────────────┐
│  SKILL.md 正文:12 大框架速查 + Gotchas + 章节索引         │  2,005 tok
│  预算 ~5,000                                           │
└────────────────────────────────────────────────────────┘
                        ↓ 按需读
┌─ files 层 ─────────────────────────────────────────────┐
│  chapters/ch01-ch11.md  ·  supporting/*.md              │  无限预算
│  references/topic-index.md · references/retrieval.md   │  只读用得上的
└────────────────────────────────────────────────────────┘
```

**实测(用 [skill-forge](https://github.com/kizemo/skill-optimizer) 自己的 tokenizer,不是拍脑袋):**

| 层级 | v0.1 | v0.3 | 降幅 | 预算 |
|---|---:|---:|---:|---|
| index(每会话都付) | 231 tok | **100 tok** | **-57%** | ~100 ✅ |
| load(触发时) | 5,503 tok | **2,005 tok** | **-64%** | ~5,000 ✅ |
| **单次触发合计** | **5,734 tok** | **2,105 tok** | **-63%** | — |
| validator 警告 | 11 条 | **0 条** | — | — |

> 对比:`evidence-skill` 触发成本 1,556 tok。**sql-skill 用一半的价格覆盖 4 个方言 + 全部通用 SQL 工程判断。**

设计细节见 [`docs/audit/`](docs/audit/),改动逐条列在 [CHANGELOG](docs/CHANGELOG.md)。

---

## 三、章节索引(11 章)

每章统一 9 段结构(Core Idea → Frameworks → Key Concepts → Mental Models → Anti-patterns → Code Examples → Reference Tables → Key Takeaways → Connects To),**结构一致 = agent 能预测每章长什么样**。

| # | 章节 | 主题 | 行数 |
|---|---|---|---:|
| 1 | [ch01-grammar.md](sql-skill/chapters/ch01-grammar.md) | SQL 语法铁律:8 子句执行顺序 / 别名作用域 / NULL 三值逻辑 / 风格铁律 | 256 |
| 2 | [ch02-joins.md](sql-skill/chapters/ch02-joins.md) | JOIN 7 种 + 性能差异 + N+1 反模式 | 450 |
| 3 | [ch03-window-functions.md](sql-skill/chapters/ch03-window-functions.md) | OVER / PARTITION BY / ROW_NUMBER / RANK / LAG-LEAD / 帧子句 / 命名窗口 | 488 |
| 4 | [ch04-cte-recursion.md](sql-skill/chapters/ch04-cte-recursion.md) | WITH / WITH RECURSIVE / MATERIALIZED / CTE vs 子查询 vs 临时表 | 454 |
| 5 | [ch05-aggregates.md](sql-skill/chapters/ch05-aggregates.md) | 聚合 / GROUP BY / HAVING / FILTER / ROLLUP-CUBE / GROUPING SETS | 448 |
| 6 | [ch06-set-ops.md](sql-skill/chapters/ch06-set-ops.md) | UNION / UNION ALL / INTERSECT / EXCEPT + 与 JOIN 转换 | 352 |
| 7 | [ch07-pg-specific.md](sql-skill/chapters/ch07-pg-specific.md) | JSONB / array / GIN / postgres_fdw / 中文 schema 雷区 | 322 |
| 8 | [ch08-indexes-perf.md](sql-skill/chapters/ch08-indexes-perf.md) | 索引结构 / WHERE 索引失效 / JOIN 算法 / 排序分组 / 分页窗口 / EXPLAIN ANALYZE | 405 |
| 9 | [ch09-antipatterns.md](sql-skill/chapters/ch09-antipatterns.md) | 反模式综合:建模 / 查询 / 索引 / NULL / 字符串日期 / 性能 / 安全 **7 类 25+** | 429 |
| 10 | [ch10-evidence-bridge.md](sql-skill/chapters/ch10-evidence-bridge.md) | SQL Agent 范式(MCP + 4 道防线)/ evidence-skill 协作 / 评测 | 337 |
| 11 | [ch11-multi-db.md](sql-skill/chapters/ch11-multi-db.md) | **多方言**:MySQL / Oracle / SQL Server 语义地雷 + 跨库协作 | 434 |

**辅助文件 ×5**(写 SQL 的第一站,不必翻章节):

| 文件 | 内容 | 何时读 |
|---|---|---|
| [supporting/cheatsheet.md](sql-skill/supporting/cheatsheet.md) | 13 张决策表 + 18 条关键经验 | **写 SQL / 排错第一站** |
| [supporting/glossary.md](sql-skill/supporting/glossary.md) | 166 条术语定义 | 查术语 |
| [supporting/patterns.md](sql-skill/supporting/patterns.md) | 8 大模式 + 反模式总表 | 套现成模式 |
| [references/topic-index.md](sql-skill/references/topic-index.md) | 99 个术语 → 章节定位 | 不知道读哪章 |
| [references/retrieval.md](sql-skill/references/retrieval.md) | 跨 vault 检索路径与优先级 | 要查 skill 外的资料 |

---

## 四、实测:不是宣称,是测出来的

### 4.1 知识覆盖率 —— 1090 题实战题库

用 [civilian7](https://github.com/) 的 **1090 道真实 SQL 题**(beginner / intermediate / advanced)做覆盖率评测:每道题按 `tags` + `metadata.concepts` + `type` + 标题正文 4 路匹配,看能不能定位到正确的章节。

```
python tools/eval_civilian7.py --mode skill-aware
# [OK] skill-aware: 100.0% coverage (1090/1090)
```

| 章节 | 覆盖题数 | | 章节 | 覆盖题数 |
|---|---:|---|---|---:|
| ch01 语法 | 918 | | ch06 集合操作 | 101 |
| ch05 聚合 | 468 | | ch09 反模式 | 59 |
| ch02 JOIN | 280 | | ch08 索引性能 | 44 |
| ch04 CTE | 267 | | ch03 窗口函数 | 245 |
| ch07 PG 特有 | 139 | | ch10/ch11 | 实战题库未覆盖 |

### 4.2 Baseline 自检 —— reference SQL 真能跑

拿题库自带的 reference SQL 在真实 SQLite(32 张电商表)上跑,验证**题库本身**可执行:

```
python tools/eval_civilian7.py --mode baseline --db <playground.db>
# [OK] baseline: 95.6% SQL 可执行 (282/300)
```

剩下的 5% 已分类:方言专属构造(`PROCEDURE` / `TRIGGER` / `DELIMITER`)、SQLite 不支持的 `GROUP_CONCAT(DISTINCT x, sep)`,以及**故意触发约束违例**的题(那批题的目的就是演示报错)。

### 4.3 执行准确率 A/B —— skill 到底帮上忙没有

让模型真的去答 SQL,把生成的 SQL 拿去 SQLite 执行,和 reference SQL 的**结果集**对拍(不是比字符串):

```bash
python tools/eval_civilian7.py --mode claude-api --db <playground.db> --api-sample 20 --seed 42 --context none
python tools/eval_civilian7.py --mode claude-api --db <playground.db> --api-sample 20 --seed 42 --context skill
```

固定 `--seed` 保证两轮抽到同一批题,否则 A/B 不可比。结果见 [`docs/audit/`](docs/audit/)。

---

## 五、快速开始

### 5.1 安装(3 步)

```bash
# 1. 克隆
git clone https://github.com/kizemo/sql-skill.git
cd sql-skill

# 2. 装到 Claude Code 全局 skills 目录
mkdir -p ~/.claude/skills/sql-skill
cp -r sql-skill/* ~/.claude/skills/sql-skill/

# 3. 验证
ls ~/.claude/skills/sql-skill/
# SKILL.md  chapters/  supporting/  references/
```

Claude Code 会自动发现 `SKILL.md` 并按 `description` + `triggers` 路由。**不需要任何 API key、不需要 pip install、不需要起服务** —— 纯 markdown + 标准库 Python。

### 5.2 验证

直接问:

> 「大 OFFSET 分页怎么优化」

预期行为:先查 `cheatsheet.md` 决策表 → 命中 [ch08 §5](sql-skill/chapters/ch08-indexes-perf.md) → 给出 keyset 分页 `WHERE id > last_id LIMIT N`,并说明 OFFSET 的代价随 offset 线性增长。

### 5.3 可选:接 Obsidian vault / gbrain

| 场景 | 做法 |
|---|---|
| 想用 Obsidian 检索 | `cp -r sql-skill/ E:/obsidian/SQL/08-sql-skill/` |
| 想用 gbrain semantic recall | 见 [`docs/DEPLOY.md`](docs/DEPLOY.md) |

---

## 六、知识同步:4 通道

知识写完会过期。`sql-skill` 的知识可以来自 Claude 写、Obsidian 改、批量导入,所以做了 4 条通道:

```
Claude 写 .md ──► A. PostToolUse hook ──► gbrain put_page   (≈1s,即写即同步)
Obsidian 外部改 ─► B. Cron 每日 02:00 ──► gbrain sweep
Session 启动 ─────► C. 消费 queue ─────► gbrain put_page    (兜底)
人工/批量 ────────► D. Manual ─────────► gbrain put_page
```

| 通道 | 触发 | 用途 | 延迟 |
|---|---|---|---|
| **A. PostToolUse hook** | Claude 写 `.md` 到 vault | 主通道,写完即同步 | **≈1s** |
| **B. Cron** | 每日 02:00 | 同步 Obsidian app 的外部编辑 | ≤24h |
| **C. SessionStart** | 每次 Claude 启动 | 消费 A 遗留的 queue(兜底) | 启动时 |
| **D. Manual** | 用户主动 | 应急 / 批量 ingest / 调试 | 立即 |

通道 A 的实现(`tools/post-write-auto-sync.py`)是**三层降级**:

1. **MCP over HTTP** —— 内嵌最小 MCP 客户端(`initialize` → `notifications/initialized` → `tools/call put_page`),JSON 与 SSE 两种响应模式都支持
2. **gbrain CLI** —— `gbrain put <slug>` 走 stdin 传内容(章节 25KB+,命令行传参会撞 Windows 32KB 上限)
3. **queue 文件** —— 前两条都失败时兜底,**绝不丢内容**

---

## 七、与 evidence-skill 的边界

两个 skill 刻意不重叠,靠 ch10 固化边界:

| 主题 | 查 sql-skill | 查 evidence-skill |
|---|---|---|
| 通用语法 / 索引 / JOIN / 聚合 / 反模式 | ✅ ch01-ch11 | — |
| 多方言语义差异(MySQL / Oracle / SQL Server) | ✅ ch11 | — |
| Evidence BI 配置 / nginx / pgbouncer 部署 | ch08 §3/§6 引 | ✅ ch14 权威 |
| 中文 schema 假名映射明细(13+ page 清单) | ch07 §5 引 | ✅ ch05 权威 |
| postgres_fdw 完整 5 步部署 | ch07 §4 引 | ✅ ch07 权威 |
| MCP self-host 4 道防线部署细节 | ch09 §7 引 | ✅ ch16 权威 |

---

## 八、目录结构

```
sql-skill/
├── sql-skill/                        ← skill 本体(装进 ~/.claude/skills/ 的就是这一层)
│   ├── SKILL.md                      ← 入口:12 框架速查 + Gotchas + 章节索引(104 行)
│   ├── INDEX.md                      ← 资源索引
│   ├── chapters/                     ← 11 章正文(4,375 行)
│   └── supporting/                   ← cheatsheet / glossary / patterns
│   └── references/                   ← topic-index(99 术语)/ retrieval(检索规范)
│
├── tools/                            ← 同步与评测工具(仅标准库依赖)
│   ├── post-write-auto-sync.py       ← 通道 A:内嵌 MCP 客户端 + CLI 直写 + queue 兜底
│   ├── sync-queue-consumer.py        ← 通道 C:消费 queue
│   ├── cron-sync-sql-skill.sh        ← 通道 B:Cron 脚本
│   ├── register-cron-sync.ps1        ← 通道 B:注册 Windows 计划任务
│   └── eval_civilian7.py             ← 评测:count / skill-aware / baseline / claude-api
│
├── references/luke/                  ← Use The Index, Luke! 8 篇离线镜像(252K)
│
├── docs/                             ← 开发文档
│   ├── audit/                        ← token 成本 / validator 报告
│   ├── specs/ · plans/ · handoffs/   ← 各阶段设计、计划、交接
│   └── CHANGELOG.md
│
└── eval_civilian7_report.{json,md}   ← 最近一次评测报告
```

---

## 九、依赖与兼容性

| 依赖 | 版本 | 必需? | 用途 |
|---|---|---|---|
| Markdown 阅读器 | — | ✅ | 核心内容,无运行时依赖 |
| Python | 3.10+ | 同步/评测工具需要 | 仅标准库(`json` / `urllib` / `sqlite3`) |
| PostgreSQL | 14+ | 例子针对 | SQL 示例的基准方言 |
| Git Bash | 4.0+ | Cron 通道 | `cron-sync-sql-skill.sh` |
| PowerShell | 5.1+ | Cron 通道 | `register-cron-sync.ps1` |
| [gbrain](https://github.com/garrytan/gbrain) | 0.60+ | 可选 | semantic recall + 知识同步 |
| Anthropic API | — | 可选 | 仅 `--mode claude-api` 评测用 |

**知识来源**:[Use The Index, Luke!](https://use-the-index-luke.com/)(8 篇离线镜像)· [civilian7](https://github.com/) 1090 题 · [awesome-postgres](https://github.com/) · [SQL Style Guide](https://github.com/mattm/sql-style-guide)

---

## 十、贡献

```bash
git clone https://github.com/kizemo/sql-skill.git
cd sql-skill
# 编辑 sql-skill/chapters/*.md
python tools/eval_civilian7.py --mode skill-aware   # 改完跑一遍,覆盖率不能掉
git commit -m "ch08: 补充 BRIN 时序场景"
git push origin main
```

**新增章节 checklist**:

1. 复制模板 `cp sql-skill/chapters/ch09-antipatterns.md sql-skill/chapters/ch12-new-topic.md`
2. 保留 9 段结构
3. `sql-skill/SKILL.md` 的 Chapter Index 加一行
4. `sql-skill/references/topic-index.md` 补术语
5. `supporting/cheatsheet.md` 补关键经验
6. 跑 `eval_civilian7.py --mode skill-aware` 确认覆盖率不掉
7. 跑 skill-forge audit 确认 index 层没超 100 tok

---

## 十一、已知限制

1. **`sql-skill` 本身不解决 schema 幻觉** —— 表结构、列名、业务口径要靠上层连接上下文提供(evidence-skill / MCP)
2. **多方言只讲「与 PG 的差异」** —— 不教 MySQL / Oracle / SQL Server 入门
3. **gbrain embedding 默认关闭**(缺 `VOYAGE_API_KEY`)—— 只能 keyword 召回
4. **ch10 / ch11 在 civilian7 题库里没有对应用例** —— 那两章的覆盖靠人工评审,不是自动评测
5. **`references/luke/` 是 HTML 镜像** —— 上游更新后需要手动同步

---

## 十二、路线图

- [x] 10 章通用 SQL 知识 + 4 辅助文件
- [x] 4 通道知识同步
- [x] 渐进式披露重构(index 231→100 tok,load 5,503→2,005 tok)
- [x] 多方言章节(MySQL / Oracle / SQL Server)
- [x] hook 内嵌 MCP 客户端(即写即同步)
- [x] 1090 题自动评测 + 执行准确率 A/B
- [ ] gbrain embedding 启用(等 `VOYAGE_API_KEY`)
- [ ] ch10 / ch11 专项题库(补自动评测盲区)
- [ ] 更多方言(SQLite / ClickHouse)

---

## 十三、致谢

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/) —— 语法与行为的权威来源
- [Use The Index, Luke!](https://use-the-index-luke.com/) —— Markus Winand,索引与执行计划
- [Mark Mazur SQL Style Guide](https://github.com/mattm/sql-style-guide) —— 风格铁律
- [civilian7](https://github.com/) —— 1090 道实战题库
- [evidence-skill](https://github.com/kizemo/evidence-skill) —— 业务侧互补
- [gbrain](https://github.com/garrytan/gbrain) —— semantic RAG 与知识同步基础设施
- [skill-optimizer](https://github.com/kizemo/skill-optimizer) —— token 成本审计与 validator

---

**License**: [MIT](LICENSE) · **Maintainer**: [kizemo](https://github.com/kizemo) · **Repo**: https://github.com/kizemo/sql-skill
