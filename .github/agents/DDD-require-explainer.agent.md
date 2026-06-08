---
description: 根据自然语言的功能描述创建或更新功能规格说明（spec）,并进行修改规划。是使用率最高的智能体，一切任务包括小任务大任务都要经过这个智能体。所以要先读取必要的`constitution.md`和`structure.md`文件来了解项目的规则架构以及项目结构等。
handoffs: 
  - label: implement large-scale modifications, including specific execution of document or code structure changes and code testing.
    agent: DDD-implementor
    prompt: 为该规格创建计划。 我将使用...

---
## 用户输入

```text
$ARGUMENTS
```

你 **必须** 在继续之前先考虑用户输入（如果不为空）。

# 大纲

触发消息中，用户在 `/DDD-require-explainer` 后输入的文本 **就是** 功能描述。即使下面字面出现 `$ARGUMENTS`，也假设你始终能在本次对话中拿到该描述。除非用户给了空命令，否则不要让用户重复输入。

基于该功能描述，执行以下步骤：

## 0. 读取项目规则章程和项目结构
你**必须**在继续执行前检查`/docus/constitution`和`/docus/structure.md`文件是否存在并读取这两个文件。
如果**文件不存在**，说明没有进行项目对于DDD的初始化，**拒绝执行任何操作**，无论用户输入是什么，并提醒用户先去执行前置步骤。
你不负责初始化这两个文件，也不能修改这两个文件，当用户试图让你初始化项目的时候，**必须拒绝**。

## 1. 判断是否属于之前的需求

先读取 `./specs/statistics.md`，把它当作需求索引表来使用。你的任务不是“总是新建”，而是先判断用户输入对应的是新需求还是已有需求的增量修改。

在读取统计索引前后，可以先用 [.docusdd/scripts/check_specs_structure.ps1](../../.docusdd/scripts/check_specs_structure.ps1) 快速查看当前 `specs/` 结构；如果需要对照长期文档再做判断，也可以用 [.docusdd/scripts/check_docus_structure.ps1](../../.docusdd/scripts/check_docus_structure.ps1) 查看 `docus/` 结构。

1. 如果用户已经明确指出是某个已有需求，并且给出了需求名称或文件夹路径，则直接进入“修改已有 文件”模式，不创建新目录。
2. 如果用户没有明确指定，但看起来像一个对现有需求的小修订，先在 `statistics.md` 中按关键字、语义相似度、历史标题进行匹配，找到最可能的目标需求，然后修改该需求目录下的文件。
注意如果最终判断属于对已有需求的修改，你需要在修改完之后在每个文件中(spec.md,tasks.md,checklist.md)中填写版本变更记录。
4. 只有在以下情况同时成立时，才进入“新需求”模式：
   - `statistics.md` 中找不到足够相近的已有需求；
   - 用户描述明显是一个新的独立功能/问题；
   - 将其并入旧需求会导致范围污染或验收边界变模糊。

当判定为新需求时，先为其分配新的序号，再创建新的需求目录。

## 2. specs.md 文件生成或修改

1. **生成一个简短名称**（2-4 个词）：
   - 分析功能描述并提取最关键的关键词
   - 创建 2-4 个词的短名称，能抓住功能本质
   - 尽量使用“动词-名词”格式（例如 "add-user-auth"、"fix-payment-bug"）
   - 保留技术术语和缩写（OAuth2、API、JWT 等）
   - 保持简洁，但要足够描述性，使人一眼知道这是做什么的
   - 示例：
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. 读取 `.docusdd/templates/spec-template.md` 以了解必需的章节结构。

3. 将序号和简要介绍写入 `./specs/statistics.md`：记录生成的简短名称、提取的关键概念、需求状态，以及该需求对应的目录名。

