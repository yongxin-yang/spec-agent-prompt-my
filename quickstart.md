## 快速入口

- 架构与治理见 [structures](./structures)
- 智能体定义见 [.github/agents](./.github/agents)
- 辅助脚本见 [.docusdd/scripts](./.docusdd/scripts)
- 模板见 [.docusdd/templates](./.docusdd/templates)

## 推荐工作流

1. 先看 `structures/` 里的架构、原则与智能体体系。
2. 需要初始化或修订治理时，使用 `DDD-constitution-builder`，并确保宪章变更已传播到 `.docusdd/templates/`、`.github/agents/`、`README.md`、`quickstart.md`。
3. 需要生成或修改需求时，使用 `DDD-require-explainer`，它会先判断是新需求还是已有需求修改，并更新 `specs/statistics.md`。
4. 需要实现、测试、评估或检查时，使用 `DDD-implementor`，它会更新 `docus/`、`src/`、`tests/`、`tasks.md`、`checklist.md`，并把报告写入 `specs/reports/`。

## 常用脚本

- `get_env_name.ps1`：读取或写入当前项目环境名。
- `check_codefile_structure.ps1`：查看 `src/` 结构。
- `check_specs_structure.ps1`：查看 `specs/` 结构。
- `check_docus_structure.ps1`：查看 `docus/` 结构。

## 模板约定

- `spec-specs-template.md`：需求规范模板
- `spec-tasks-template.md`：任务模板，按 Setup / Foundational / 用户故事 / Polish 组织
- `spec-checklist-template.md`：实现验收清单模板
- `spec-report-template.md`：测试、评估、检查与验收报告模板

## 目录约定

- `specs/`：每个特性一个目录，包含 `spec.md`、`tasks.md`、`checklist.md`
- `specs/reports/`：所有执行报告、测试报告、评估报告的统一输出位置
- `docus/`：长期稳定的依据来源文档
- `src/`：实现代码
- `tests/`：测试与验证脚本

