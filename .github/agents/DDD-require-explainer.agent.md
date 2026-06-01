---
description: 根据自然语言的功能描述创建或更新功能规格说明（spec）,并进行修改规划
handoffs: 
  - label: implement large-scale modifications, including specific execution of document or code structure changes and code testing.
    agent: DDD-implementor
    prompt: 为该规格创建计划。 我将使用...
  - label: consistency check for specs, documents and src
    agent: DDD-consistency-checker
    prompt: 检验文档与代码结构的一致性。重点在...

---
## 用户输入

```text
$ARGUMENTS
```

你 **必须** 在继续之前先考虑用户输入（如果不为空）。

## 1. 判断是否属于之前的需求

1. 如果用户明确指明属于之前未完成的需求，并指明了需求名称和文件夹，则跳过第2步的specs.md文件生成，直接修改。
2. 如果没有指明但是属于很小的需求或者之前的需求，先加载./specs/statistics.md，找到与用户输入最相关的需求（可以通过关键词匹配、语义相似度等方式），合并到其中，跳过第二步的文件生成，直接修改。

## 2. specs.md 文件生成或修改

### 大纲

触发消息中，用户在 `/speckit.specify` 后输入的文本 **就是** 功能描述。即使下面字面出现 `$ARGUMENTS`，也假设你始终能在本次对话中拿到该描述。除非用户给了空命令，否则不要让用户重复输入。

基于该功能描述，执行以下步骤：

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

3. 将序号和简要介绍写入 ./specs/statistics.md: 记录生成的简短名称、提取的关键概念以及给这个需求排上序号

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

5. 建立相应的文件夹和文件，命名为 `./specs/###-short-name/`，其中 `###` 是上一步中分配的序号，`short-name` 是第 1 步生成的简短名称。文件夹内必须包含：
   - `spec.md`：功能规格说明
   - `tasks.md`：实现规划与任务列表以及检查要求（初始可空）
   - `checklist.md`：验收标准检查清单（初始可空）

### 快速指南

- 聚焦于用户需要 **什么** 与 **为什么**。
- 避免描述如何实现（不写技术栈、API、代码结构）。
- 面向业务相关方而非开发者撰写。
- 不要在 spec 中内嵌任何检查清单。清单将由后面生成。


## 3. tasks.md 文件生成或修改

### 大纲

3. **执行任务生成工作流**：
   - 加载 spec.md 并提取用户故事及其优先级（P1、P2、P3 等）
   - 加载 `docus/structure.md` 和 `docus/constitution.md` 以了解当前项目架构与原则
   - 依据需要加载相应docus文件或源代码src以获取实现上下文
   - 按用户故事组织生成任务（见下方任务生成规则）
   - 生成依赖图，展示用户故事完成顺序
   - 校验任务完整性（每个用户故事具备所需任务，且可独立测试）

4. **生成 tasks.md**：使用 `.docusdd/templates/tasks-template.md` 作为结构，并填充：
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

任务生成上下文：$ARGUMENTS 

tasks.md 应当可立即执行——每个任务必须足够具体，使得 LLM 无需额外上下文即可完成。

### 任务生成规则

**关键要求**：任务必须按用户故事组织，以支持独立实现与测试。

**测试为可选项**：仅当功能规格中明确要求，或用户要求采用 TDD 方法时，才生成测试任务。

### 清单格式（必需）

每个任务都必须严格遵循以下格式：

```text
- [ ] [TaskID] [P?] [Story?] 带文件路径的描述
```

**格式组件**：

1. **复选框**：始终以 `- [ ]` 开始（Markdown checkbox）
2. **任务 ID**：按执行顺序递增编号（T001、T002、T003...）
3. **[P] 标记**：仅当任务可并行时才包含（涉及不同文件，且不依赖未完成任务）
4. **[Story] 标签**：仅用于用户故事 phase 的任务，且为必需
   - 格式：[US1]、[US2]、[US3] 等（映射到 spec.md 的用户故事）
   - Setup phase：不加 story 标签
   - Foundational phase：不加 story 标签
   - User Story phases：必须有 story 标签
   - Polish phase：不加 story 标签
5. **描述**：清晰动作 + 精确文件路径

**示例**：

- ✅ 正确：`- [ ] T001 Create project structure per implementation plan`
- ✅ 正确：`- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ 正确：`- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ 正确：`- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ 错误：`- [ ] Create User model`（缺少 ID 与 Story 标签）
- ❌ 错误：`T001 [US1] Create model`（缺少复选框）
- ❌ 错误：`- [ ] [US1] Create User model`（缺少任务 ID）
- ❌ 错误：`- [ ] T001 [US1] Create model`（缺少文件路径）


## 4. 实现小型任务

如果生成的任务列表中包含 5 个或更少的任务，并且这些任务都属于同一个用户故事（即它们共享同一个 [US?] 标签），则可以直接执行这些任务，而无需调用DDD-implementor进入实现阶段。
执行完之后更新 task.md中的任务状态.



