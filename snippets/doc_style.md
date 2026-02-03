### 1. 规范驱动开发原则
即实行 **文档驱动开发**：规范文档不仅是开发的指导，更是代码的直接依据。
具体执行标准（**由宏观到微观的层级化规范**）：
**项目规范和需求文档文件夹路径固定为 `./SpecMd`**

**需求迭代** (`Specify.md`): 唯一的需求变更源与版本控制中心。

#### Level 1: 宏观架构与全局控制 (Global Scope)
- **项目架构** (`Structure.md`): 包含项目目标、架构设计、技术栈及模块职责。
- **通用准则** (`ProjectRules.md`): 全局适用的代码编写规则与底线。

#### Level 2: 模块协作与层级规范 (Module & Layer Scope)
- **流程与交互** (`./SpecMd/workflows/`): 定义模块间的工作流及数据流转规范。
- **层级实现** (`./SpecMd/layers/`): 针对特定代码层（如数据层、模型层）的详细说明文档。
- **智能体检查报告** (`./SpecMd/agents/`): 存放各智能体的检查结果、状态报告及自动化生成的日志。
- **其他规范** (`./SpecMd/others/`): 依据项目变化而变化的特殊规范文档（如配置文件规范、临时脚本规范）。

#### Level 3: 微观文件实现 (File Scope)
- **文件自描述**: 源代码文件头部的注释即为该文件的“需求文档”。

---

### 文档格式规范 (Document Format Templates)

所有 `SpecMd/` 下的子目录文档必须遵循以下特定模板：

#### 1. 层级实现文档模板 (`layers/*.md`)
```markdown
# [Layer Name] 层规范

## 1. 目的与范围 (Purpose & Scope)
- 说明该层解决什么问题，包含哪些模块。

## 2. 代码结构与文件组织 (Structure)
- 列出核心文件及其职责。

## 3. 数据结构与流转 (Data Flow)
- **输入**: 格式、来源。
- **输出**: 格式、去向。
- **内部状态**: 关键变量或类属性。

## 4. 验证规则 (Validation Rules)
- 详细说明数据校验逻辑（如 ID 掩码一致性）。
- **约束**: 必须遵守的硬性限制。

## 5. 集成要点 (Integration)
- 依赖哪些上游层？被哪些下游层调用？
```

#### 2. 工作流文档模板 (`workflows/*.md`)
```markdown
# [Workflow Name] 流程规范

## 1. 流程概述 (Overview)
- 简述该业务流程的目标。

## 2. 流程图 (Flowchart)
- 使用 Mermaid 语法绘制流程图。
mermaid
graph TD
    A[Start] --> B{Condition}
    B -- Yes --> C[Action]
    B -- No --> D[End]

## 3. 步骤详解 (Step-by-Step)
- **Step 1**: [步骤名称]
    - 输入: ...
    - 处理逻辑: ...
    - 输出: ...

## 4. 异常处理 (Exception Handling)
- 定义流程中可能出现的错误及恢复策略。
```

#### 3. 智能体报告模板 (`agents/*.md`)
```markdown
# [Agent Name] 检查报告

## 1. 检查元数据 (Metadata)
- **时间**: YYYY-MM-DD HH:MM
- **执行人**: [Agent Name]
- **目标**: [检查对象，如 Specify.md 或 src/]

## 2. 检查结果摘要 (Summary)
- **状态**: [Pass / Fail / Warning]
- **发现问题数**: N

## 3. 详细问题清单 (Issues)
- [ ] [Critical] 文件 X 缺少头部注释。
- [x] [Warning] 函数 Y 参数未注明类型。

## 4. 修正建议 (Suggestions)
- 针对发现的问题给出具体修改建议。
```

#### 4. 其他规范模板 (`others/*.md`)
```markdown
# [Topic] 规范

## 1. 背景 (Context)
- 为什么需要这个额外的规范？

## 2. 规范定义 (Definition)
- 具体的规则列表（如 JSON 字段定义、环境变量列表）。

## 3. 示例 (Examples)
- 提供具体的代码或配置片段示例。
```
