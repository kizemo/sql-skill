# sql-skill v1.0 — 完整版交付 handoff

> 交付日期: 2026-10-14
> 当前阶段: **sql-skill v1.0 完成**(Phase 2 + 3a + 3b + 3c 4 阶段沉淀)
> 沉淀位置: `E:/obsidian/SQL/08-sql-skill/`
> 形态: 10 章完整 + 4 辅助文件 / 总行数 ~3700
> 用途: 让 Claude/OpenClaw agent 写更专业、更准确的 SQL,通用 PostgreSQL 视角

---

## 一、v1.0 项目总览

### 1.1 sql-skill v1.0 完整版

**10 章 + 4 辅助文件 / 总行数 ~3700**

| # | 章节 | 行数 | 阶段 | 主题 |
|---|---|---|---|---|
| 1 | ch01-grammar.md | 256 | Phase 2 | SQL 语法铁律(8 子句执行顺序 / 别名 / NULL / 风格) |
| 2 | ch02-joins.md | 450 | Phase 3b | JOIN 7 种 + 性能差异 |
| 3 | ch03-window-functions.md | 488 | Phase 3b | 窗口函数(OVER / PARTITION BY / RANK / 帧) |
| 4 | ch04-cte-recursion.md | 454 | Phase 3b | CTE / 递归 CTE / 物化 |
| 5 | ch05-aggregates.md | 448 | Phase 3b | 聚合 / GROUP BY / HAVING / FILTER |
| 6 | ch06-set-ops.md | 352 | Phase 3c | 集合操作(UNION / INTERSECT / EXCEPT) |
| 7 | ch07-pg-specific.md | 322 | Phase 2 | PostgreSQL 特有(JSONB / array / GIN / FDW) |
| 8 | ch08-indexes-perf.md | 405 | Phase 2 | 索引与性能(B-Tree / GIN / JOIN 算法 / EXPLAIN) |
| 9 | ch09-antipatterns.md | 429 | Phase 3a | SQL 反模式综合(7 类 25+ 反模式) |
| 10 | ch10-evidence-bridge.md | 314 | Phase 3c | SQL Agent 范式 + evidence-skill 协作 |
| — | **10 章合计** | **3918** | — | — |
| 辅 | SKILL.md | 入口 + 12 framework | Phase 3c 更新 | 12 大 framework + Chapter Index + Topic Index |
| 辅 | glossary.md | 关键术语 | Phase 3c 更新 | 按字母 / 中文术语分组 |
| 辅 | patterns.md | 8 模式 + 反模式总表 | Phase 3c 更新 | 60+ 反模式 |
| 辅 | cheatsheet.md | 13 决策表 + 18 关键经验 | Phase 3c 更新 | 一页纸决策快查 |

### 1.2 与 evidence-skill 互补关系(已固化边界)

| Skill | 覆盖 | 状态 |
|---|---|---|
| **sql-skill**(本项目) | 通用 SQL 知识(语法 / 性能 / 反模式 / PG 特性)— 10 章 | v1.0 完成 |
| evidence-skill | 业务落地知识(Evidence BI / 中文 PG schema / nginx / FDW / MCP)— 18 章 | 已部署 |
| 联动 | sql-skill ch02-09 + evidence-skill ch05/ch07/ch14/ch16 互补 | — |

**核心边界铁律**(沿用 Phase 2/3a/3b/3c,不可破坏):
- sql-skill ch02 不写 nginx immutable / pgbouncer session-mode(归 evidence-skill ch14)
- sql-skill ch02 不重写 postgres_fdw 完整 5 步 SQL(归 evidence-skill ch07,只引简化版 + 引用)
- sql-skill ch02 不重写中文列双引号细节(归 evidence-skill ch05,只提通用)
- sql-skill ch10 不重写 evidence-skill 18 章内容,只引 + 协作范式
- 各 chapter 不重复其他 chapter 已写内容,只引用

### 1.3 用户技术栈

