# 智能体体系（与仓库中实际智能体一致）

本仓库当前包含三个主力智能体，下面按功能、输入/输出与边界进行简要说明，并标注与 spec-kit 的对应模板链接，方便对标与复用。

1) DDD-constitution-builder — 宪章/治理维护器 & 项目初始化器
- 目标：维护项目最高治理文档（`docus/constitution.md`）并负责项目初始化（建立仓库的标准文件夹与初始文档）。
- 主要职责：
  - 创建或更新宪章，填充模板占位符并决定语义化版本；
  - 生成同步影响报告并列出需人工跟进的 TODO；
  - 初始化项目骨架（在空仓或需要重置时复制 `.docusdd/templates` 中的模板到 `docus/`、创建 `specs/`、`specs/reports/`、`src/`、`tests/` 等目录并写入初始文件）；
  - 在宪章更新需要触发的情况下，列出/触发后续模板与命令（但不直接实现业务代码）。
- 相关脚本：
  - [.docusdd/scripts/check_docus_structure.ps1](../.docusdd/scripts/check_docus_structure.ps1)
  - [.docusdd/scripts/check_specs_structure.ps1](../.docusdd/scripts/check_specs_structure.ps1)
- 输入：仓库上下文（README、现有所有文件）、用户交互输入（修订或初始化指令）。
- 输出：更新或新建的 `docus/constitution.md`、初始化产生的目录/文件、同步影响报告与 TODO 清单。
- 边界：负责治理文档与初始化物料的创建/更新；若需要执行具体功能实现或测试，则交付 `DDD-require-explainer` 或 `DDD-implementor` 执行。
- 对标 spec-kit：与 spec-kit 的宪章/初始化相关命令思路相近，参考：[spec-kit/templates/commands/constitution.md](https://github.com/github/spec-kit/blob/main/templates/commands/constitution.md)

2) DDD-require-explainer — 需求/规格生成器（Specify & plan & Tasks）
- 目标：将自然语言需求或交互式输入转化为可执行的 `spec.md`（需求规范），并生成或更新 `tasks.md` 与 `checklist.md`。
- 主要职责：
  - 提取参与者/动作/数据/约束，生成短名称或识别目标 spec；
  - 根据上下文**创建新 spec 目录或修改已有 spec**（即：不强制总是新建目录，允许在既有需求上修改）；
  - 填写或更新 `spec.md`，并生成初版质量检查清单与 `specs/statistics.md` 条目。
- 输入：用户需求描述、仓库 Docus（constitution/structure）、可选的历史 `specs`。若用户指定某个已有 spec，则以该目录为修改目标。
- 输出：新建或已更新的 `specs/<feature>/spec.md`、`tasks.md`（初版或更新）、`specs/statistics.md` 更新条目。
- 边界：只产出或修改规格及其相关文档；当任务数较少且可执行时可直接执行小型实现，否则将任务移交 `DDD-implementor` 执行。
- 相关脚本：
  - [.docusdd/scripts/get_env_name.ps1](../.docusdd/scripts/get_env_name.ps1)
  - [.docusdd/scripts/check_specs_structure.ps1](../.docusdd/scripts/check_specs_structure.ps1)
  - [.docusdd/scripts/check_docus_structure.ps1](../.docusdd/scripts/check_docus_structure.ps1)
- 对标 spec-kit：主要对标 spec-kit 的 `specify` 与 `tasks` 命令，参考：
  - [spec-kit/templates/commands/specify.md](https://github.com/github/spec-kit/blob/main/templates/commands/specify.md)
  - [spec-kit/templates/commands/tasks.md](https://github.com/github/spec-kit/blob/main/templates/commands/tasks.md)
  - [spec-kit/templates/commands/plan.md](https://github.com/github/spec-kit/blob/main/templates/commands/plan.md)
  - [spec-kit/templates/commands/analyze.md](https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md)

3) DDD-implementor — 实现与执行器（Implementor）
- 目标：读取并执行 `tasks.md` 中定义的实现计划，完成代码实现、文档更新、测试与验收，并更新任务状态与检查清单。
- 主要职责：
  - 按 tasks 的阶段与依赖顺序执行任务；
  - 根据实现需要**修改或新增**依据来源文档（`docus/`）、源代码（`src/`）与测试（`tests/`）；
  - 生成或运行 `checklist.md`（实现验收清单），并在执行过程中更新其状态；
  - 在实现过程中回写并更新 `tasks.md` 的完成状态、产出测试报告与实现证明材料。
- 输入：`specs/*/tasks.md`（或 `specs/*/spec.md` 作为实现依据）以及仓库当前的文件结构与内容（`docus/`、`src/`、`tests/` 等现有文件）。实现器以这些现有产物为起点并在执行中进行必要更改。
- 输出：变更后的 `docus/` 文档、`src/` 代码变更、`tests/` ，以及更新 `tasks.md`、`checklist.md` 和 `specs/reports/` 中的报告。
- 边界：实现阶段必须遵循 `docus/constitution.md` 的治理原则；在遇到超出当前 spec 范围的设计决策或治理冲突时，应暂停并回交 `DDD-require-explainer` 或 `DDD-constitution-builder` 以取得明确指示。
- 额外说明：`DDD-implementor` 负责 `checklist` 的生成与运行（如同 `spec-tester` 的部分职责），并在需要时把测试、评估、检查和验收结果输出到 `specs/reports/`，因此 `checklist` 与 `reports` 功能都已并入实现流程。
- 相关脚本：
  - [.docusdd/scripts/get_env_name.ps1](../.docusdd/scripts/get_env_name.ps1)
  - [.docusdd/scripts/check_codefile_structure.ps1](../.docusdd/scripts/check_codefile_structure.ps1)
  - [.docusdd/scripts/check_specs_structure.ps1](../.docusdd/scripts/check_specs_structure.ps1)
  - [.docusdd/scripts/check_docus_structure.ps1](../.docusdd/scripts/check_docus_structure.ps1)
- 对标 spec-kit：对应 spec-kit 的 `implement` 与 `plan`、`analyze` 等命令，参考：
  - [spec-kit/templates/commands/implement.md](https://github.com/github/spec-kit/blob/main/templates/commands/implement.md)
  - [spec-kit/templates/commands/checklist.md](https://github.com/github/spec-kit/blob/main/templates/commands/implement.md)


说明：以上智能体说明以仓库中 `.github/agents/*.agent.md` 为准；若需要扩展额外专职智能体（如 consistency-checker、tester），在 `.github/agents/` 新增对应文件并在本文档追加简短描述即可。
- **适用性**: 复杂功能开发、大型架构重构、对代码质量和文档完整性有严格要求的任务。
