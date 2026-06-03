---
description: 通过处理并执行 tasks.md 中定义的全部任务来执行实现计划
---

## 用户输入

```text
$ARGUMENTS
```

你 **必须** 在继续之前先考虑用户输入（如果不为空）。

## 执行前检查

先把实现目标和边界看清楚，再开始改文件。

1. 找到目标 `specs/<feature>/` 目录，读取其中的 `specs.md`、`tasks.md` 和 `checklist.md`。
2. 读取仓库根目录下的 `docus/constitution.md` 和 `docus/structure.md`，把它们作为实现时的最高约束与架构地图。
3. 如果 `tasks.md` 指向了某个模块层或工作流层，再读取 `docus/layers/` 与 `docus/workflows/` 中的相关文件。
4. 再看当前的 `src/`、`tests/` 和相关文件头注释，确认已有结构、边界和依赖关系。

建议在启动实现前，先运行这些脚本快速确认现状：
- [.docusdd/scripts/get_env_name.ps1](../../.docusdd/scripts/get_env_name.ps1)：确认当前虚拟环境名，便于执行测试或环境验证。
- [.docusdd/scripts/check_codefile_structure.ps1](../../.docusdd/scripts/check_codefile_structure.ps1)：查看 `src/` 结构。
- [.docusdd/scripts/check_specs_structure.ps1](../../.docusdd/scripts/check_specs_structure.ps1)：查看 `specs/` 结构。
- [.docusdd/scripts/check_docus_structure.ps1](../../.docusdd/scripts/check_docus_structure.ps1)：查看 `docus/` 结构。

本智能体不是“只改代码”的执行器，而是会同时更新与实现相关的 `docus/`、`src/`、`tests/`、`tasks.md` 与 `checklist.md`。


## 大纲

流程与职责说明： 你正在执行 `tasks.md` 中定义的实现计划。该文件通常包含一个或多个用户故事（以 `[US?]` 标签标识）以及与之相关的任务列表。你的职责是：(a) 逐条执行任务，(b) 在执行过程中更新 `tasks.md` 中每个任务的状态，维护 `checklist.md`，并且 (c) 在完成所有任务后将用户故事标记为已完成。

**注意**：当任务属于测试、评估、检查、验收、真实性环境验证或报告输出时，`DDD-implementor` 还会启用可选流程，此时直接跳到可选流程

### 1. 先读清楚再动手

1. 读取 `specs.md`，确认功能目标、范围、验收标准和用户故事。
2. 读取 `tasks.md`，确认阶段、依赖、并行任务和测试任务。
3. 读取 `docus/constitution.md`，确认治理原则、边界、命名和文档同步要求。
4. 读取 `docus/structure.md`，确认系统模块、目录映射、职责边界与已有架构。
5. 必要时读取 `docus/layers/`、`docus/workflows/` 与 `src/` 中相关文件，搞清楚现有实现点。

### 2. 按依赖顺序执行文档与实现

先判断这个任务会影响哪些层，再决定要改哪些文件：

1. **如果任务会改变项目结构、模块边界或设计原则**
	- 先修改 `docus/structure.md` 或 `docus/constitution.md`。
	- 如果新增了层级或流程文档，使用 [.docusdd/templates/docu-template.md](../../.docusdd/templates/docu-template.md) 创建新文档。
	- 再回到 `tasks.md`，把对应的文档更新任务标记为完成。

2. **如果任务会改变某个层或工作流的规则**
	- 修改对应的 `docus/layers/` 或 `docus/workflows/` 文档。
	- 让文档先表达清楚规则、边界、输入输出和约束，再开始改 `src/`。

3. **如果任务只影响实现文件**
	- 读取相关 `src/` 文件头注释，按文件层规范直接修改实现。
	- 同步检查相关测试文件，必要时更新或补充测试。

4. **如果任务涉及新增文件或目录**
	- 先确认 `docus/structure.md` 是否需要增加目录映射说明。
	- 再创建新文件并补足头部注释、接口说明与依赖说明。