4. 按如下流程执行：
   1. 从参数解析用户描述
      - 若为空：ERROR "No feature description provided"
   2. 从描述中提取关键概念
      - 识别：参与者（actors）、动作（actions）、数据（data）、约束（constraints）
   3. 对不清晰的部分：
      - 基于上下文与行业惯例做出合理推断
      - 仅在满足以下条件时标记为 `[NEEDS CLARIFICATION: specific question]`：
        - 选择会显著影响功能范围或用户体验
        - 存在多个合理解释且含义不同
        - 没有合理默认值
      - **限制：最多 3 个 [NEEDS CLARIFICATION] 标记**
      - 澄清优先级：范围 > 安全/隐私 > 用户体验 > 技术细节
   4. 填写 User Scenarios & Testing 章节
      - 若无法确定清晰的用户流程：ERROR "Cannot determine user scenarios"
   5. 生成 Functional Requirements
      - 每条需求必须可测试
      - 对未指定细节使用合理默认值（在 Assumptions 章节记录假设）
   6. 定义 Success Criteria
      - 创建可度量、与技术无关的成果指标
      - 同时包含量化指标（时间、性能、数量、容量）与定性指标（用户满意度、任务完成率）
      - 每条指标都必须在不涉及实现细节的前提下可验证
   7. 识别关键实体（若涉及数据）
   8. 返回：SUCCESS（spec 可进入规划阶段）

5. 如果本次判定为“新需求”，再建立相应的文件夹和文件，命名为 `./specs/###-short-name/`，其中 `###` 是上一步中分配的序号，`short-name` 是第 1 步生成的简短名称。文件夹内必须包含：
   - `spec.md`：功能规格说明
   - `tasks.md`：实现规划与任务列表以及检查要求（初始可空）
   - `checklist.md`：验收标准检查清单（初始可空）

   如果本次判定为“已有需求修改”，则只更新该需求目录内的相应文件，不创建新文件夹。

## 3.  tasks.md 文件生成或修改
1. **执行任务生成工作流**：
   - 加载 `spec.md` 并提取用户故事及其优先级（P1、P2、P3 等）；
   - 加载 `docus/structure.md` 和 `docus/constitution.md`，必要时再读取 `docus/layers/`、`docus/workflows/` 与 `src/` 中的相关文件，以获取实现上下文；
   - 识别哪些用户故事需要测试、哪些可作为基础设施/前置任务、哪些可并行；
   - 按用户故事组织任务，并为每个阶段生成清晰的依赖顺序；
   - 校验任务完整性（每个用户故事必须具备足够任务，并且验收标准可独立测试）。

2. **生成 tasks.md**：使用 [.docusdd/templates/spec-tasks-template.md](/.docusdd/templates/spec-tasks-template.md) 作为结构，并填充：
   - 从 spec.md 获取正确的功能名称
   - 状态（已完成，正在实现，正在规划）
   - 类型（重构或建构，bug修复或代码测试，功能开发或修改）
   - 版本变更记录
   - 每个用户故事一个 phase（按 spec.md 的优先级顺序）
   - 每个 phase 包含：故事目标、独立测试标准、测试（如需要）
   - 需要遵守的规则或阻碍项（优先来自于`docus/constitution.md`中的规则）
   - 所有任务必须遵循严格的清单格式（见下方任务生成规则）
   - 每个任务给出明确的文件路径
   - Dependencies 部分展示故事完成顺序
   - 每个故事提供并行执行示例
   - 实现策略部分（MVP 优先、增量交付）

## 4.  checklist.md 文件生成或修改

参考 [.docusdd/templates/spec-checklist-template.md](/.docusdd/templates/spec-checklist-template.md) 的结构，生成或更新 `checklist.md`
checklist.md用于检验实现产物是否满足 spec.md 中的验收标准。它不是可有可无的附属文件，而是实现验收的一部分。你需要：
1. 把 `spec.md` 中的关键验收标准改写成可逐项检查的条目。
2. 在实现过程中会逐项打勾或标记失败原因。

