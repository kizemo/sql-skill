# sql-skill Phase 3b — 设计 spec

**Date**: 2026-10-14
**Phase**: Phase 3a 完成 / Phase 3b 设计阶段
**Owner**: claude (this session)
**Status**: 用户已对齐,待 Plan 撰写后立即执行

---

## 一、设计背景

### 1.1 Phase 3a 已完成

- `chapters/ch09-antipatterns.md` 429 行 / Frameworks 63 条 / Anti-patterns 21 条 / 25+ SQL 反模式综合(沿用 SQLBolt + luke + civilian7 + evidence-skill 联动)
- 4 辅助文件已同步更新(SKILL.md / glossary.md / patterns.md / cheatsheet.md)
- handoff Phase 3a 已交付

### 1.2 Phase 3b 必交付

把 ch02 / ch03 / ch04 / ch05 共 **4 个 stub → 完整 9 段章节**,深度对齐 ch09 429 行:

| chapter | 主题 | 深度 |
|---|---|---|
| ch02 | JOIN 7 种 + 性能差异 | ~250-300 行 |
| ch03 | 窗口函数(OVER/PARTITION BY/RANK/lead-lag) | ~300 行 |
| ch04 | CTE / 递归 CTE / 物化 | ~250 行 |
| ch05 | 聚合 / GROUP BY / HAVING / FILTER | ~200 行 |

合计 4 chapter ~1000 行 + 4 辅助文件更新 + handoff Phase 3c。

### 1.3 关键约束(CLAUDE.md 红线,沿用 Phase 2/3a)

- ❌ 禁 rm / Remove-Item / del / Move-Item 任何文件
- ❌ 禁 git reset --hard / git clean -fd / git checkout --
- ❌ 禁 DROP / TRUNCATE / DELETE FROM 不带 WHERE
- ❌ 禁文件名用 \ / : * ? " < > |
- ✅ 临时文件写 C:\Temp\,不写 ~/.tmp/
- ✅ 单次 Write ≤ 400 行 / 8000 tokens(避 120s abort)
- ✅ Edit 用锚定 old_string 追加

---

## 二、不重叠铁律(沿用 Phase 2/3a)

### 2.1 不重叠矩阵

| 主题 | 已写章节 | ch02-ch05 处理 |
|---|---|---|
| JOIN 算法(EXPLAIN 视角) | ch08 §3 | ch02 §6 引用,不重写 |
| N+1 反模式 | ch09 §6 | ch02 §7 引用,不重写 |
| 隐式 JOIN 反模式 | ch09 §2 | ch02 §3 引用,不重写 |
| 窗口函数索引视角 | ch08 §5 | ch03 §4 引用,不重写 |
| 排序分组索引视角 | ch08 §4 | ch05 §2 引用,不重写 |
| NULL 三值逻辑 | ch01 §3 + ch09 §4 | 不重写,引用 |
| EAV / SELECT * 反模式 | ch09 §1/§2 | 不涉及 |
| FDW 跨 DB | evidence-skill ch07 | ch04 §1 引用,FDW 不重写 |
| 中文 schema 雷区 | evidence-skill ch05 | 不重写 |

### 2.2 9 段结构固定

每 chapter 必含:
```
Core Idea / Frameworks Introduced / Key Concepts / Mental Models / Anti-patterns / Code Examples / Reference Tables / Key Takeaways / Connects To
```

ch09 因 7 节内容超单段容量,4 段用 "(续)" 段。ch02-ch05 单节内容较少,**不必拆 "(续)" 段**。

---

## 三、ch02 JOIN 详细设计(第一个 chapter)

### 3.1 主题与子结构

**JOIN 7 种 + 性能差异**

| 节 | 主题 | 主要素材 |
|---|---|---|
| § 1 | INNER JOIN(等值 / 非等值 / 自连接) | SQLBolt join + civilian7 |
| § 2 | OUTER JOIN(LEFT / RIGHT / FULL + ON vs WHERE) | SQLBolt + civilian7 |
| § 3 | CROSS JOIN(笛卡尔积 / 隐式逗号 FROM) | SQLBolt + ch09 §2 隐式 JOIN 反模式 |
| § 4 | SELF JOIN(自连接 / 层次结构) | civilian7 |
| § 5 | NATURAL JOIN / USING(列名匹配) | PG docs |
| § 6 | JOIN 算法与性能(NL / Hash / Sort Merge,与 ch08 §3 互补) | luke sql-join-* + ch08 §3 引用 |
| § 7 | JOIN 反模式(隐式逗号 / N+1 / 笛卡尔积 / 大表 JOIN) | ch09 §2 + §6 引用 |

### 3.2 ch02 关键铁律(目标 10+ 条)

每节 1-2 条,共 10+ 条铁律。

### 3.3 ch02 反模式(目标 8+ 条)

每节 1-2 条,共 8+ 条反模式(与 ch09 互补,不重复)。

### 3.4 ch02 跨引用(必须)

- **→ sql-skill ch08 §3 JOIN 算法**:ch02 §6 引用,JOIN 性能底层(ch02 讲语法 + 场景,ch08 §3 讲 EXPLAIN 算子)
- **→ sql-skill ch09 §2 隐式 JOIN 反模式**:ch02 §3 引用
- **→ sql-skill ch09 §6 N+1 反模式**:ch02 §7 引用
- **→ evidence-skill ch07 FDW CTE local scope**:ch02 §6 提及(FDW JOIN 性能差,本 chapter 不重写)

