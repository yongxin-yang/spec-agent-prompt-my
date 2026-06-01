# 宪章摘录（默认，来源：.docusdd/templates/docu-constitution-template.md）
<!-- 文档即代码；可执行规范；单一事实来源；AI 工具链与极简可观测性 -->

# 实施计划：[FEATURE]

**分支**：`[###-feature-name]` | **日期**：[DATE] | **规范**：[link]  
**输入**：来自 `/specs/[###-feature-name]/spec.md` 的特性规范

说明：此模板由 `/DDD-` 填充。执行流程见 `.specify/templates/commands/plan.md`。

## 宪章检查（必填）

<!--
  需操作：在开始结构设计前，先核对 docus/constitution.md。
  最少给出以下结论：
  - 文档即代码：本次结构变更是否先完成文档更新。
  - 单一事实来源：本模板中的结构是否与 docus/、specs/ 约束一致。
  - 可执行规范：是否能映射到 spec/tasks/checklist/report。
  - 环境与测试纪律：是否定义 tests/ 与 specs/reports/ 的对应关系。

  示例：
  - 引用条款：I 文档即代码；III 单一事实来源；VI 环境与测试纪律
  - 结果：通过（无冲突）
-->

# 项目介绍
## [PROJECT_GOAL_1]
<!-- 示例： 1. 最终项目目标-->
[PROJECT_GOAL_1_DESCRIPTION]
<!-- 示例：
1.标准化原始数据[多维(wavelenth,x)对多维y],不支持图像处理
2.机器学习,即利用统计学方法训练一个回归,聚类或分类模型
3.进行实际操作,解决实际问题
-->

## 技术上下文

<!--
  需操作：将此处替换为项目技术细节；结构仅作建议以引导迭代。
-->

**语言/版本**：[如 Python 3.11、Swift 5.9、Rust 1.75 或 NEEDS CLARIFICATION]  
**主要依赖**：[如 FastAPI、UIKit、LLVM 或 NEEDS CLARIFICATION]  
**存储**：[若适用，如 PostgreSQL、CoreData、文件 或 N/A]  
**测试**：[如 pytest、XCTest、cargo test 或 NEEDS CLARIFICATION]  
**目标平台**：[如 Linux、iOS 15+、WASM 或 NEEDS CLARIFICATION]
**项目类型**：[single/web/mobile —— 决定源码结构]  
**性能目标**：[领域相关，如 1000 req/s、10k lines/sec、60 fps 或 NEEDS CLARIFICATION]  
**约束**：[领域相关，如 p95 <200ms、内存 <100MB、离线可用 或 NEEDS CLARIFICATION]  
**规模/范围**：[领域相关，如 1 万用户、100 万行代码、50 个界面 或 NEEDS CLARIFICATION]

## 运行环境

<!--
  需操作：若项目采用 Python，则默认遵循以下环境规则；若项目有自己的结构文档，可在 docus/structure.md 中进一步细化并覆盖说明。
  示例：
  - 操作系统：Windows。
  - 终端环境：PowerShell。
  - Python 环境管理：使用 my-uv 统一管理虚拟环境，不直接使用标准 venv 命令。
  - 环境名：优先读取 `$env:PROJECT_ENV_NAME`；若未设置，则运行 `.docusdd/scripts/get_env_name.ps1` 获取/写入。
  - 激活顺序：执行 Python 任务前必须先 `my-uv activate $env:PROJECT_ENV_NAME`。
  - 依赖同步：使用 `uv sync` 同步依赖；使用 `uv add`/`uv remove`/`uv lock`/`uv export` 管理锁定与导出。
  - 运行方式：优先在已激活环境中直接执行 `python`；必要时使用 `uv run python <script>`。
  - 环境检查：在编写或运行代码前确认环境已激活且依赖完整。
