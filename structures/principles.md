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


## 依据来源文档(/docus/)简要叙述
- **Level 1: 宏观架构 (Global Scope)**
    - `Structure.md` (项目架构) 与 `constitution.md` (通用准则) 控制全局。
- **Level 2: 模块协作 (Module & Layer Scope)**
    - `/SpecMd/workflows/` (流程) 与 `/SpecMd/layers/` (层级) 定义具体实现逻辑。
- **Level 3: 微观实现 (File Scope)**
    - **文件自描述**: 源代码文件的头部注释即为该文件的微观需求文档。

## 规范驱动文档(/Specs/)简要叙述






