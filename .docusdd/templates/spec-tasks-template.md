---
description: "特性实现任务模板"
---

# 任务：[FEATURE NAME]

## 版本需求迭代（迭代特性必填）

- **基线版本**：[填写本次迭代所基于的版本、旧 spec 或已交付能力]
- **变更内容**：[填写相对基线版本的新增、修改、删除内容]

**输入**：来自 `/specs/[###-feature-name]/` 的设计文档  
**前置**：plan.md（必需）、specs.md（用户故事必需）、research.md、data-model.md、contracts/

**测试**：下例包含测试任务。测试为可选——仅当特性规范明确要求时包含。

**组织**：任务按“用户故事”分组，以便每个故事可独立实现与测试。

## 格式：`[ID] [P?] [Story] 描述`

- **[P]**：可并行（不同文件、无依赖）
- **[Story]**：该任务所属的用户故事（如 US1、US2、US3）
- 描述中应包含精确文件路径

<!-- 
  ============================================================================
  重要：以下任务仅为示例。
  /speckit.tasks 必须用真实任务替换它们，基于：
  - specs.md 中的用户故事与优先级
  - plan.md 中的特性需求
  - data-model.md 的实体
  - contracts/ 的端点
  任务必须按用户故事组织，以便独立实现/测试/MVP 交付。
  不要在生成的 tasks.md 中保留示例任务。
  ============================================================================
-->


# 模板

## 阶段 0：Constitution Alignment（宪章对齐）

**目的**：把宪章规则转为可执行任务，作为所有实现前置条件。

- [ ] T000 更新 `docus/` 或 `specs/` 对应文档后再开始实现（文档即代码）
- [ ] T000A 校验 `specs.md` 需求均具备可测试验收标准
- [ ] T000B 建立 `specs ↔ docus` 双向引用，并标注相关文档是“需求专属”还是“全局适用”
- [ ] T000C 校验目标 `src/` 文件或函数将补充依据来源自描述（引用对应 `docus/` 章节）
- [ ] T000D 校验运行环境约束（Windows/PowerShell；Python 项目需 my-uv + uv）
- [ ] T000E 预创建或确认报告输出路径 `specs/reports/`

---

## 阶段 0.5：Version Iteration（版本需求迭代，按需）

**目的**：把基线版本和变更内容拆分为可执行任务；若不是迭代需求，可整体删除本阶段。

- [ ] T000F 确认基线版本与追溯路径（如 `specs/[old-feature]/specs.md`、旧报告、已发布文档）
- [ ] T000G 梳理 `specs.md` 中的变更内容，并确认与旧版本差异一致
- [ ] T000H [P] 更新受影响的文档、任务和验收引用，确保版本描述一致

---

## 阶段 1：Setup（共享基础设施）

**目的**：项目初始化与基础结构

- [ ] T001 按实施计划创建项目结构
- [ ] T002 初始化 [language] 项目并安装 [framework] 依赖
- [ ] T003 [P] 配置 Lint 与格式化工具

---

## 阶段 2：用户故事 1 - [标题]（优先级：P1）🎯 MVP

**目标**：[此故事交付内容]

**独立测试**：[如何单独验证]

### 用户故事 1 的测试（可选，若有请求）⚠️

> 先编写测试并确保在实现前失败

- [ ] T010 [P] [US1] 合约测试 tests/contract/test_[name].py
- [ ] T011 [P] [US1] 集成测试 tests/integration/test_[name].py

### 用户故事 1 的实现

- [ ] T001 [P] 更新设计文档 docus/layers/[layer]#2.1预处理.md
更新预处理使得加入对于光谱长度的限制,限制光谱区间为300-1500
- [ ] T002 [P] 更新设计文档 docus/workflows/[workflow].md
更新设计文档使得数据流转加入预处理后的数据，类型为:np.array
- [ ] T003 [P] 更新结构文档 docus/structure.md
新增文档：docus/layers/utils/README.md
- [ ] T004 [P] 更新微观文件 `src/utils/preprocessor.py` 的自描述
添加主要职责:强调统一公共入口 `preprocess_pipeline(X, wavelengths, config) -> (X_new, wavelengths_new)`与重复性评估公共入口 `evaluate_repetition(X, sample_indices=None, eps) -> float`
- [ ] T005 [P] 依据文档在 `src/utils/preprocessor.py` 里面实现`preprocess_pipeline`与`evaluate_repetition`函数

检查点：用户故事 1 可独立完整运行并可测试

[按需添加更多故事阶段，复用上述模式]

---

## 阶段 N：Polish 与横切关注点

**目的**：影响多个用户故事的改进

- [ ] TXXX [P] 更新文档 docus/
- [ ] TXXX 代码清理与重构
- [ ] TXXX 全局性能优化
- [ ] TXXX [P] 追加单元测试 tests/unit/（若有请求）
- [ ] TXXX 安全加固
- [ ] TXXX 运行 quickstart.md 校验

---

## 备注

- [P] 任务：不同文件、无依赖  
- [Story] 标签：用于可追溯性映射到用户故事  
- 版本迭代任务应优先覆盖“基线确认、变更拆解、文档回写”。  
- 每个用户故事应可独立完成与测试  
- 实现前先确保测试失败  
- 每个任务/逻辑组后提交  
- 可在任一检查点暂停并独立验证  
- 避免：模糊任务、同文件冲突、破坏故事独立性的跨故事依赖
