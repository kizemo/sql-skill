# sql-skill Phase 3 — 设计 spec

**Date**: 2026-10-14
**Phase**: Phase 2 完成 / Phase 3 设计阶段
**Owner**: claude (this session)
**Status**: 待用户 review

---

## 一、设计背景与上下文

### 1.1 Phase 2 完成状态

sql-skill v0.1 沉淀完毕,7 个 markdown 文件 / 1839 行 / 92KB:
- `SKILL.md` 261 行 + `glossary.md` 158 行 + `patterns.md` 247 行 + `cheatsheet.md` 190 行
- `chapters/ch01-grammar.md` 256 行 + `chapters/ch07-pg-specific.md` 322 行 + `chapters/ch08-indexes-perf.md` 405 行

### 1.2 Phase 3 必交付

把 ch02 / ch03 / ch04 / ch05 / ch06 / ch09 / ch10 共 **7 个 stub → 完整 9 段章节**,让 sql-skill v1.0 完整覆盖 10 章。

### 1.3 关键约束(CLAUDE.md 红线,沿用 Phase 2)

- ❌ 禁止 rm / Remove-Item / del 任何文件
- ❌ 禁止 git reset --hard / git clean -fd / git checkout --
- ❌ 禁止 DROP / TRUNCATE / DELETE FROM 不带 WHERE
- ❌ 禁止在 E:/obsidian/SQL/ 文件名用 \ / : * ? " < > | 或 emoji
- ✅ 临时文件写 C:\Temp\,不要写 ~/.tmp/
- ✅ 单次 Write ≤ 400 行 / 8000 tokens(避 120s abort)

---

## 二、Phase 3 必交付清单

### 2.1 7 个 chapter 文件输出位置

