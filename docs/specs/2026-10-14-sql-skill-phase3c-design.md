# sql-skill Phase 3c — 设计 spec

**Date**: 2026-10-14
**Phase**: Phase 3a + 3b 完成 / Phase 3c 设计阶段
**Owner**: claude (this session)
**Status**: 用户已对齐,待 Plan 撰写后立即执行

---

## 一、设计背景

### 1.1 Phase 3a + 3b 已完成

- `chapters/ch09-antipatterns.md` 429 行(Phase 3a)
- `chapters/ch02-joins.md` 450 行 / `ch03-window-functions.md` 488 行 / `ch04-cte-recursion.md` 454 行 / `ch05-aggregates.md` 448 行(Phase 3b)
- 4 辅助文件已同步更新(SKILL.md / glossary.md / patterns.md / cheatsheet.md)
- handoff Phase 3b 已交付
- **合计 8 章完整 + 4 辅助文件 / 总行数 ~3252**

### 1.2 Phase 3c 必交付 — sql-skill v1.0 完整版

把 ch06 / ch10 共 **2 个 stub → 完整 9 段章节**,让 sql-skill v1.0 完整覆盖 10 章:

| chapter | 主题 | 深度 |
|---|---|---|
| ch06 | 集合操作(UNION/INTERSECT/EXCEPT) | ~150-200 行 |
| ch10 | 与 evidence-skill 协作 / 范式 / 评测 | ~250 行 |

合计 2 chapter ~400-450 行 + 4 辅助文件更新 + handoff v1.0。

### 1.3 关键约束(CLAUDE.md 红线,沿用 Phase 2/3a/3b)

- ❌ 禁 rm / Remove-Item / del / Move-Item 任何文件
- ❌ 禁 git reset --hard / git clean -fd / git checkout --
- ❌ 禁 DROP / TRUNCATE / DELETE FROM 不带 WHERE
- ❌ 禁文件名用 \ / : * ? " < > |
- ✅ 临时文件写 C:\Temp\,不写 ~/.tmp/
- ✅ 单次 Write ≤ 400 行 / 8000 tokens(避 120s abort)
- ✅ Edit 用锚定 old_string 追加

---

## 二、不重叠铁律(沿用 Phase 2/3a/3b)

### 2.1 不重叠矩阵

| 主题 | 已写章节 | ch06/ch10 处理 |
|---|---|---|
| JOIN 7 种 | ch02 | ch06 §4 引用,UNION vs JOIN 等价场景 |
| SELECT * 反模式 | ch09 §2 | ch06 §6 引用 |
| 窗口函数 | ch03 | ch10 §5 评测引用 |
| 聚合 / GROUP BY | ch05 | ch06 §2 INTERSECT 引用 |
| 中文 schema | evidence-skill ch05 | ch10 §3 引用 |
| BI 场景性能 | evidence-skill ch14 | ch10 §4 引用 |
| FDW 5 步 | evidence-skill ch07 | ch10 §2 引用 |
| MCP 4 道防线 | evidence-skill ch16 + ch09 §7 | ch10 §2 引用 |

### 2.2 9 段结构固定

每 chapter 必含 9 段:Core Idea / Frameworks Introduced / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To。

ch06/ch10 内容较少,**不必拆 "(续)" 段**。

---

## 三、ch06 集合操作详细设计(第一个 chapter)

### 3.1 主题与子结构

**集合操作(UNION / INTERSECT / EXCEPT)**

| 节 | 主题 | 主要素材 |
|---|---|---|
| § 1 | UNION / UNION ALL(合并去重 / 保留重复) | SQLBolt + civilian7 |
| § 2 | INTERSECT(交集,自动去重) | civilian7 |
| § 3 | EXCEPT(差集,自动去重) | civilian7 |
| § 4 | 集合操作与 JOIN 转换(等价表达) | civilian7 |
| § 5 | 集合操作 + ORDER BY / LIMIT(顶层 vs 子查询) | PG docs |
| § 6 | 集合操作反模式(列数类型不匹配 / ORDER BY 误用) | civilian7 + ch09 |

### 3.2 ch06 关键铁律(目标 8+ 条)

每节 1-2 条,共 8+ 条铁律。

### 3.3 ch06 反模式(目标 6+ 条)

每节 1-2 条,共 6+ 条反模式(与 ch09 互补,不重复)。

### 3.4 ch06 跨引用(必须)