---

## 四、ch03 窗口函数详细设计

### 4.1 主题与子结构

**窗口函数(OVER/PARTITION BY/RANK/lead-lag)**

| 节 | 主题 |
|---|---|
| § 1 | OVER 子句基础(partition + order + frame) |
| § 2 | 排序函数(ROW_NUMBER / RANK / DENSE_RANK / NTILE) |
| § 3 | 分析函数(LAG / LEAD / FIRST_VALUE / LAST_VALUE / NTH_VALUE) |
| § 4 | 聚合窗口(SUM/AVG/COUNT OVER + 滑动窗口) |
| § 5 | 命名窗口(WINDOW 子句) |
| § 6 | 帧子句(ROWS BETWEEN / RANGE BETWEEN) |
| § 7 | 窗口函数反模式(无 PARTITION 聚合 vs GROUP BY 混用) |

### 4.2 ch03 跨引用

- **→ sql-skill ch08 §5 分页与窗口函数索引**:ch03 §4 引用
- **→ sql-skill ch05 聚合**:ch03 §4 与 ch05 §1 GROUP BY 区分

---

## 五、ch04 CTE 详细设计

### 5.1 主题与子结构

**CTE / 递归 CTE / 物化**

| 节 | 主题 |
|---|---|
| § 1 | WITH clause 基础(非递归 CTE) |
| § 2 | WITH RECURSIVE(递归 CTE + UNION / UNION ALL) |
| § 3 | MATERIALIZED CTE 决策(PG 12+ AS MATERIALIZED / NOT MATERIALIZED) |
| § 4 | CTE vs 子查询 vs 临时表(性能对比) |
| § 5 | CTE 可读性 + 维护性 |
| § 6 | 递归 CTE 应用场景(层次结构 / 图遍历 / 数字序列) |
| § 7 | CTE 反模式(过度嵌套 / 物化滥用) |

### 5.2 ch04 跨引用

- **→ evidence-skill ch07 FDW CTE local scope**:ch04 §1 引用,FDW 用法

---

## 六、ch05 聚合详细设计

### 6.1 主题与子结构

**聚合 / GROUP BY / HAVING / FILTER**

| 节 | 主题 |
|---|---|
| § 1 | 基础聚合(COUNT / SUM / AVG / MIN / MAX) |
| § 2 | GROUP BY(列表达式 / 隐式列 / ROLLUP / CUBE) |
| § 3 | HAVING(聚合后过滤) |
| § 4 | FILTER 子句(PG 9.4+,WHERE 不能替代) |
| § 5 | GROUPING SETS / GROUPING()(多维聚合) |
| § 6 | 聚合反模式(SELECT * + GROUP BY / 隐式 GROUP BY 列) |
| § 7 | 窗口聚合 vs GROUP BY(ch03 §4 引用) |

### 6.2 ch05 跨引用

- **→ sql-skill ch08 §4 排序与分组索引**:ch05 §2 引用
- **→ sql-skill ch01 §1 SQL 执行顺序**:ch05 §3 HAVING 引用

---

## 七、辅助文件更新

| 路径 | 更新 |
|---|---|
| `E:/obsidian/SQL/08-sql-skill/SKILL.md` | Chapter Index 把 ch02-ch05 `🔵 stub` → `✅` 完整 + Topic Index + Supporting Files + 调研入口 |
| `E:/obsidian/SQL/08-sql-skill/glossary.md` | 新增 ch02-ch05 Key Concepts 词条 |
| `E:/obsidian/SQL/08-sql-skill/patterns.md` | 反模式总表追加 ch02-ch05 反模式 |
| `E:/obsidian/SQL/08-sql-skill/cheatsheet.md` | 新增 ch02-ch05 决策表 + 关键经验追加 |

---

## 八、验收清单

- [ ] ch02/ch03/ch04/ch05 4 文件存在 + 9 段齐全
- [ ] ch02 250-300 行 / ch03 300 行 / ch04 250 行 / ch05 200 行
- [ ] Frameworks 累计 ≥ 30 条(ch02 10+ / ch03 8+ / ch04 6+ / ch05 6+)
- [ ] Anti-patterns 累计 ≥ 30 条(ch02 8+ / ch03 6+ / ch04 8+ / ch05 8+)
- [ ] 不重叠 ch01/ch07/ch08/ch09 已写内容
- [ ] 不重写 evidence-skill 业务侧(ch05/ch07/ch14/ch16)
- [ ] SKILL.md Chapter Index ch02-ch05 `🔵 stub` → `✅`
- [ ] glossary.md 新增 ≥ 15 词条
- [ ] patterns.md 反模式 ≥ 35 条
- [ ] cheatsheet.md 决策表 ≥ 14 张 / 关键经验 ≥ 13 条
- [ ] handoff-sql-skill-phase3c-2026-10-14.md 已写

---

## 九、不做的事(明确边界)

- ❌ ch06 / ch10 留 Phase 3c 接力
- ❌ 不实现评测集 / 联动测试(Phase 4+)
- ❌ 不重复 Phase 2 + Phase 3a 内容
- ❌ 不修改 evidence-skill

---

## 十、下一步

1. ✅ 用户已对齐 + 已选 Native 执行(沿用 Phase 3a 模式)
2. invocation **`superpowers:writing-plans`** 写 Phase 3b 实施计划
3. 计划批准后:Native 执行 4 chapter + 4 辅助文件 + verification + handoff
4. 每章完成前:`superpowers:verification-before-completion`