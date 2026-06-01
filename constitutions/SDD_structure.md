# 项目架构与文件叙述

## DDD的项目架构(project strcture)

- specs/ **规范驱动文档**
 - `SPEC_ORDER`/
  - specs.md 当前未完成的需求的简洁的自然语言描述
  - tasks.md 当前未完成的需求的具体实现规划以及实现状态
  - checklist.md
 - scripts/ 脚本工具等
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

## 依据来源文档(/docus/)简要叙述

- **Level 1: 宏观架构 (Global Scope)**
    - `Structure.md` (项目架构) 与 `constitution.md` (通用准则) 控制全局。
- **Level 2: 模块协作 (Module & Layer Scope)**
    - `/SpecMd/workflows/` (流程) 与 `/SpecMd/layers/` (层级) 定义具体实现逻辑。
- **Level 3: 微观实现 (File Scope)**
    - **文件自描述**: 源代码文件的头部注释即为该文件的微观需求文档。

## 规范驱动文档(/specs/)简要叙述

