# DDD 的目标

DDD 试图结合 SDD(specify driven development) 和 vibe coding 的优势：

* 保留 Vibe Coding 的探索能力
* 保留 SDD 的结构化流程
* 建立长期可维护的知识体系
* 实现 AI 与文档协同开发

DDD 的核心观点是：

> 文档不是代码的说明书，而是系统本身。

代码只是文档的一种实现形式。

---

# 核心原则

## 核心理念
- **文档即代码 (Docs as Code)**: 规范文档不是事后补充的说明，而是代码的直接前置条件。
- **让规范可执行 (Executable Specs)**: 需求文档应直接转化为可验证的代码实现。
- **单一事实来源 (Single Source of Truth)**: `SpecMd` 目录是项目需求的唯一真理来源。

## 文档是唯一事实来源

系统行为由文档定义。
代码必须符合文档。
测试必须验证文档。
任何变更都必须首先修改文档。

## AI 面向文档编程

开发者主要查看、维护**依据来源文档**。
AI 负责：
* 规范驱动
* 按照开发者指令修改**依据来源文档**
* 代码实现
* 测试生成
* 一致性检查
开发者关注： 系统应该是什么
AI 关注： 系统如何实现

## DDD的项目架构(project strcture)

- specs/ **规范驱动文档**
 - `SPEC_ORDER`/
  - specs.md 该需求的简洁的自然语言描述
  - tasks.md 该需求的具体实现规划以及实现状态和测试规划
  - checklist.md 该需求的一致性和测试性检查清单以及状态
 - scripts/ 脚本工具等
 - reports/ 该需求或实现过程的测试、评估、检查、验收与环境验证报告
 - statistics.md
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
- pyproject.toml (可选,如果是python项目)
- README.md (可选,项目说明文档)
- quickstart(可选，方便项目快速启动)

## 开发流程(workflows)
协作与工作流（简要）
- 典型流水线：
  1. 用户提出模糊需求 → 调用 `DDD-require-explainer` 生成/更新 `spec.md`。
  2. `DDD-require-explainer` 生成 `tasks.md` 并标注依赖与优先级；若任务量小且独立，可直接进入实现。
  3. 对于需要实现的任务，调用 `DDD-implementor` 执行并在完成后回写 `tasks.md` 与 `checklist.md`。
  4. 若变更触及治理层面或规则更新，调用 `DDD-constitution-builder` 进行宪章修订并同步模板。


## 依据来源文档(/docus/)简要叙述
- **Level 1: 宏观架构 (Global Scope)**
    - `Structure.md` (项目架构) 与 `constitution.md` (通用准则) 控制全局。
- **Level 2: 模块协作 (Module & Layer Scope)**
    - `/SpecMd/workflows/` (流程) 与 `/SpecMd/layers/` (层级) 定义具体实现逻辑。
- **Level 3: 微观实现 (File Scope)**
    - **文件自描述**: 源代码文件的头部注释即为该文件的微观需求文档。

## 规范驱动文档(/Specs/)简要叙述
规范驱动文档（Specs）是 DDD 的执行层，用于记录“现在要做什么”——它直接驱动实现、测试与验收。Specs 应当短期可变、面向当前迭代，并与长期的依据来源文档（`docus/`）保持一致。Specs 目录默认位于项目根的 `specs/` 下，每个功能应有独立的特性文件夹（例如：`specs/003-user-auth/`），包含三个核心文件：

- `spec.md`：需求说明（Task Title、Step-by-Step Implementation Roadmap、Detailed Requirements、接口定义、验证标准、Iteration History）。写作要点：面向业务/产品，避免实现细节；每条需求必须可测试并包含明确的 Success Criteria。
- `tasks.md`：实现计划与任务清单（按阶段组织：Setup、Foundational、User Stories、Polish）。每个任务应遵循清单格式（示例：`- [ ] T001 [P] [US1] Implement User model in src/models/user.py`），并标注依赖与并行性。
- `checklist.md`：验收与一致性检查清单，用于在实现后验证产物是否满足 `spec.md` 中的验收标准。

此外，`specs/` 下还需要保留 `reports/` 目录，用于归档实现过程中的测试报告、评估报告、检查报告、验收报告与环境验证报告。它与 `checklist.md` 的区别是：`checklist.md` 负责逐项检查，`reports/` 负责保存完整输出。

补充项：
- `scripts/`：与该 spec 相关的辅助脚本（例如数据准备、环境检查）。
- `statistics.md`：全局索引与序号管理，映射 spec 目录与简要说明。

生命周期与工作流：
- 典型流程：`Specify` → `Plan` → `Tasks` → `Implement` → `Test/Checklist` → `Close`。
- 创建与修改：`DDD-require-explainer` 可用于生成或更新 `spec.md`；`DDD-implementor` 执行 `tasks.md` 并在实现过程中更新 `checklist.md`、`specs/reports/` 与任务状态。若变更触及治理条款或需要初始化项目结构，可调用 `DDD-constitution-builder`。
- 版本与状态：每个 spec 应包含状态字段（例如：`Draft/Planned/In Progress/Blocked/Done`）与迭代历史（时间戳 + 变更摘要），以确保可追溯性。

编写规范（最低准则）：
- 面向“是什么”与“为什么”，避免“如何实现”。
- 每条需求具备可验证的验收标准（量化指标或明确文件/行为输出）。
- 必要时在 `Assumptions` 中显式列出合理默认值。
- 限制澄清标记：当关键信息缺失时使用 `[NEEDS CLARIFICATION: question]`（建议最多 3 项），并将其优先级记录在 `spec.md` 顶部。

自动化与一致性：
- 使用 `.docusdd/templates/` 下的模板初始化 `spec.md` / `tasks.md` / `checklist.md`，并把实现测试、评估和检查报告存入 `specs/reports/` 以便审计。
- CI 应将 `checklist.md` 的关键项纳入自动化验证，确保实现与 spec 的 1:1 对齐。

与依据来源文档（`docus/`）的关系：
- `docus/` 保持长期不变的领域模型、系统结构与治理原则；`specs/` 负责当下可执行的实现计划。所有对系统设计/边界的实质性更改，必须先更新 `docus/structure.md` 或 `docus/constitution.md`，并在 `spec.md` 中引用相应版本/条款。





