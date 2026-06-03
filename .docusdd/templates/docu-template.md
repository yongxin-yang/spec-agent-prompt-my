<!-- 宪章摘录（默认，来源：.docusdd/templates/docu-constitution-template.md） -->
<!-- 核心：文档即代码；可执行规范；单一事实来源；AI 与人类共同治理 -->
<!-- 强制：每个 layers/workflows 文档必须在开头写明“引用的宪章条款”与“本文件如何满足条款”。 -->

所有 `docus/` 下的子目录文档必须遵循以下特定模板：

# 1. 层级README.md文件模板 (`layers/*/README.md`)
```markdown

# 1. 目的与范围 (Purpose & Scope)
- 说明该层解决什么问题，包含哪些模块。
<!--例如：
- 目的：Tools 层作为“业务步骤包装器（wrapper）”，承接 ProcessCenter 的调度，调用注入的 Utils 对象完成具体步骤，并将结果写回 DataBuffer。
- 范围：`src/tools/` 下所有步骤脚本（每个文件对应一个步骤）。
-->

# 2. 数据流转以及调用 (Data Flow & integration)
- **输入**: 格式、来源。
- **输出**: 格式、去向。
- **内部状态**: 关键变量或类属性。
- **依赖上下游**：依赖哪些上游层？被哪些下游层调用？
- **宪章对齐**：引用哪些宪章条款，以及本文件如何满足这些条款？
<!--例如：
- 输入：
  - `data_buffer`：读取上一步结果与写回当前步骤产物。
  - `path_name_config`：统一路径/目录名映射。
  - 注入对象：由 ProcessCenter 注入的 utils 实例（按步骤不同而不同）。
  - 步骤配置：来自 `function_config.json` 的该步骤配置段。
  - 脚本覆盖参数：来自 `step_overrides` 的单次运行参数（优先级高于 JSON）。
- 输出：
  - 返回值：通常为 `dict`（统计信息/路径/指标）或 `bool`（成功/失败）。
  - 关键副作用：必须把必要结构写回 `data_buffer`（供后续步骤使用）。
- 不变量：
  - `data_indices` / `sample_indices` 仅允许在 Step 1 生成，后续步骤严禁重建或破坏映射关系。
- 上游：只由 ProcessCenter 调用。
- 下游：调用 Utils 对象完成核心逻辑；不直接调用其他 Tools。
- 步骤映射：步骤号与函数、配置键的绑定以 `src/ProcessCenter.py` 为唯一权威。
-->

# 3. 文件职责作用索引（摘要）
<!--例如：
| 步骤 | Tools 文件 | 目标 | 主要注入依赖 |
| :--- | :--- | :--- | :--- |
| 1 | `data_reader_1.py` | 读取原始光谱并生成 ID | `SpectrumProcessor` |
| 2 | `outlier_detector_2.py` | 异常检测与清洗（先执行可配置前处理序列，默认兼容 300~1500 截取 + 面积归一化；再按 `outlier_model_type=pls|cnn` 执行模型路径；最后统一双算法判定）；支持 `algorithm_type: "chi_square" \| "mean_absolute_error"`；`cnn` 路径默认超参为 `epochs=300,batch_size=96,learning_rate=0.005,loss_function=huber_tf,DenseN=112,DropoutR=0.06,C1_K=8,C1_S=8,C2_K=16,C2_S=20`；结果输出需含 Step2 前处理快照与模型快照（供 Step4 摘要追溯）；前处理能力必须复用 `PreProcessor` 既有接口，不新增 utils 接口 | `AbnormalDataDetector`, `PLSProcessor`, `PreProcessor`, `NeuralNetwork` |
| 3 | `data_preprocessor_3.py` | 预处理光谱（DA/EMSC/1st derivative 三元组合，共8种） | `PreProcessor` |
| 4 | `dataset_splitter_4.py` | 样本级分割与打乱 | `SampleManager` |
| 5 | `data_visualizer_5.py` | 可视化展示 | `EnhancedPlotManager`, `SampleManager` |
| 6 | `data_loader_6.py` | 从磁盘恢复 split 数据 | `DataLoadSave`（或 DataModels/Utils 读写实现） |
| 7 | `pls_trainer_7.py` | PLS 训练 | `PLSProcessor` |
| 8 | `pls_predictor_8.py` | PLS 预测与评估 | `PLSProcessor`, `LossManager`, `EnhancedPlotManager` |
| 9 | `bayesian_optimizer_9.py` | 贝叶斯优化超参 | `NeuralNetwork` |
| 10 | `neural_network_trainer_10.py` | 1D-CNN 训练 | `NeuralNetwork` |
| 11 | `neural_network_predictor_11.py` | 1D-CNN 预测与评估 | `NeuralNetwork` |
-->
```

# 2. 层级规定文档模板(`layers/*.md`)以及其他特殊规定
```markdown
# 1. 目的与范围
- 说明该规范解决什么问题，对哪些文件哪些功能做限制。
<!--例如：
1. 目的：
- 将项目数据处理流程中用到的核心算法公式固化，作为代码实现的唯一数学来源。
- 固定算法所使用的库和方法等，明确代码和算法实现的计算机算法来源。
2. 范围：
2.1 符号约定 作用全局
2.2 预处理 作用于该层代码文件夹下的./preprocessor.py
2.6-2.7 神经网络部分 ./PLSprocessor.py
......
-->

# 2. 规范定义(definiton)
- 主要用于规范指定区域的代码的实现，包括对数学来源，引用库，接口格式或数据传输结构等进行规范。

注意：如果有用.py等格式来进行规定的比如说规范数据库格式，需要在md中进行引用
<!--例如：
对后端的数据结构进行规范，规范文件参考：
[datamodel](./datamodel.py)
-->
# 其他章节
......
```

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