### 3. 修改 checklist.md 和 tasks.md 等文件的状态

如果任务实现，就在 `tasks.md` 中对应项的状态上打勾
如果测试通过，就在 `checklist.md` 中对应项的状态上打勾
如果测试失败，就在 `checklist.md` 中对应项的状态上标记失败原因

### 4. 向用户输出最终摘要：
   - 目标规格：对应的 `specs/<feature>/` 目录与需求名称（从 `specs.md` 获取）。
   - 完成情况：已完成/未完成的用户故事（[US?]）列表，以及各自的验收结果结论（通过/失败/阻塞）。
   - 变更清单：本次修改/新增的关键文件路径集合（按 `docus/`、`src/`、`tests/`、`specs/<feature>/`、`specs/reports/` 分组列出）。
   - 验证证据：执行过的测试/检查命令与结果；若生成报告，给出 `specs/reports/<...>.md` 的路径。
   - 风险与遗留：仍需手动跟进的事项（外部依赖、环境问题、未决设计、TODO）及对应文件位置。
   - 建议提交信息：按变更性质选择 `feat:` / `fix:` / `refactor:` / `test:` / `docs:`，并包含特性名与关键范围（例如：`feat: implement <feature> (docs + tests)`）。

### 可选流程

当任务属于测试、评估、检查、验收、真实性环境验证或报告输出时，`DDD-implementor` 还会启用可选流程：

1. 先确认是需要“写测试、跑测试、做评估、做检查”中的哪一种或哪几种。
2. 依据任务目标选择合适的动作组合：
	- 编写或补充 `tests/` 下的测试文件；
	- 运行已有测试或新增测试；
	- 做静态检查、人工一致性检查或环境验证；
	- 汇总测试结果、检查结果和结论。
3. 把执行过程中的关键结论统一输出到 `specs/reports/` 下对应的报告文件中，reports职责见下文.
。
4. 若任务已经在 `checklist.md` 中定义了验收项，则同时更新 `checklist.md` 的状态。

`specs/reports/` 是专门用于实现报告、测试报告、环境验证报告、评估报告和检查报告的目录。它不是替代 `checklist.md`，而是用来保存更完整的执行产物和最终结论。

#### reports-职责

`specs/reports/` 用于承载实现过程中的正式报告文件。通常在以下场景写入：

1. 测试任务：记录测试命令、覆盖范围、通过/失败结果和失败原因。
2. 评估任务：记录评估标准、样本范围、评分结论和偏差说明。
3. 检查任务：记录一致性检查、环境检查、文件检查或真实性校验的结果。
4. 验收任务：记录最终验收结论、残留风险和建议后续动作。

报告文件应放在 `specs/reports/` 下，按功能特性或任务编号进行组织，避免散落在 `tests/` 中。`tests/` 继续只放测试代码和测试辅助脚本。

参考报告模板：[.docusdd/templates/spec-report-template.md](/.docusdd/templates/spec-report-template.md)。


## 规定与要求
### 1. 代码、测试与文档的协同执行

执行顺序通常是：文档 → 结构 → 实现 → 测试 → 回写任务状态。

1. 先完成文档层面必要的修改。
2. 再改 `src/` 中的实现。
3. 再改 `tests/` 中的测试或验证脚本。
4. 最后更新 `tasks.md` 和 `checklist.md` 的状态。

### 2. 输出边界

- 输入不是“只有 spec 和 tasks”，而是 `specs.md`、`tasks.md`、`checklist.md`、`docus/`、`src/`、`tests/` 以及这些目录中的现有结构。
- 输出也不只是代码，而是对 `docus/`、`src/`、`tests/`、`tasks.md`、`checklist.md` 和 `specs/reports/` 的联合更新。
- 如果遇到超出 spec 的新需求、设计冲突或职责重叠，先停止并回交 `DDD-require-explainer` 或 `DDD-constitution-builder`。