- **数据库**:企业 PostgreSQL(中文 schema,列名如 `"店铺"` `"订单日期"`)
- **BI 工具**:Evidence BI (Core 2026,生产在跑)
- **Agent 平台**:Claude Code / OpenClaw(已装 evidence-skill 自建 skill)
- **凭据**:环境变量管理(CLAUDE.md 硬编码红线)

---

## 二、必读顺序(新会话 / 新 agent)

按业务流顺序读,3-5 分钟掌握全貌:

```
ch01(语法铁律) → ch02(JOIN) → ch03(窗口) → ch04(CTE) → ch05(聚合) → ch06(集合)
  → ch07(PG 特有) → ch08(索引性能) → ch09(反模式) → ch10(协作范式)
```

**写 SQL / 排错 / 调性能三层 lookup 顺序**:
1. **cheatsheet.md**(13 决策表 + 18 关键经验)— 第一查
2. **对应 chapter**(ch01-ch10)— 针对性 deep dive
3. **evidence-skill 业务侧**(ch05 中文 schema / ch07 FDW / ch14 BI 性能 / ch16 MCP)— 业务落地

---

## 三、调研入口(本地资源 / 联动 skill)

### 3.1 本地资源

| 资源 | 路径 | 用途 |
|---|---|---|
| 资源总索引 | `E:/obsidian/SQL/00-索引.md` | 7 个沉淀目录入口 |
| luke 48 章 | `E:/obsidian/SQL/03-use-the-index-luke/` | 索引圣经 |
| pg-docs 5 章 | `E:/obsidian/SQL/03-use-the-index-luke/pg-docs/` | PG 官方文档 |
| SQLBolt 17 课 | `E:/obsidian/SQL/03-use-the-index-luke/sqlbolt/` | 互动教程 |
| civilian7 1065 题 | `E:/obsidian/SQL/02-sql-tutorial-civilian7/` | SQL 评测题库 |
| nl2sql-handbook 综述 | `E:/obsidian/SQL/01-nl2sql-handbook/`(199M) | NL2SQL 综述 |
| awesome-postgres | `E:/obsidian/SQL/04-awesome-postgres/` | PG 资源汇总 |
| sql-style-guide | `E:/obsidian/SQL/05-sql-style-guide/` | SQL 风格指南 |

### 3.2 联动 skill

| Skill | 路径 | 用途 |
|---|---|---|
| evidence-skill(BI / 中文 PG / FDW / nginx / MCP) | `E:/Users/Duanyi/.claude/skills/evidence-skill/` | 业务侧权威 |
| 调研笔记 | `F:/soft/00selfmade/sql-skill/_knowledge_base/research-github-sql-agent-20261013.md` | 调研笔记 |
| Phase 2 spec/plan/handoff | `F:/soft/00selfmade/sql-skill/docs/superpowers/` + `handoff-sql-skill-phase2-*.md` | Phase 2 沉淀 |
| Phase 3a spec/plan/handoff | `F:/soft/00selfmade/sql-skill/docs/superpowers/` + `handoff-sql-skill-phase3a-*.md` | Phase 3a 沉淀 |
| Phase 3b spec/plan/handoff | `F:/soft/00selfmade/sql-skill/docs/superpowers/` + `handoff-sql-skill-phase3b-*.md` | Phase 3b 沉淀 |
| Phase 3c spec/plan/handoff | `F:/soft/00selfmade/sql-skill/docs/superpowers/` + `handoff-sql-skill-phase3c-*.md` | Phase 3c 沉淀 |
| **v1.0 handoff(本次)** | `F:/soft/00selfmade/sql-skill/handoff-sql-skill-v1-2026-10-14.md` | — |

---

## 四、维护建议

### 4.1 PG 大版本升级时

- re-read luke `sql-anatomy-*` + pg-docs `indexes.html` + `performance-tips.html`
- 看新特性(GIN 改进 / BRIN 优化 / MERGE / partitioning 改进)
- 更新 ch08(ch08 §1 索引结构)

