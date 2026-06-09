### 4. 代码风格与规范
- **核心原则**: **极简主义**. 只保留核心业务逻辑, 拒绝冗余.
- **错误处理**:
    - **默认策略**: **不写** `try-except` 块. 让程序在错误处直接崩溃以暴露问题.
    - **例外情况**: 仅在用户明确要求时添加, 且必须包含以下堆栈打印代码:
      `print(f"[ERROR] 异常堆栈:\n{traceback.format_exc()}")`
- **注释规范**:
    - **文件头注释 (必须)**: 必须包含文件名, 主要类/函数功能, 初始化/属性说明, 方法摘要, **调用链上下文** (明确谁调用了本文件), 及关键参数.
    - **行内注释**: 仅用于解释极其复杂的算法步骤或业务逻辑. 避免废话注释.
- **版本迭代**:
    - **覆盖式修改**: 修复Bug or 新增功能时, **直接修改**原代码. 禁止保留注释掉的废弃代码或"兼容旧版"的代码.
- **架构一致性**:
    - **精准定位**: 修改前必须先定位负责该功能的具体模块/类.
    - **职责边界**: 严格遵守"单一职责原则", 不破坏类与类之间的功能界限.
    - **结构变更**: 若需重构类结构或拆分文件, **必须先征询用户意见**.
- **I/O与调试**:
    - 直接进行文件读写, 不预先检查路径/文件是否存在 (相信系统环境).
    - 调试用的 `print` 信息必须精简, 直击要点.

# 错误示范：
1. 检查项，兼容项太多：

```
    data_buffer = getattr(process_center, "data_buffer", None)
    other_results:dict = getattr(data_buffer, "other_results", {}) if data_buffer is not None else {}
    if not isinstance(other_results, dict):
        other_results = {}
    outlier_detection:dict = other_results.get("outlier_detection", {}) or {}
    if not isinstance(outlier_detection, dict):
        outlier_detection = {}
    model_snapshot:dict = other_results.get("step02_outlier_model_snapshot", {}) or {}
    if not isinstance(model_snapshot, dict):
        model_snapshot = {}
```

应该改成：

```
try:
    data_buffer：dict = getattr(process_center, "data_buffer")
    other_results:dict = getattr(data_buffer, "other_results")
    outlier_detection:dict = other_results.get("outlier_detection")
    model_snapshot:dict = other_results.get("step02_outlier_model_snapshot")
except Exception as e: 
    print(f"[ERROR] process_center输入结构有误: {e}")
```

即：
检查项用静态类型注释而不用 if 判断语句，
兼容项去掉，兼容的报错情况用try...except语句捕获处理

AI的评价： 把兼容式 getattr/if 判断改成你要求的 try/except + 明确结构假设。

# 功能实现过杂和错位
比如说，一个需要实现主流程步骤重复执行的函数脚本，
加入了results-subdir,cv-folds,max-components等本该由function_config.yaml配置的参数，
导致代码及其冗杂。


# 数据传递不设成统一格式，使得代码参数冗杂且数据结构并不清晰。
比如：
```
common_entry = {
            "run_hash": runtime["run_hash"],
            "step_hash": runtime["step_hash"],
            "step_id": runtime["step_id"],
            "base_method_id": runtime["base_method_id"],
            "artifact_type": "normalized_scale_scatter",
            "step_index": int(runtime["step_index"]),
            "artifact_hash": runtime["artifact_hash"] or None,
            "artifact_label": runtime["artifact_label"] or None,
            "scale_metric": scale_metric,
        }
        self._write_json(
            summary_path,
            {
                **common_entry,
                "run_manifest_name": os.path.basename(runtime["manifest_path"]) if runtime["manifest_path"] else None,
                "run_manifest_dir": os.path.dirname(runtime["manifest_path"]) if runtime["manifest_path"] else None,
                "pipeline_sequence": runtime["pipeline_sequence"],
                "pipeline_sequence_text": pipeline_sequence_text,
                "pipeline_base_method_ids": runtime["pipeline_base_method_ids"],
                "applied_sequence": runtime["applied_sequence"],
                "report_sequence": runtime["applied_sequence"],
                "report_sequence_text": applied_sequence_text,
                "applied_base_method_ids": runtime["applied_base_method_ids"],
                "manifest_path": runtime["manifest_path"] or None,
                "score": None,
                "eps": float(eps),
                "scale_metric_description": self._describe_repetition_scale_metric(scale_metric),
                "input_dataset": runtime["input_dataset"] or None,
                "score_details": None,
                "x_shape": list(runtime["x_arr"].shape),
                "wavelengths_shape": list(runtime["wl_arr"].shape),
                "wavelengths_min": runtime["wl_min"],
                "wavelengths_max": runtime["wl_max"],
                "selected_wavelengths": self.selected_wavelengths,
                "has_sample_indices": True,
                "normalized_scale_summary": normalized_scale_summary,
                "artifact_paths": artifact_paths,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            },
        )

        record = {
            **common_entry,
            "pipeline_sequence_text": pipeline_sequence_text,
            "report_sequence_text": applied_sequence_text,
            "score": None,
            "eps": float(eps),
            "score_details": None,
            "summary_path": summary_path,
            "plot_path": normalized_scale_plot_path,
            "csv_path": normalized_scale_csv_path,
            "between_plot_path": artifact_paths["between_plot_path"],
            "between_csv_path": artifact_paths["between_csv_path"],
            "normalized_scale_plot_path": artifact_paths["normalized_scale_plot_path"],
            "normalized_scale_csv_path": artifact_paths["normalized_scale_csv_path"],
        }
        index_entry = {
            **common_entry,
            "input_dataset": runtime["input_dataset"] or None,
            "pipeline_sequence": list(runtime["pipeline_sequence"]),
            "pipeline_sequence_text": pipeline_sequence_text,
            "report_sequence": list(runtime["applied_sequence"]),
            "report_sequence_text": applied_sequence_text,
            "manifest_path": runtime["manifest_path"] or None,
            "artifact_paths": artifact_paths,
        }
```
这种其实要好一些，因为起码用了复用，只不过没有指定格式，还是json传递。