| 路径 | 用途 |
|---|---|
| `E:/obsidian/SQL/08-sql-skill/chapters/ch02-joins.md` | JOIN 7 种 + 性能差异 |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch03-window-functions.md` | 窗口函数(OVER/PARTITION BY/RANK/lead-lag) |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch04-cte-recursion.md` | CTE / 递归 CTE / 物化 |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch05-aggregates.md` | 聚合 / GROUP BY / HAVING / FILTER |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch06-set-ops.md` | 集合操作(UNION/INTERSECT/EXCEPT) |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch09-antipatterns.md` | **第一个**(priority 1,深度 ~350 行) |
| `E:/obsidian/SQL/08-sql-skill/chapters/ch10-evidence-bridge.md` | 与 evidence-skill 协作 / 范式 |

### 2.2 辅助文件更新

| 路径 | 更新 |
|---|---|
| `E:/obsidian/SQL/08-sql-skill/SKILL.md` | Chapter Index 把 🔵 stub → ✅ 完整 |
| `E:/obsidian/SQL/08-sql-skill/glossary.md` | 新 chapter 的 Key Concepts 词汇加入 |
| `E:/obsidian/SQL/08-sql-skill/patterns.md` | 新 chapter 的 Frameworks + Anti-patterns 收入反模式总表 |
| `E:/obsidian/SQL/08-sql-skill/cheatsheet.md` | 新 chapter 决策表 + 12 关键经验追加 |

### 2.3 9 段结构(对齐 Phase 2)

每 chapter 固定含:
```
Core Idea / Frameworks Introduced / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To
```

---

## 三、Phase 3 推进策略(用户已对齐)

### 3.1 整体策略:subagent 并行(用户选择)

按用户对齐:
- **整体 7 章并行化**:3 批 subagent + 1 收尾 subagent,每 subagent 上下文独立
- **本次会话只启动 ch09 subagent**(Phase 3 第一个 chapter),其余 6 章留 Phase 3 后续会话接力

### 3.2 3 批 subagent 划分

| 批 | chapter | 难度 | 评估 |
|---|---|---|---|
| Phase 3a | ch09 + ch03 | 中-高 | ch09 反模式综合(civilian7 1065 题筛选),ch03 窗口函数 luke + civilian7 |
| Phase 3b | ch02 + ch04 + ch05 | 中 | JOIN 7 种 + CTE + 聚合,SQLBolt + luke + civilian7 三源 |
| Phase 3c | ch06 + ch10 | 低 | ch06 集合操作简单,ch10 协作范式与 evidence-skill 全 18 章联动 |

### 3.3 本次会话范围

- ✅ 写 ch09 反模式完整 9 段(~350 行)
- ✅ Update SKILL.md Chapter Index(ch09: 🔵 stub → ✅ 完整)
- ✅ Update glossary.md(ch09 Key Concepts 词汇)
- ✅ Update patterns.md(ch09 Frameworks + 反模式总表)
- ✅ Update cheatsheet.md(新增 ch09 决策表 + 关键经验)
- ✅ 写 handoff 给 Phase 3b 接力
- ❌ ch02 / ch03 / ch04 / ch05 / ch06 / ch10 留 Phase 3b 接力

---

## 四、ch09 反模式详细设计

### 4.1 ch09 主题与子结构

**SQL 反模式综合**(25+ 模式,从 civilian7 1065 题筛选 + evidence-skill ch05 联动)

| 节 | 主题 | 主要素材 |
|---|---|---|
| § 1 | 数据建模反模式(EAV / 实体属性值) | civilian7 + SQL Antipatterns 经典 |
| § 2 | 查询编写反模式(SELECT * / 隐式 JOIN) | civilian7 + evidence-skill ch05 |
| § 3 | 索引使用反模式(过度索引 / 无用索引) | civilian7 + ch08 §1 |
| § 4 | NULL 处理反模式(NULL 拼接 / NULL 聚合) | civilian7 + ch01 §3 |
| § 5 | 字符串 / 日期反模式(隐式 cast / date SUBSTR) | civilian7 + ch07 §5 + evidence-skill ch05 |
| § 6 | 性能反模式(N+1 / 大 OFFSET / 函数索引失效) | civilian7 + ch08 §2/§3/§5 |
| § 7 | 安全反模式(SQL 注入 / 字符串拼接 query) | civilian7 + evidence-skill ch16 MCP 防线 |

### 4.2 ch09 关键铁律(预估 18+ 条)

每节 2-3 条,共 18+ 条铁律。

### 4.3 ch09 反模式列表(目标 25+ 条)

每节 3-5 条反模式 + ✅ 修法,共 25+ 条。

### 4.4 ch09 与 evidence-skill ch05 联动

- evidence-skill ch05 业务侧 13+ page 假名清单(权威)
- ch09 提供通用反模式铁律
- ch09 §5 引用 evidence-skill ch05 作为"中文 PG schema 业务侧权威"

---

## 五、Phase 3a ch09 命名规范与形态

### 5.1 文件名

- 编号 `ch09` + 英文短词 `antipatterns`
- 不带 emoji、不带空格、不带 Windows 禁用字符
- 完整路径 `E:/obsidian/SQL/08-sql-skill/chapters/ch09-antipatterns.md`

### 5.2 深度目标

对齐 Phase 2:
- ch09 主体 ~350 行(反模式最多,比 ch08 略少)
- Frameworks 18+ 条
- Anti-patterns 25+ 条
- Code Examples 7 节齐全
- Reference Tables 7 节齐全

### 5.3 跨引用规则

- 章节引用 `ch0X`,evidence-skill 引用 `evidence-skill ch0X`,luke 引用 `luke/<file>.html`,civilian7 引用 `civilian7/<path>`
- 引用时如 evidence-skill 已有权威,走 evidence-skill;否则 ch09 自己写

---

## 六、Phase 3a ch09 验收清单

### 6.1 文件存在性

- [ ] `E:/obsidian/SQL/08-sql-skill/chapters/ch09-antipatterns.md`(350 行左右)
- [ ] `E:/obsidian/SQL/08-sql-skill/SKILL.md`(Chapter Index 更新,ch09: 🔵 stub → ✅ 完整)
- [ ] `E:/obsidian/SQL/08-sql-skill/glossary.md`(新增 ch09 Key Concepts 词汇)
- [ ] `E:/obsidian/SQL/08-sql-skill/patterns.md`(新增 ch09 反模式到总表)
- [ ] `E:/obsidian/SQL/08-sql-skill/cheatsheet.md`(新增 ch09 决策表 + 关键经验)

### 6.2 形态对齐

- [ ] ch09 9 段齐全(grep 验证)
- [ ] Frameworks 18+ 条
- [ ] Anti-patterns 25+ 条
- [ ] Code Examples 7 节齐全
- [ ] Reference Tables ≥ 7 张

### 6.3 与 Phase 2 兼容

- [ ] 不重复 ch01/ch07/ch08 已写铁律(只引用,不在 ch09 重写)
- [ ] 与 evidence-skill ch05/ch14 边界清晰
- [ ] 与其他 6 个 stub chapter 不重叠

### 6.4 沉淀入口

- [ ] SKILL.md "调研 / 沉淀入口" 段加 ch09 链接
- [ ] cheatsheet § 13 加 ch09 链接
- [ ] handoff-sql-skill-phase3a-2026-10-14.md 给 Phase 3b 接力

---

## 七、Phase 3a 不做的事(明确边界)

- ❌ 不实现 Phase 3b / 3c 的 ch02 / ch03 / ch04 / ch05 / ch06 / ch10(留后续会话接力)
- ❌ 不写评测集 / 联动测试(Phase 4+)
- ❌ 不重复 Phase 2 内容
- ❌ 不修改 evidence-skill(独立 skill,边界清晰)
- ❌ 不重写 civilian7 1065 题筛选机制(只引用权威)

---

## 八、风险与避坑

| 风险 | 避坑 |
|---|---|
| Write 工具调用 >120s abort | ch09 350 行分 7 次 Write(每节 ≤ 50 行),先骨架后 Edit 补内容 |
| 反模式重复 evidence-skill ch05 | § 4.4 联动规则 + 验收清单 6.3 |
| civilian7 引用无源 | 引用具体路径 `civilian7/exercises/beginner/...` 而非"来自 civilian7" |
| 跨章引用断链 | Connects To 段固定列 cross-ref |

---

## 九、下一步(用户 approve 后)

1. **invocation `superpowers:writing-plans`** 写 Phase 3a 实施计划
2. 计划包含:ch09 7 节具体 task + 4 辅助文件更新 task + verification task + handoff task
3. 计划批准后:实施 ch09 7 节(每节 1 task) + 4 辅助文件 + verification + handoff
4. 每章完成前:`superpowers:verification-before-completion`

---

**Spec 写完,等待用户 review。**