### 4.2 每月

- 跑 `ANALYZE` 所有大表,统计信息新鲜
- 看 `pg_stat_statements` top-20 慢 query
- 更新 cheatsheet 决策表(如有新反模式)

### 4.3 每季

- review 一次索引决策(B-Tree / GIN / BRIN / Hash 是否仍最优)
- 跑一次 `pg_stat_user_indexes.idx_scan = 0` 找无用索引,谨慎 `DROP INDEX CONCURRENTLY`
- review evidence-skill 18 章边界(避免重叠)

### 4.4 半年

- review 与 evidence-skill 边界(避免重叠)
- 跑 civilian7 1065 题验证(Phase 4+ 自动化)
- update cheatsheet 关键经验(累积实战经验)

### 4.5 升级 / 修改 skill 时

- 修改 chapter 前先读 handoff 必读顺序,避免破坏 9 段结构
- 新增 chapter 必含 9 段(可拆 "(续)" 段但不能省)
- 更新辅助文件前 grep 引用,确保 cross-ref 不断链
- 严格遵守 CLAUDE.md 红线(禁 rm / 禁 DROP / 禁危险 SQL)

---

## 五、未来扩展(Phase 4+ 建议)

### 5.1 自动化评测(短期)

- civilian7 1065 题自动化跑(基于 ch10 §5)
- 评测 SQL 生成质量 + 反模式命中率
- 集成 CI / hook(可选)

### 5.2 联动 evidence-skill 测试(中期)

- sql-skill ch10 + evidence-skill ch16 联动测试
- 中文 schema 假名修复 + 4 道防线端到端验证
- 跑 `pg_stat_statements` 慢 query 真实样本

### 5.3 多 DB 支持(长期)

- MySQL 8.x(`SHOW PROCESSLIST` / `EXPLAIN` 差异)
- Oracle 19c(`DBA_*` 视图 / `EXPLAIN PLAN` 差异)
- SQL Server 2019(`sys.dm_exec_*` 视图差异)
- SQLite 3.x(嵌入式 / 简化语法)

### 5.4 新 chapter 拓展(可选)

- ch11 Query Optimizer 内部(成本估算 / 统计信息)
- ch12 事务 / 隔离级别(MVCC / 锁 / 死锁)
- ch13 复制 / 高可用(replication / failover)
- ch14 时序数据 TimescaleDB / Citus 扩展

---

## 六、v1.0 完成状态总结

### 6.1 已完成

- ✅ Phase 2:ch01 + ch07 + ch08 + 4 辅助文件(v0.1 沉淀)
- ✅ Phase 3a:ch09 反模式综合(429 行)
- ✅ Phase 3b:ch02 JOIN + ch03 窗口 + ch04 CTE + ch05 聚合(1840 行)
- ✅ Phase 3c:ch06 集合 + ch10 evidence-bridge(666 行)
- ✅ 4 辅助文件全程同步更新(SKILL.md / glossary.md / patterns.md / cheatsheet.md)
- ✅ 4 个 handoff 文档(Phase 2 / 3a / 3b / 3c + v1.0)
- ✅ 4 个 spec/plan 文档(superpowers/specs + plans)

### 6.2 量化指标

- **总行数**:3918(chapters)+ 4 辅助文件(累计 ~4500-5000)
- **chapter 9 段结构**:10/10 章节齐全
- **Frameworks 累计**:10 章 ~ 100+ 铁律
- **Anti-patterns 累计**:10 章 ~ 80+ 反模式
- **不重叠矩阵**:每章 Connects To 段固定列 cross-ref
- **辅助文件引用**:ch01-ch10 全部 grep 命中

### 6.3 不做的事(明确边界)

- ❌ 不实现评测集自动化(Phase 4+)
- ❌ 不重写 evidence-skill 18 章
- ❌ 不重复 ch01-ch09 已写内容
- ❌ 不修改 evidence-skill(独立 skill)
- ❌ MySQL / Oracle / SQL Server / SQLite 多 DB 支持(Phase 4+)