## 5.  实现小型任务

如果生成的任务列表中包含 5 个或更少的任务，并且这些任务都属于同一个用户故事（即它们共享同一个 [US?] 标签），则可以直接执行这些任务，而无需调用 `DDD-implementor` 进入实现阶段。
执行完之后更新 `tasks.md` 中的任务状态。

## 6. 向用户输出最终摘要：
   - 需求定位：判定为“新需求”或“修改已有需求”，并给出对应目录 `specs/###-short-name/`（或实际目标目录）。
   - 关键产物：本次新增/更新的文件路径（至少包含 `spec.md`、`tasks.md`、`checklist.md`，以及 `specs/statistics.md` 的变更）。
   - 用户故事概览：从 `spec.md` 汇总 [US?] 列表与优先级（P1/P2/P3），并说明是否满足进入实现阶段（SUCCESS / ERROR）。
   - 需要澄清与默认假设：列出所有 `[NEEDS CLARIFICATION: ...]`（最多 3 条）与 Assumptions 的关键点。
   - 下一步执行建议：若任务数 ≤ 5 且同一 [US?]，说明已直接执行并更新 `tasks.md`；否则给出移交 `DDD-implementor` 的明确入口与目标目录。
   - 建议提交信息：新建需求用 `specs: add ###-short-name (spec + tasks + checklist)`；增量修改用 `specs: update ###-short-name (scope: <...>)`。



# 原则与参考

## 任务生成的具体判断顺序

AI 应当按下面顺序做决定，而不是直接开始写任务：
1. 先判断这是不是已有需求的增量修改；
2. 再判断 spec 中有几个用户故事、哪些故事是核心、哪些是支撑；
3. 再判断哪些任务必须先于实现完成（例如文档、数据模型、接口契约、测试）；
4. 再判断哪些任务可以并行（不同文件、不同故事、无依赖）；
5. 最后生成 `tasks.md`。

## 文件与模板来源

创建或更新规范文件时，必须明确参照仓库内模板：
- `spec.md` 的结构来源： [.docusdd/templates/spec-specs-template.md](../../.docusdd/templates/spec-specs-template.md)
- `tasks.md` 的结构来源： [.docusdd/templates/spec-tasks-template.md](../../.docusdd/templates/spec-tasks-template.md)
- `checklist.md` 的结构来源： [.docusdd/templates/spec-checklist-template.md](../../.docusdd/templates/spec-checklist-template.md)

AI 需要能清楚区分：
- 读取 `statistics.md` → 识别“新建”还是“修改已有需求”；
- 新建时 → 先分配序号、再建立目录、再写入三个文件；
- 修改时 → 直接定位到目标目录并更新现有内容。

如果需要更快确认上下文，优先使用以下脚本：
- [.docusdd/scripts/get_env_name.ps1](../../.docusdd/scripts/get_env_name.ps1)
- [.docusdd/scripts/check_specs_structure.ps1](../../.docusdd/scripts/check_specs_structure.ps1)
- [.docusdd/scripts/check_docus_structure.ps1](../../.docusdd/scripts/check_docus_structure.ps1)

## 快速指南

- 聚焦于用户需要 **什么** 与 **为什么**。
- 避免描述如何实现（不写技术栈、API、代码结构）。
- 面向业务相关方而非开发者撰写。
- 不要在 spec 中内嵌任何检查清单。清单将由后面生成。

## 参考链接

与 spec-kit 对应的参考命令：
- [spec-kit/templates/commands/specify.md](https://github.com/github/spec-kit/blob/main/templates/commands/specify.md)
- [spec-kit/templates/commands/tasks.md](https://github.com/github/spec-kit/blob/main/templates/commands/tasks.md)
- [spec-kit/templates/commands/plan.md](https://github.com/github/spec-kit/blob/main/templates/commands/plan.md)
- [spec-kit/templates/commands/analyze.md](https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md)