- **→ sql-skill ch02 JOIN 7 种**:ch06 §4 引用,UNION vs JOIN 等价场景
- **→ sql-skill ch09 §2 SELECT * 反模式**:ch06 §6 引用,集合操作必须 explicit columns
- **→ sql-skill ch05 聚合 / GROUP BY**:ch06 §2 INTERSECT 引用与 HAVING 区分

---

## 四、ch10 evidence-bridge 详细设计

### 4.1 主题与子结构

**与 evidence-skill 协作 / 范式 / 评测**

| 节 | 主题 |
|---|---|
| § 1 | sql-skill 与 evidence-skill 边界(已固化) |
| § 2 | SQL Agent 范式(MCP + 4 道防线,详 evidence-skill ch16) |
| § 3 | 中文 schema 假名修复流程(详 evidence-skill ch05) |
| § 4 | BI 场景性能与 Core 28 page(详 evidence-skill ch14) |
| § 5 | 评测集(沿用 civilian7 1065 题) |
| § 6 | sql-skill v1.0 沉淀清单 |

### 4.2 ch10 关键铁律(目标 6+ 条)

### 4.3 ch10 反模式(目标 4+ 条)

### 4.4 ch10 跨引用(必须)

- **→ evidence-skill ch05**:中文 schema 业务侧权威
- **→ evidence-skill ch07**:postgres_fdw 跨 DB
- **→ evidence-skill ch14**:BI 场景性能
- **→ evidence-skill ch16**:MCP self-host 4 道 SQL 防线

---

## 五、辅助文件更新

| 路径 | 更新 |
|---|---|
| `E:/obsidian/SQL/08-sql-skill/SKILL.md` | Chapter Index 把 ch06 / ch10 `🔵 stub` → `✅` 完整 + Topic Index + Supporting Files + 调研入口 |
| `E:/obsidian/SQL/08-sql-skill/glossary.md` | 新增 ch06 / ch10 Key Concepts 词条 |
| `E:/obsidian/SQL/08-sql-skill/patterns.md` | 反模式总表追加 ch06 / ch10 反模式 |
| `E:/obsidian/SQL/08-sql-skill/cheatsheet.md` | 新增 ch06 / ch10 决策表 + 关键经验追加 |

---

## 六、v1.0 handoff 必交付清单

`handoff-sql-skill-v1-2026-10-14.md` 内容:

1. **项目总览**:v1.0 完成 10 章 + 4 辅助文件 / 总行数 / 与 evidence-skill 边界
2. **必读顺序**:ch01 → ch05 → ch07 → ch08 → ch09 → ch06 → ch10(按业务流)
3. **调研入口**:luke 48 章 + civilian7 1065 题 + nl2sql-handbook + evidence-skill 18 章
4. **维护建议**:PG 大版本升级 / 季度 review / 评测集更新
5. **未来扩展**:Phase 4+(评测 / 自动化测试 / 多 DB 支持)

---

## 七、验收清单

- [ ] ch06/ch10 2 文件存在 + 9 段齐全
- [ ] ch06 150-200 行 / ch10 250 行
- [ ] ch06 Frameworks 8+ / Anti-patterns 6+
- [ ] ch10 Frameworks 6+ / Anti-patterns 4+
- [ ] 不重叠 ch01-ch05/ch07-ch09 已写内容
- [ ] ch10 不重写 evidence-skill 18 章,只引用
- [ ] SKILL.md Chapter Index ch06/ch10 `🔵 stub` → `✅`
- [ ] glossary.md 新增 ≥ 8 词条
- [ ] patterns.md 反模式 ≥ 8 条
- [ ] cheatsheet.md 关键经验 ≥ 18 条
- [ ] handoff-sql-skill-v1-2026-10-14.md 已写

---

## 八、不做的事(明确边界)

- ❌ ch06/ch10 留 Phase 3c 接力(本次完成)
- ❌ 不实现评测集 / 联动测试(Phase 4+)
- ❌ 不重复 Phase 2 + 3a + 3b 内容
- ❌ 不修改 evidence-skill
- ❌ ch10 不重写 evidence-skill 18 章内容,只引 + 协作范式

---

## 九、下一步

1. ✅ 用户已对齐 + 已选 Native 执行(沿用 Phase 3a/3b 模式)
2. invocation **`superpowers:writing-plans`** 写 Phase 3c 实施计划
3. 计划批准后:Native 执行 2 chapter + 4 辅助文件 + verification + handoff v1.0
4. 每章完成前:`superpowers:verification-before-completion`