# [PROJECT_NAME] 宪章
<!-- 示例：spec-agent-prompt-my 宪章 -->

## 核心原则

### [PRINCIPLE_1_NAME]
<!-- 示例：文档即代码 (Docs as Code) -->
[PRINCIPLE_1_DESCRIPTION]
<!-- 示例：
- MUST：所有功能变更必须先更新 docus/ 或 specs/ 中的对应文档，再进行代码修改。
- MUST：实现、测试、验收必须可追溯到文档条目（spec.md / tasks.md / checklist.md）。
- MUST NOT：未经文档确认直接修改核心行为或接口契约。
- Rationale：保证系统行为由文档定义，避免 AI 生成与设计漂移。
-->

### [PRINCIPLE_2_NAME]
<!-- 示例：让规范可执行 (Executable Specs) -->
[PRINCIPLE_2_DESCRIPTION]
<!-- 示例：
- MUST：每个需求目录至少包含 spec.md、tasks.md、checklist.md。
- MUST：spec.md 中每条关键需求必须可测试，且有 Success Criteria。
- SHOULD：任务按用户故事分组，保证可独立交付与验证。
- MUST：测试、评估、检查、验收输出统一落地到 specs/reports/。
- Rationale：确保“规范 -> 实现 -> 验证”闭环可执行、可审计。
-->

### [PRINCIPLE_3_NAME]
<!-- 示例：单一事实来源 (Single Source of Truth) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- 示例：
- MUST：长期规则以 docus/ 为准，迭代实现以 specs/ 为准。
- MUST：specs/statistics.md 维护规范编号与目录映射。
- MUST NOT：在多个文件中维护相互冲突的“最终定义”。
- SHOULD：PR 描述中显式引用被影响的 docus 条款与 spec 条款。
- Rationale：降低信息分叉，提升跨人类/AI 协作一致性。
-->

### [PRINCIPLE_4_NAME]
<!-- 示例：交互语言与协作规则 -->
[PRINCIPLE_4_DESCRIPTION]
<!-- 示例：
- MUST：默认对话语言与文档语言为中文。
- SHOULD：当用户输入英文且表达有误时，先给出修正表达，再执行任务。
- MUST：AI 输出应保持指令可执行、路径清晰、步骤可复现。
- Rationale：降低沟通误差，确保协作可持续。
-->

### [PRINCIPLE_5_NAME]
<!-- 示例：代码风格与错误处理策略 -->
[PRINCIPLE_5_DESCRIPTION]
<!-- 示例：
- MUST：遵循极简主义，仅保留核心业务逻辑。
- MUST：默认不添加 try-except 吞错；除非用户明确要求。
- MUST：复杂修改前先定位职责边界；结构性重构前先征求用户意见。
- SHOULD：注释聚焦“为什么”，避免废话式注释。
- Rationale：以最小复杂度实现可维护、可诊断代码。
-->

### [PRINCIPLE_6_NAME]
<!-- 示例：环境与测试纪律 -->
[PRINCIPLE_6_DESCRIPTION]
<!-- 示例：
- MUST：在 Windows + PowerShell 环境下执行项目默认流程（若项目另有说明，以项目为准）。
- MUST：Python 项目使用 my-uv 与 uv 统一管理环境与依赖。
- MUST：测试框架优先 pytest，目录建议 test/unit、test/integration、test/data。
- MUST：报告包含通过率、失败详情、关键堆栈、可选覆盖率摘要，并归档到 specs/reports/。
- Rationale：保证环境可复现、测试结果可验证。
-->

## [SECTION_2_NAME]
<!-- 示例：项目结构与文档体系约束 -->

[SECTION_2_CONTENT]
<!-- 示例：
- 目录职责：
  - docus/：长期依据来源文档（constitution、structure、layers、workflows、others）。
  - specs/：当前迭代规范（每个需求子目录 + statistics.md）。
  - specs/reports/：测试、评估、检查、验收、环境验证报告。
  - src/：实现代码；tests/：测试代码。
- MUST：当现有仓库结构不符合约束时，先制定迁移策略，再分步迁移。
- SHOULD：迁移前后运行结构检查脚本并记录差异。
-->

## [SECTION_3_NAME]
<!-- 示例：宪章同步与执行流程 -->

[SECTION_3_CONTENT]
<!-- 示例：
- 宪章更新流程：
  1) 收集输入与仓库上下文
  2) 更新 docus/constitution.md
  3) 同步 .docusdd/templates/*
  4) 同步 .github/agents/*.agent.md 中的约束引用
  5) 同步 README.md 与 quickstart.md 的运行时说明
  6) 输出同步影响报告（版本变更、影响文件、待办项）
- MUST：同步时主动检查是否存在过时路径、过时代理名、冲突规则。
- MUST：如果关键信息缺失，写 TODO(FIELD_NAME): explanation 并在报告中列出。
-->

## 治理
<!-- 示例：宪章优先于其他实践，所有变更必须有版本策略与传播策略 -->

[GOVERNANCE_RULES]
<!-- 示例：
- 宪章优先级：本文件高于项目内其他流程性文档。
- 修订要求：必须说明变更动机、影响范围、迁移/回滚策略。
- 版本策略（SemVer）：
  - MAJOR：不兼容治理变更或原则重定义。
  - MINOR：新增原则/章节，或流程实质增强。
  - PATCH：措辞澄清、排版修复、非语义细化。
- 一致性传播最小检查集（必须执行）：
  - .docusdd/templates/docu-structure-template.md
  - .docusdd/templates/docu-template.md
  - .docusdd/templates/spec-specs-template.md
  - .docusdd/templates/spec-tasks-template.md
  - .docusdd/templates/spec-checklist-template.md
  - .docusdd/templates/spec-report-template.md
  - .github/agents/*.agent.md
  - README.md
  - quickstart.md
- 合规审计：关键 PR 必须给出受影响原则清单与 specs/reports/ 证据链接。
-->

**版本**： [CONSTITUTION_VERSION] | **通过日期**： [RATIFICATION_DATE] | **最后修订**： [LAST_AMENDED_DATE]
<!-- 示例：版本：1.2.0 | 通过日期：2026-05-20 | 最后修订：2026-06-01 -->
