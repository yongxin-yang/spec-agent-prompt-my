---
description: 基于交互式或已提供的原则输入创建或更新项目宪章、项目结构，并确保所有依赖模板保持同步。
handoffs: 
  - label: build specifications, including specific execution of document or code structure changes and code testing based on the updated constitution.
    agent: DDD-require-explainer
    prompt: 基于更新后的宪章实现功能规格。我想构建...
---

## 用户输入

```text
$ARGUMENTS
```

你 **必须** 在继续之前先考虑用户输入（如果不为空）。

## 执行前检查

先判断当前仓库是否需要“初始化”还是“增量更新”。

- 如果 `docus/constitution.md`、`docus/structure.md`、`specs/` 或 `src/` 尚未建立，或用户明确要求初始化项目，则执行初始化流程。
- 如果项目已存在，则只更新宪章、必要的依赖模板和与宪章相关的目录结构，不要重建已存在文件。

### 初始化流程

若需要初始化项目，请按以下顺序创建：
1. 复制 [.docusdd/templates/docu-constitution-template.md](/.docusdd/templates/docu-constitution-template.md) 到 `docus/constitution.md`。
2. 复制 [.docusdd/templates/docu-structure-template.md](/.docusdd/templates/docu-structure-template.md) 到 `docus/structure.md`。
3. 复制 [.docusdd/templates/docu-template.md](/.docusdd/templates/docu-template.md) 到 `docus/layers/`、`docus/workflows/` 或其他需要的新文档文件中，作为新文档的起点。
4. 创建 `docus/layers/`、`docus/workflows/`、`docus/others/`、`specs/`、`specs/reports/`、`src/`、`tests/` 等目录。
5. 在 `specs/` 下创建 `statistics.md`，作为需求序号与目录索引。
初始化或重建项目结构时，可先运行 [.docusdd/scripts/check_docus_structure.ps1](../../.docusdd/scripts/check_docus_structure.ps1) 和 [.docusdd/scripts/check_specs_structure.ps1](../../.docusdd/scripts/check_specs_structure.ps1) 观察当前树状结构，再决定需要创建或迁移哪些文件。

### 目录与文件的职责

- `docus/`：长期稳定的依据来源文档，包含宪章、结构、层级与流程规范。
- `specs/`：当前迭代的规范驱动文档集合，包含每个需求的 `spec.md`、`tasks.md`、`checklist.md`。
- `specs/reports/`：测试、评估、检查、验收和环境验证报告的统一输出目录。
- `src/`：实现代码目录，仅在实现层面使用。
- `tests/`：测试代码与验证脚本目录。

### 运行环境叙述职责

当你处理 `docus/structure.md` 时，必须把运行环境约束写成清晰、可执行的默认说明，并优先参考用户提供的参考文件或输入。如果用户没有提供足够信息，则需要从仓库上下文推断，或直接询问用户以获取必要信息。运行环境说明必须包含：

如果仓库已有 `docus/structure.md`，你不仅要更新宪章，也要同步更新该文件里的运行环境段落与项目结构说明。
这个文件作为项目的外部架构契约（Architecture Contract），应保持接口稳定性（Interface Stability）。
即内部实现和目录结构的重构不应直接影响其内容，仅当对外暴露的逻辑模块、运行方式或公共能力发生变化时才更新文档。

### 模板引用规则

所有创建新文件时的模板来源都必须显式指向仓库内的真实模板文件，优先使用相对路径链接，例如：
- [.docusdd/templates/docu-constitution-template.md](../../.docusdd/templates/docu-constitution-template.md)
- [.docusdd/templates/docu-structure-template.md](../../.docusdd/templates/docu-structure-template.md)
- [.docusdd/templates/docu-template.md](../../.docusdd/templates/docu-template.md)
- [.docusdd/templates/spec-specs-template.md](../../.docusdd/templates/spec-specs-template.md)
- [.docusdd/templates/spec-tasks-template.md](../../.docusdd/templates/spec-tasks-template.md)
- [.docusdd/templates/spec-checklist-template.md](../../.docusdd/templates/spec-checklist-template.md)
- [.docusdd/templates/spec-report-template.md](../../.docusdd/templates/spec-report-template.md)

### DDD文件夹架构

- specs/ **规范驱动文档**
 - scripts/ 脚本工具等
 - checklists/ 各类检查清单，按照需求或模块进行分类 tester 输出
 - ###-feature/ 每个需求的文件夹，命名为需求编号加简要名称（如 `001-user-authentication/`）
   - specs.md 该需求的简洁的自然语言描述
   - tasks.md require-explainer 输出 具体实现规划以及实现状态和测试规划
 - statistics.md 对规范以及规范文件夹序列(`SPEC_ORDER`)进行管理，映射规范序号与简要说明之间的关系

- docus/ **依据来源文档**
 - structure.md 项目结构，项目目标、架构设计、技术栈及模块职责
 - constitution.md 最高的规则与规范
 - layers/ 分层与模块的文件或文件夹(如果代码结构是多层嵌套的)，注明每个层的作用以及相互之间的交互逻辑
  - README.md 介绍文档，包含规范文档的注册等
  - ...
 - tops/ 贯穿整个项目,需要重点强调的规范
  - README.md 介绍文档，包含规范文档的注册等
  - ...
 - others/ 其他规范

- src/ 源代码目录
- tests/ 测试代码目录
- ... 数据，结果，提示词等
- README.md (可选,项目说明文档)
- quickstart(可选，方便项目快速启动)
若不为空，则定位测试文件，源代码和文档位置并进行迁移，使之符合上述架构。
你需要制定迁移策略，读取文档，了解项目并进行文件的移动和更改等。
可能需要进行多轮。