---

## 七、环境/基线状态

| 项 | 状态 |
|---|---|
| 工作目录 | `F:/soft/00selfmade/sql-skill/` |
| Git 仓库 | **未 init** |
| sql-skill v1.0 | **10 章完整 + 4 辅助文件** |
| 主沉淀 | `E:/obsidian/SQL/08-sql-skill/` (3918 行 chapters + 4 辅助文件) |
| evidence-skill | `E:/Users/Duanyi/.claude/skills/evidence-skill/` (18 章) |
| spec/plan 文档 | `F:/soft/00selfmade/sql-skill/docs/superpowers/` (8 文件) |
| handoff 文档 | `F:/soft/00selfmade/sql-skill/handoff-sql-skill-*.md` (5 文件) |

---

## 八、v1.0 关键决策沉淀(沿用各 phase)

### Phase 2 决策

1. ch01 8 子句执行顺序铁律
2. NULL 三值逻辑铁律
3. 风格铁律(关键字大写 / snake_case / 显式 AS / 2 空格缩进)

### Phase 3a 决策(ch09)

1. ch09 7 节细分(数据建模 / 查询 / 索引 / NULL / 字符串日期 / 性能 / 安全)
2. ch09 Frameworks 63 条 + Anti-patterns 21 条
3. ch09 行数 429(略超 ch08 405,但内容质量优先)

### Phase 3b 决策(ch02-ch05)

1. ch02 7 节细分(INNER / OUTER / CROSS / SELF / NATURAL / JOIN 算法 / 反模式)
2. ch02 Frameworks 14+ / ch03 15+ / ch04 10+ / ch05 15+ 铁律
3. ch02 450 / ch03 488 / ch04 454 / ch05 448 行(对齐 ch09 429,深度优先)
4. 不重写 ch08 §3 JOIN 算法 / ch09 §2 隐式 JOIN / ch09 §6 N+1

### Phase 3c 决策(ch06/ch10)

1. ch06 6 节细分(UNION / INTERSECT / EXCEPT / JOIN 转换 / ORDER BY-LIMIT / 反模式)
2. ch10 6 节细分(边界 / SQL Agent 范式 / 中文 schema / BI 性能 / 评测集 / v1.0 沉淀)
3. ch10 不重写 evidence-skill 18 章,只引 + 协作范式
4. 三层 lookup 顺序固定(cheatsheet → chapter → evidence-skill)

### 全局决策

1. **9 段结构固定**:每 chapter 必含 9 段,可拆 "(续)" 段
2. **不重叠矩阵**:每章 Connects To 段固定列 cross-ref 到其他 chapter + evidence-skill
3. **CLAUDE.md 红线**:禁 rm / 禁 DROP / 禁危险 SQL / 临时文件 `C:\Temp\`
4. **单次 Write ≤ 400 行 / 8000 tokens**(避 120s abort)

---

## 九、致谢与历史

- Phase 2(2026-10-14):v0.1 沉淀(3 章 + 4 辅助文件,沿用 ch01/ch07/ch08 三章)
- Phase 3a(2026-10-14):ch09 反模式综合 429 行
- Phase 3b(2026-10-14):ch02-ch05 1840 行
- Phase 3c(2026-10-14):ch06/ch10 666 行,v1.0 完整版 3918 行

**核心贡献**:
- 沉淀了 sql-skill 与 evidence-skill 严格互补的边界
- 9 段结构 + 不重叠矩阵 + Connects To 强制 cross-ref
- 三层 lookup 顺序 + 4 道防线纵深防御
- civilian7 1065 题 + cheatsheet 决策表 + 关键经验

---

**v1.0 完整版交付完成,sql-skill 从 v0.1 3 章扩展到 v1.0 10 章,通用 PostgreSQL 视角,PostgreSQL + Evidence BI 企业场景覆盖完整。**

**未来 Phase 4+(评测 / 自动化 / 多 DB)是 sql-skill v2.0 演进方向。**