-->
- **操作系统**: Windows
- **终端环境**: PowerShell
- **包与环境管理**:
        - **Python**: 使用自制uv扩展 `my-uv` 进行环境管理.
            - **注意**: 本项目依赖 `my-uv` 提供的统一命令来管理虚拟环境, 请勿直接使用标准 `venv` 命令.
            - **项目环境名称**: 优先使用终端环境变量 `$env:PROJECT_ENV_NAME`；若未设置则点源 `/.docusdd/scripts/get_env_name.ps1` 写入后使用。
            - **激活环境**: 执行 python 任务前**必须**先激活此环境：`my-uv activate $env:PROJECT_ENV_NAME`.
        - **扩展命令参考**:
            - `my-uv activate <name>` (别名 `a`): 激活指定名称的虚拟环境.
            - `my-uv new <name> [python]` (别名 `n`): 创建新环境 (支持指定版本).
            - `my-uv list` (别名 `l`): 列出本机所有由 my-uv 管理的虚拟环境.
            - `my-uv delete <name>` (别名 `del`): 删除环境.
            - `my-uv deactivate` (别名 `d`): 停用当前环境.
        - **依赖管理**: 读取 `pyproject.toml` 获取依赖列表 (遵循标准 uv/pep621 规范).
        - **依赖包管理 (使用 `uv`)**:
            - `uv sync`: 根据 `pyproject.toml` 与锁文件同步并安装依赖到已激活环境。
            - `uv add <package> [==version] [--dev]`: 添加依赖并更新锁文件, 随后同步安装。
            - `uv remove <package>`: 从项目依赖中移除并更新锁文件与环境。
            - `uv lock [--upgrade]`: 生成/更新锁文件; 使用 `--upgrade` 全量升级到最新兼容版本。
            - `uv export -o requirements.txt`: 导出当前锁定依赖为 `requirements.txt` 以供外部复现。
            - `uv run python <script>`: 在项目依赖上下文中运行脚本 (可选; 常规用法为激活环境后直接执行 `python`)。
        - **使用顺序建议**:
            - 若 `$env:PROJECT_ENV_NAME` 未设置，先点源 `/docusdd/scripts/get_env_name.ps1`，再执行 `my-uv activate $env:PROJECT_ENV_NAME`，最后执行 `uv ...` 命令。
            - 运行时依赖与开发依赖分离: 使用 `uv add --dev <package>` 添加仅开发场景需要的依赖。
            - 项目以 `pyproject.toml` 为单一依赖声明源; 锁文件控制具体解析版本, 保证可复现安装。
        - **详细文档**: `UVExtenIntro`文件夹下内容.
        - **扩展特点**: 统一命令行入口 `my-uv`, 环境物理路径与项目分离.
- **环境检查**: 每次编写或执行代码前, 必须确认虚拟环境已激活且依赖包完整.


## 项目结构

### 规范驱动文档

```text
specs/scripts/ 脚本工具等
specs/statistics.md 索引所有需求，标号并写简要概述
specs/reports/ 实现、测试、评估、检查、验收与环境验证报告
specs/[###-feature]/
├── specs.md             # require-explainer 输出 该需求的简洁的自然语言描述
├── checklist.md          # tester 输出 
└── tasks.md             # require-explainer 输出 具体实现规划以及实现状态和测试规划
```
### 依据来源文档
<!--
  需操作：将下方占位树替换为具体结构；删除未选项；保留真实路径，并在每一个文件夹或文件后做简要注释
-->
```text
docus/ 依据来源文档
|── workflows
│   └── workflow.md 工作流文件，明确数据流转格式等
└── others
│   ├── InputDataset.md
│   ├── OutputImage.md
│   └── OutputParadigm.md
└── layers 分层与模块的文件或文件夹(如果代码结构是多层嵌套的)，注明每个层的作用以及相互之间的交互逻辑
│   ├── README.md 所有这一层的文件的分工职责总介绍以及相互之间的数据传递格式等
│   ├── Explainability.md
│   └── 2utils utils层规范
        ├── README.md
        └── algorithm.md 算法规范 -- 数学上的唯一实现
│   ├── 1tools.md tools层规范
│   ├── 3datamodels.md
│   ├── 4JsonConfig.md
│   ├── 5processcenter.md
│   └── 6scripts.md
└── structure.md 项目结构，项目目标、架构设计、技术栈及模块职责
└── constitution.md 最高的规则与规范
```

### 源码（仓库根）
<!--
  需操作：将下方占位树替换为具体结构；删除未选项；保留真实路径。
-->

```text
# [若未使用请删除] 选项 1：单项目（默认）
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [若未使用请删除] 选项 2：Web 应用（检测到 frontend + backend 时）
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [若未使用请删除] 选项 3：移动端 + API（检测到 iOS/Android 时）
api/
└── [同上 backend]

ios/ 或 android/
└── [平台结构：特性模块、UI 流程、平台测试]
```

**结构决策**：[记录所选结构并引用上述真实目录]

## 复杂度跟踪

仅当“宪章检查”存在需被合理化的违规时填写：

| 违规 | 为什么需要 | 更简单替代被拒原因 |
|------|------------|---------------------|
| [如第 4 个项目] | [当前需要] | [为何 3 个项目不够] |
| [如 Repository 模式] | [具体问题] | [为何直接 DB 访问不够] |
