# Topic Index — 术语 → 章节全索引

> sql-skill 全部 99 个术语的章节定位。SKILL.md 只保留 12 大框架速查,
> 完整索引在此。**读法**:先在此定位术语 → 再 Read 对应 chapter 段落。
> 术语**定义**查 [supporting/glossary.md](../supporting/glossary.md)。

---

1. **AOT / API** → 不在 sql-skill 范围(evidence-skill ch01)
2. **array** → ch07 §2
3. **anti-pattern** → ch01/ch07/ch08 + cheatsheet §11
4. **B-Tree** → ch08 §1
5. **Bitmap Heap Scan** → ch08 §6
6. **BRIN** → ch08 §1
7. **COALESCE** → ch01 §3
8. **covering index (INCLUDE)** → ch08 §1
9. **CROSS JOIN** → ch02 §3
10. **CTE / WITH RECURSIVE / MATERIALIZED** → ch04 §1/§2/§3
11. **cast (`::` / CAST)** → ch01 §2
12. **date 不能 SUBSTR** → ch07 §5
13. **DENSE_RANK / NTILE** → ch03 §2
14. **DISTINCT ON** → ch01 §4
15. **EXPLAIN ANALYZE** → ch08 §6
16. **expression index** → ch08 §2
17. **FILTER 子句** → ch05 §4
18. **FIRST_VALUE / LAST_VALUE / NTH_VALUE** → ch03 §3
19. **Filter / FROM** → ch01 §1
20. **FULL OUTER JOIN** → ch02 §2
21. **GIN / GiST** → ch07 §1/§3
22. **GROUP BY / HAVING / GROUPING SETS / ROLLUP / CUBE** → ch05 §2/§3/§5
23. **GROUPING() / GROUPING_ID()** → ch05 §5
24. **Group By / GROUP BY 索引** → ch08 §4
25. **Hash Index / Hash Join** → ch08 §1/§3
26. **HashAggregate** → ch08 §4/§6
27. **INNER JOIN / LEFT JOIN / RIGHT JOIN** → ch02 §1/§2
28. **JOIN 7 种** → ch02
29. **JOIN 算法** → ch02 §6 / ch08 §3
30. **JSONB / JSON** → ch07 §1
31. **Keyset pagination** → ch08 §5
32. **LAG / LEAD** → ch03 §3
33. **LIKE** → ch08 §2
34. **LIMIT / OFFSET** → ch08 §5
35. **LATERAL JOIN` + `unnest** → ch07 §2
36. **MATERIALIZED (CTE)** → ch04 §3
37. **MUST` (中文 schema 雷区)** → ch07 §5
38. **NATURAL JOIN / USING** → ch02 §5
39. **N+1 反模式** → ch02 §7 / ch08 §3 / ch09 §6
40. **NULL` 三值逻辑** → ch01 §3
41. **NULLIF** → ch01 §3
42. **Nested Loop** → ch08 §3
43. **OUTER JOIN (LEFT/RIGHT/FULL)** → ch02 §2
44. **OVER 子句 (窗口函数)** → ch03 §1
45. **operator class** → ch08 §2
46. **ORDER BY 索引** → ch08 §4
47. **PARTITION BY** → ch03 §1
48. **partial index** → ch08 §2
49. **percentile_cont / array_agg / string_agg** → ch05 §1
50. **INTERSECT (交集)** → ch06 §2
51. **INTERSECT ALL** → ch06 §2
52. **UNION / UNION ALL** → ch06 §1
53. **EXCEPT (差集)** → ch06 §3
54. **EXCEPT ALL** → ch06 §3
55. **evidence-skill 协作** → ch10 §1-§4
56. **三层 lookup (cheatsheet → chapter → evidence-skill)** → ch10 §6
57. **4 道防线 (readonly + sqlglot + statement_timeout + LIMIT)** → ch09 §7 / ch10 §2
58. **civilian7 评测** → ch10 §5
59. **cheatsheet 决策快查** → cheatsheet.md
60. **pgbouncer session-mode** → ch07 §4
61. **pg_stat_statements** → ch08 §6
62. **postgres_fdw** → ch07 §4
63. **RANK / DENSE_RANK / NTILE / ROW_NUMBER** → ch03 §2
64. **RANGE BETWEEN / ROWS BETWEEN** → ch03 §6
65. **Recursion (递归 CTE)** → ch04 §2
66. **ROLLUP / CUBE / GROUPING SETS** → ch05 §5
67. **SELF JOIN** → ch02 §4
68. **Sort (算子)** → ch08 §6
69. **Sort Merge Join** → ch08 §3
70. **snake_case** → ch01 §4
71. **Seq Scan** → ch08 §6
72. **Subquery** → ch01 §1/§2
73. **Top-N optimization** → ch08 §5
74. **unnest** → ch07 §2
75. **varchar_pattern_ops** → ch08 §2
76. **WHERE vs HAVING** → ch05 §3
77. **WINDOW 子句 (命名窗口)** → ch03 §5
78. **Window Function** → ch03
79. **percentile_cont** → ch05 §1
80. **array_agg` / `string_agg** → ch05 §1
81. **"店铺" / "订单日期" / "销售金额"** → ch07 §5
82. **中文列双引号** → ch07 §5 + evidence-skill ch05
83. **ds` / `shop_name` / `stat_date` 假名** → ch07 §5 + evidence-skill ch05
84. **date SUBSTR 陷阱** → ch07 §5 + evidence-skill ch05
85. **MySQL 8.0** → ch11 §1
86. **MySQL 隐式转换 (文本→数字)** → ch11 §1
87. **MySQL DDL 隐式 commit** → ch11 §1
88. **Oracle** → ch11 §2
89. **Oracle 空串 = NULL** → ch11 §2
90. **Oracle ROWNUM vs ROW_NUMBER** → ch11 §2
91. **Oracle NLS 会话变量** → ch11 §2
92. **SQL Server** → ch11 §3
93. **SARGability** → ch11 §3
94. **FORMAT() 性能陷阱** → ch11 §3
95. **CROSS APPLY / OUTER APPLY** → ch11 §3
96. **keyset 分页 (三方言写法)** → ch11 §4 / ch08 §5
97. **跨方言对照表** → ch11 §4
98. **查询门面 (跨 DB 协作)** → ch11 §5 / ch10 §7
99. **方言迁移 12 项检查** → ch11 §6

---

## 中文术语

- **date 不能 SUBSTR** → ch07 §5
- **FILTER 子句** → ch05 §4
- **Group By / GROUP BY 索引** → ch08 §4
- **JOIN 7 种** → ch02
- **JOIN 算法** → ch02 §6 / ch08 §3
- **MUST` (中文 schema 雷区)** → ch07 §5
- **N+1 反模式** → ch02 §7 / ch08 §3 / ch09 §6
- **NULL` 三值逻辑** → ch01 §3
- **OVER 子句 (窗口函数)** → ch03 §1
- **ORDER BY 索引** → ch08 §4
- **INTERSECT (交集)** → ch06 §2
- **EXCEPT (差集)** → ch06 §3
- **evidence-skill 协作** → ch10 §1-§4
- **三层 lookup (cheatsheet → chapter → evidence-skill)** → ch10 §6
- **4 道防线 (readonly + sqlglot + statement_timeout + LIMIT)** → ch09 §7 / ch10 §2
- **civilian7 评测** → ch10 §5
- **cheatsheet 决策快查** → cheatsheet.md
- **Recursion (递归 CTE)** → ch04 §2
- **Sort (算子)** → ch08 §6
- **WINDOW 子句 (命名窗口)** → ch03 §5
- **"店铺" / "订单日期" / "销售金额"** → ch07 §5
- **中文列双引号** → ch07 §5 + evidence-skill ch05
- **ds` / `shop_name` / `stat_date` 假名** → ch07 §5 + evidence-skill ch05
- **date SUBSTR 陷阱** → ch07 §5 + evidence-skill ch05

---

## 多方言术语(ch11)

- **MySQL 8.0** → ch11 §1
- **MySQL 隐式转换 (文本→数字)** → ch11 §1
- **MySQL DDL 隐式 commit** → ch11 §1
- **Oracle** → ch11 §2
- **Oracle 空串 = NULL** → ch11 §2
- **Oracle ROWNUM vs ROW_NUMBER** → ch11 §2
- **Oracle NLS 会话变量** → ch11 §2
- **SQL Server** → ch11 §3
- **SARGability** → ch11 §3
- **FORMAT() 性能陷阱** → ch11 §3
- **CROSS APPLY / OUTER APPLY** → ch11 §3
- **keyset 分页 (三方言写法)** → ch11 §4 / ch08 §5
- **跨方言对照表** → ch11 §4
- **查询门面 (跨 DB 协作)** → ch11 §5 / ch10 §7
- **方言迁移 12 项检查** → ch11 §6