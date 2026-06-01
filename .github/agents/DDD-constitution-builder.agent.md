---
description: 基于交互式或已提供的原则输入创建或更新项目宪章，并确保所有依赖模板保持同步。
handoffs: 
  - label: build specifications, including specific execution of document or code structure changes and code testing based on the updated constitution.
    agent: DDD-require-explainer
    prompt: 基于更新后的宪章实现功能规格。我想构建...
reference: https://github.com/github/spec-kit
---

## 用户输入

```text
$ARGUMENTS
```

你 **必须** 在继续之前先考虑用户输入（如果不为空）。

## 执行前检查

检查项目文件夹是否为空。
若为空，则创建标准文件夹与文件架构（见下文DDD文件夹架构）：
1. 复制 `.docusdd/templates/constitution-template.md` 到 `docus/constitution.md` 。
2. 复制 `.docusdd/templates/structure-template.md` 到 `docus/structure.md` 。
3. 创建 `docus/layers/`、`docus/workflows/` 文件夹。
4. 创建 `src/`、`tests/` 文件夹。
5. 创建 `specs/` 文件夹，并在其中创建 `statistics.md` 文件

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
  - ...
 - workflows/ 层与层之间、模块与模块之间交互的逻辑或代码运行的调用和传递等
  - ...
 - others/ 非代码部分的规范等
  - ...
 ... 其他文件，通常可能是贯穿整个项目的文档
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

**注意**：如果 `docus/constitution.md` 尚不存在，它应当在项目初始化时从 `.docusdd/templates/constitution-template.md` 初始化而来。如果缺失，先复制模板。

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
   - 读取 `.docusdd/templates/spec-tasks-template.md` 并确保其中的 "Constitution Check" 或规则与更新后的原则一致。
   - 读取 `.docusdd/templates/spec-specs-template.md` 以确保范围/需求对齐——若宪章新增/移除必需章节或约束，则更新模板。
   - 读取 `.docusdd/templates/spec-checklist-template.md` 并确保任务分类反映新增或移除的原则驱动任务类型（例如可观测性、版本管理、测试纪律）。
   - 读取 `docus/` 下的每个命令文件，确认在需要通用指导时不存在过时引用（例如仅提及 CLAUDE 这类特定代理名）。

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