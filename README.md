# Document-Driven Development (DDD)

> Documentation is the Single Source of Truth.

## 背景

随着 AI Coding 的快速发展，开发效率得到了前所未有的提升。

目前主流的 AI 开发模式主要有两类：

### Vibe Coding

Vibe Coding 强调快速探索与快速迭代。

开发者提出想法，AI 负责实现。

这种模式非常适合：

* 科研探索
* 算法验证
* 原型开发
* 快速试错

但随着项目规模增长，往往会出现：

* 架构逐渐失控
* 功能难以追踪
* 设计决策丢失
* 文档缺失
* 代码与认知脱节

[参考来源](https://www.runoob.com/ai-agent/vibe-coding-start.html)

---

### Specification-Driven Development（SDD）

SDD 强调规范优先。

通过：

```text
Spec
→ Plan
→ Task
→ Implementation
```

驱动开发过程。

其优势在于：

* 需求追踪
* 设计决策记录
* 实现规划
* 结构化开发流程

同时，由于 AI 更擅长按照明确规则执行，因此 SDD 能够为 AI 提供清晰的实现路径。

然而 SDD 默认假设：

```text
需求相对明确
目标相对稳定
```

对于科研开发、算法研究和持续演化的项目而言，需求本身往往处于不断变化之中。

此时：

```text
Spec
Plan
Task
```

会频繁失效并需要重构。

[参考来源](https://github.com/github/spec-kit)

---

## DDD 的目标

DDD 试图结合两者的优势：

* 保留 Vibe Coding 的探索能力
* 保留 SDD 的结构化流程
* 建立长期可维护的知识体系
* 实现 AI 与文档协同开发

DDD 的核心观点是：

> 文档不是代码的说明书，而是系统本身。

代码只是文档的一种实现形式。

去除了检查需求一致性的部分 -- 比如说checkout-or等智能体就没有

---

# 核心原则

## 文档是唯一事实来源

系统行为由文档定义。

代码必须符合文档。

测试必须验证文档。

任何变更都必须首先修改文档。

开发流程：

```text
修改文档
↓
生成代码
↓
运行测试
↓
验证一致性
```

---

## AI 面向文档编程

开发者主要维护文档。

AI 负责：

* 代码生成
* 重构
* 测试生成
* 一致性检查

开发者关注：

```text
系统应该是什么
```

AI 关注：

```text
系统如何实现
```

---

# 双文档体系

DDD 将文档分为两个独立层次。

## Docus（Documentation Layer）

Docus 是系统的依据来源文档（Source Documentation）。

用于定义：

```text
系统是什么
```

它是项目的长期知识库，也是整个系统的唯一文档来源。

当 `docus/constitution.md` 发生变更时，必须同步传播到 `.docusdd/templates/`、`.github/agents/`、`README.md`、`quickstart.md`，避免规则与执行模板脱节。


Docus 包含三个层级,其中前两个层级统一在./docus中


### 项目层

描述项目整体目标与系统架构。

包括：

* 项目目标
* 功能边界
* 总体设计
* 核心概念

---

### 模块层

描述模块职责与接口设计。

包括：

* 模块功能
* 输入输出
* 依赖关系
* 设计约束

---

### 文件层

位于每个源代码文件开头。

用于描述：

* 文件职责
* 核心接口
* 数据结构
* 实现约束

开发者无需阅读具体实现即可理解文件作用。

---

## Specs（Execution Layer）

Specs 是规范驱动文档。

用于定义：

```text
当前准备做什么
```

它不负责长期知识存储。

而负责：

* 功能规划
* 实现方案
* 任务拆解
* 开发检查

典型文件：

```text
spec.md
plan.md
check.md
```

Specs 可以被频繁创建、修改或删除。

而 Docus 应始终保持稳定并持续演化。

---

# 目录结构

```text
project/

├── docus/
│
├── specs/
│   └── reports/
│
├── src/
│
└── tests/
```

---

# 开发流程

```
DDD 的标准开发流程：

研究问题
↓
修改 Docus
↓
生成 Specs
↓
AI 实现代码
↓
生成测试
↓
验证文档-代码一致性
↓
更新 Docus

```

---

# 适用场景

DDD 特别适用于：

### 科研项目

* 光谱分析
* 深度学习
* 机器学习
* 生物信息学
* 计算化学

---

### 长周期项目

* 持续迭代
* 频繁重构
* 多阶段演进

---

### AI 原生开发

* Agent Coding
* 自动代码生成
* AI 协同开发
* AI 驱动软件工程

---

# 开发理念

DDD 认为：

```text
设计存在于 Docus

计划存在于 Specs

实现存在于 Code

验证存在于 Tests
```

最终目标是：

```text
开发者维护知识

AI维护实现
```

让人类专注于领域知识与系统设计，而让 AI 专注于代码实现与验证。
