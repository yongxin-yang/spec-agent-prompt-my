## 报告规范 (Report Specifications)

> 宪章对齐要求：所有报告必须可追溯到 `docus/constitution.md` 的相关条款，并统一归档到 `specs/reports/`。

**一致性审计报告模板**:

```markdown
# [Agent Name] 检查报告

## 1. 检查元数据 (Metadata)
- **时间**: YYYY-MM-DD HH:MM
- **执行人**: [Agent Name]
- **目标**: [检查对象，如 Specify.md 或 src/]
- **自定义检查项**: [用户定义的额外检查规则]
- **关联依据文档**: [`docus/...` 章节列表]
- **关联实现**: [`src/...` 文件/函数列表]

## 2. 检查结果摘要 (Summary)
- **状态**: [Pass / Fail / Warning]
- **发现问题数**: N
- **检查范围**: [全量 / 增量 / 自定义]

## 3. 详细问题清单 (Issues)
- [ ] [Critical] 文件 X 缺少头部注释。
- [x] [Warning] 函数 Y 参数未注明类型。

### 3.0 宪章一致性 (Constitution Compliance)
- [ ] [Critical] 是否遵循“文档即代码”（实现前文档是否已更新）
- [ ] [Critical] 是否遵循“单一事实来源”（是否出现冲突定义）
- [ ] [Critical] 是否满足“`specs ↔ docus ↔ src` 双向追溯”（需求、依据、实现是否可相互定位）
- [ ] [Warning] 是否满足“环境与测试纪律”（环境激活、测试执行、报告归档）
- [ ] [Info] 宪章条款引用是否完整（条款编号或章节名）

### 3.1 结构一致性 (Structure)
- [ ] [Critical] src/X.py 未在 Structure.md 中定义。
- [x] [Pass] 模块 Y 结构匹配。

### 3.2 规范一致性 (Specification)
- [ ] [Warning] 函数 Z 参数签名与 Layer Spec 不符。
- [ ] [Info] Spec ID #123 (from Specify.md) 未找到对应实现。

### 3.3 自定义检查 (Custom Checks)
- [ ] [Fail] 规则 "Check A" 未通过: 原因...

## 4. 修正建议 (Suggestions)
- 针对发现的问题给出具体修改建议。

## 5. 归档信息 (Archive)
- **输出路径**: `specs/reports/[report-name].md`
- **关联规范**: `specs/[###-feature-name]/specs.md`
- **关联任务**: `specs/[###-feature-name]/tasks.md`
- **关联清单**: `specs/[###-feature-name]/checklist.md`
```