## 大纲

你正在更新 `docus/constitution.md` 中的项目宪章。该文件是一个包含方括号占位符（例如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]`）的模板。你的职责是：(a) 收集/推导具体值，(b) 精确填充模板，(c) 将任何修订传播到所有依赖产物中。

**注意**：如果 `docus/constitution.md` 尚不存在，它应当在项目初始化时从 `.docusdd/templates/docu-constitution-template.md` 初始化而来。如果缺失，先复制模板。

按如下执行流程进行：

1. 加载 `docus/constitution.md` 中现有宪章。
   - 识别所有形如 `[ALL_CAPS_IDENTIFIER]` 的占位符 token。
   **重要**：用户可能需要的原则数量少于或多于模板预设数量。若用户指定了数量，必须遵从，并按通用模板调整文档结构。

2. 为占位符收集/推导值：
   - 若用户输入（对话）提供了值，直接使用。
   - 否则从仓库上下文推断（README、文档、若有内嵌的宪章旧版本等）。
   - 治理日期：`RATIFICATION_DATE` 为最初批准日期（若未知则询问或标记 TODO）；`LAST_AMENDED_DATE` 若发生修改则为今天，否则保持原值。
   - `CONSTITUTION_VERSION` 必须按语义化版本规则递增：
     - MAJOR：治理/原则的移除或重定义导致不向后兼容。
     - MINOR：新增原则/章节，或对指导进行实质性扩展。
     - PATCH：澄清、措辞/拼写修正、非语义性细化。
   - 若版本升级类型不明确，先提出理由再最终确定。

3. 起草更新后的宪章内容：
   - 将每个占位符替换为具体文本（除非项目刻意保留某些模板槽位未定义；若保留必须明确说明理由）。
   - 保持标题层级；占位符替换后可移除注释，除非注释仍能提供必要的澄清指导。
   - 确保每个 Principle 章节包含：简洁的名称行、体现不可妥协规则的段落（或要点列表）、若理由并非显而易见则给出明确 rationale。
   - 确保 Governance 章节列出：修订流程、版本策略、合规复核期望。

4. 一致性传播检查清单（将原先的检查清单转为主动校验）：
   - 读取 `.docusdd/templates/docu-structure-template.md` 并确保其中“宪章检查/复杂度跟踪/结构约束”与当前宪章一致。
   - 读取 `.docusdd/templates/docu-template.md`，确保分层文档模板的输入/输出、职责边界、注释规范与宪章一致。
   - 读取 `.docusdd/templates/spec-specs-template.md`，确保需求章节与宪章中的测试纪律、单一事实来源、语言交互规则一致。
   - 读取 `.docusdd/templates/spec-tasks-template.md`，确保任务分类包含由宪章驱动的任务类型（文档先行、环境校验、测试与报告归档）。
   - 读取 `.docusdd/templates/spec-checklist-template.md`，确保验收清单覆盖宪章合规项与 `specs/reports/` 追溯要求。
   - 读取 `.docusdd/templates/spec-report-template.md`，确保报告模板包含宪章合规检查与证据字段。
   - 读取 `.github/agents/*.agent.md`（包括本文件），确认不存在过时路径、错误模板名或冲突职责描述。
   - 读取 `README.md` 与 `quickstart.md`，更新对变更原则、目录约束和执行流程的引用。
   - 读取 `docus/` 下相关文档，确认不存在与当前治理冲突的过时引用。

4.1 当用户要求“更新模板默认规则”时的强制执行方式：
   - 必须保留 `.docusdd/templates/docu-constitution-template.md` 的占位符结构。
   - 必须把默认规则写入对应 `<!-- 示例：... -->` 注释中，而不是直接替换所有占位符。
   - 示例需尽可能详细，至少包含 MUST/SHOULD 级约束、路径约束、输出约束与 rationale。

5. 生成同步影响报告（在宪章文件更新后，以 HTML 注释形式置于宪章文件顶部）：
   - 版本变化：old → new
   - 已修改原则列表（若重命名，则 old title → new title）
   - 新增章节
   - 移除章节
   - 需要更新的模板（✅ 已更新 / ⚠ 待处理）及文件路径
   - 若刻意延期某些占位符，列出后续 TODO。

6. 在最终输出前进行校验：
   - 不存在未解释的方括号 token。
   - 版本行与报告一致。
   - 日期使用 ISO 格式 YYYY-MM-DD。
   - 原则表达为声明式、可测试、避免含糊措辞（将 "should" 替换为 MUST/SHOULD，并在必要时给出理由）。

7. 将完成后的宪章写回 `docus/constitution.md`（覆盖写入）。

8. 向用户输出最终摘要：
   - 新版本与版本升级理由。
   - 任何标记为需要手动跟进的文件。
   - 建议的提交信息（例如：`docs: amend constitution to vX.Y.Z (principle additions + governance update)`）。

格式与风格要求：

- Markdown 标题必须与模板完全一致（不要提升/降低层级）。
- 合理换行以提升可读性（理想 <100 字符），但不要为了硬性限制导致奇怪断行。
- 章节之间仅保留一个空行。
- 避免行尾空白。

如果用户只提供了部分更新（例如只修订一个原则），仍需执行校验与版本决策步骤。

如果关键信息缺失（例如批准日期确实未知），插入 `TODO(<FIELD_NAME>): explanation`，并在同步影响报告中作为延期项列出。

不要创建新的模板；始终在已有 `docus/constitution.md` 上操作。

## 执行后检查

无