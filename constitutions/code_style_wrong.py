#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: PreProcessor.py
Function: 光谱预处理核心类，负责按 canonical method_id 执行 Step 2 / Step 3 共享的预处理流水线。

Class: PreProcessor
- 主要职责:
  1) 维护类内私有方法注册表 `_method_registry`，完成 canonical method_id 到私有实现函数的单向映射。
  2) 提供统一公共入口 `preprocess_pipeline(X, wavelengths, config) -> (X_new, wavelengths_new)`。
-  3) 提供重复性评估公共入口 `evaluate_repetition(X, sample_indices=None, eps, scale_metric="norm") -> float`。
-  4) 提供独立尺度诊断步骤 `normalized_scale_scatter`，用于按样本输出归一化尺度散点报表与图像。
-  5) 提供预处理结果说明查询与落盘接口 `get_preprocessing_info` / `save_processed_data`。
- 初始化属性:
  - `path_name_config`: 由 ProcessCenter 注入的路径配置。
  - `sample_manager`: 由 ProcessCenter 注入的样本管理对象；本类不在内部重新实例化依赖。
  - `_method_registry`: 私有注册表，键为 canonical method_id，值为对应私有函数地址。
  - `selected_wavelengths`: 最近一次波段截取的元信息。
  - `last_repetition_score`: 最近一次 `evaluate_repetition` 的得分。
  - `last_pipeline_sequence`: 最近一次执行的 canonical method_id 顺序。
- 方法摘要:
  - 公共方法: `preprocess_pipeline`、`evaluate_repetition`、`get_preprocessing_info`、`save_processed_data`
  - 私有方法: `_find_wavelength_index`、各 method_id 对应实现函数
- 调用链上下文:
  - `src/tools/outlier_detector_2.py` -> `preprocess_pipeline`
  - `src/tools/data_preprocessor_3.py` -> `preprocess_pipeline`
  - `preprocess_pipeline` -> 解析 method_id 与参数 -> `_method_registry[method_id]`
- 配置来源:
  - `config.preprocessing_sequence`: 只定义执行顺序
  - `config.preprocessing_method_params`: 只定义各 method_id 的参数
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal, sparse
from scipy.sparse.linalg import spsolve


class PreProcessor:
    """光谱预处理器。"""


    def __init__(self, path_name_config, sample_manager):
        self.path_name_config = path_name_config
        self.sample_manager = sample_manager
        self._global_random_seed = int(getattr(sample_manager, "random_seed", 42))
        self.selected_wavelengths: Optional[Dict[str, Any]] = None
        self.last_repetition_score: Optional[float] = None
        self.last_repetition_details: Optional[Dict[str, Any]] = None
        self.last_pipeline_sequence: List[str] = []
        self.repetition_history: List[Dict[str, Any]] = []
        self._current_pipeline_run_id: Optional[str] = None

        datas_root = path_name_config.get("datas", "")
        preprocessed_rel = path_name_config.get("datas_path", {}).get("preprocessed", "preprocessed")
        self.output_dir = os.path.join(datas_root, preprocessed_rel)
        results_root = path_name_config.get("results", "./results")
        step03_rel = path_name_config.get("results_path", {}).get("steps", {}).get("step03", "step03_preprocessing")
        self.repetition_results_dir = os.path.join(results_root, step03_rel)

        self._method_registry: Dict[
            str, Callable[[np.ndarray, np.ndarray, Dict[str, Any]], Tuple[np.ndarray, np.ndarray]]
        ] = {
            "wavelength_select": self._apply_wavelength_select,
            "smooth_gs": self._apply_smooth_gs,
            "background_asls": self._apply_background_asls,
            "background_emsc": self._apply_background_emsc,
            "normalization_area": self._apply_normalization_area,
            "normalization_vector": self._apply_normalization_vector,
            "normalization_norm0_1": self._apply_normalization_norm0_1,
            "normalization_div_const": self._apply_normalization_div_const,
            "normalization_msc": self._apply_normalization_msc,
            "others_data_augmentation": self._apply_data_augmentation,
            "others_none_zeroification": self._apply_none_zeroification,
            "others_first_derivative": self._apply_first_derivative,
            "evaluate_repetition": self._apply_evaluate_repetition,
            "normalized_scale_scatter": self._apply_normalized_scale_scatter,
        }


    def _normalize_repetition_scale_metric(self, scale_metric: Any) -> str:
        metric = str(scale_metric or "norm").strip().lower()
        if metric not in {"norm", "sum"}:
            raise ValueError("evaluate_repetition 的 scale_metric 仅允许 'norm' 或 'sum'")
        return metric

    def _describe_repetition_scale_metric(self, scale_metric: str) -> str:
        if scale_metric == "sum":
            return "sum_of_wavelength_points"
        return "vector_norm"

    def _compute_scale_values(
        self,
        X: np.ndarray,
        *,
        scale_metric: str,
    ) -> np.ndarray:
        x_arr = np.atleast_2d(np.asarray(X, dtype=float))
        metric = self._normalize_repetition_scale_metric(scale_metric)
        if metric == "sum":
            return np.abs(np.sum(x_arr, axis=1)).astype(float)
        return np.abs(np.linalg.norm(x_arr, axis=1)).astype(float)

    def _compute_mean_reference_direction_scale_components(
        self,
        X: np.ndarray,
        eps: float,
        *,
        reference: Optional[np.ndarray] = None,
        scale_metric: str = "norm",
    ) -> Dict[str, Any]:
        x_arr = np.asarray(X, dtype=float)
        n = int(x_arr.shape[0])
        if n == 0:
            raise ValueError("重复性评分要求至少包含 1 条光谱")
        metric = self._normalize_repetition_scale_metric(scale_metric)

        norms = np.linalg.norm(x_arr, axis=1)
        normalized = np.zeros_like(x_arr, dtype=float)
        valid_norm_mask = norms > float(eps)
        if np.any(valid_norm_mask):
            normalized[valid_norm_mask, :] = x_arr[valid_norm_mask, :] / norms[valid_norm_mask].reshape(-1, 1)

        reference_arr = np.asarray(reference, dtype=float).reshape(-1) if reference is not None else np.mean(x_arr, axis=0)
        if reference_arr.shape[0] != x_arr.shape[1]:
            raise ValueError("evaluate_repetition 的 reference 长度必须与 X 的特征维度一致")
        reference_norm = float(np.linalg.norm(reference_arr))
        reference_unit = np.zeros_like(reference_arr, dtype=float)
        if reference_norm > float(eps):
            reference_unit = reference_arr / reference_norm
        direction_similarity = normalized @ reference_unit.reshape(-1, 1)
        direction_similarity = np.clip(direction_similarity.reshape(-1), 0.0, 1.0)

        scales = self._compute_scale_values(
            x_arr,
            scale_metric=metric,
        )
        reference_scale = float(
            self._compute_scale_values(
                reference_arr.reshape(1, -1),
                scale_metric=metric,
            )[0]
        )

        safe_scales = np.where(scales > float(eps), scales, float(eps)).reshape(-1)
        reference_scale_safe = float(reference_scale) if reference_scale > float(eps) else float(eps)
        scale_similarity = np.minimum(safe_scales, reference_scale_safe) / (
            np.maximum(safe_scales, reference_scale_safe) + float(eps)
        )
        scale_similarity = np.clip(scale_similarity, 0.0, 1.0)

        similarity = direction_similarity * scale_similarity
        similarity = np.clip(similarity, 0.0, 1.0)
        return {
            "similarity": similarity,
            "direction_similarity": direction_similarity,
            "scale_similarity": scale_similarity,
            "reference": reference_arr,
            "reference_scale": float(reference_scale_safe),
            "scale_metric": metric,
            "scale_metric_description": self._describe_repetition_scale_metric(metric),
            "count": int(n),
        }

    def _compute_mean_reference_direction_scale_score(
        self,
        X: np.ndarray,
        eps: float,
        *,
        reference: Optional[np.ndarray] = None,
        scale_metric: str = "norm",
    ) -> Tuple[float, int, float]:
        components = self._compute_mean_reference_direction_scale_components(
            X,
            eps,
            reference=reference,
            scale_metric=scale_metric,
        )
        similarity = np.asarray(components["similarity"], dtype=float)
        mean_similarity = float(np.mean(similarity))
        score = 100.0 * float(mean_similarity)
        score = float(np.clip(score, 0.0, 100.0))
        return score, int(components["count"]), float(mean_similarity)

    def _export_repetition_artifacts(
        self,
        sample_scores: pd.DataFrame,
        average_score: float,
        plot_path: str,
        csv_path: str,
        title: str,
        extra_summary: Optional[Dict[str, Any]] = None,
    ) -> None:
        csv_path = str(csv_path).strip()
        plot_path = str(plot_path).strip()
        csv_dir = os.path.dirname(csv_path) or "."
        plot_dir = os.path.dirname(plot_path) or "."
        print(f"csv已输出至: {csv_path}")
        print(f"plot已输出至: {plot_path}")
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(plot_dir, exist_ok=True)

        sample_scores.to_csv(csv_path, index=False, encoding="utf-8-sig")

        x_values = sample_scores["sample_id"].to_numpy(dtype=float)
        y_values = sample_scores["score"].to_numpy(dtype=float)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(x_values, y_values, marker="o", linewidth=1.2, markersize=3)
        ax.axhline(float(average_score), color="red", linestyle="--", linewidth=1.2, label=f"Mean={average_score:.3f}")
        ax.set_title(str(title))
        ax.set_xlabel("Sample ID")
        ax.set_ylabel("Repeatability Score (0-100)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

        plot_txt_dir = os.path.join(plot_dir, "plot_txt")
        os.makedirs(plot_txt_dir, exist_ok=True)
        txt_path = os.path.join(plot_txt_dir, f"{os.path.splitext(os.path.basename(plot_path))[0]}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"File: {os.path.basename(plot_path)}\n")
            f.write(f"Title: {title}\n")
            f.write("XLabel: Sample ID\n")
            f.write("YLabel: Repeatability Score (0-100)\n")
            f.write(f"Sample Count: {int(sample_scores.shape[0])}\n")
            f.write(f"Average Score: {float(average_score):.6f}\n")
            f.write(f"Min Score: {float(np.min(y_values)):.6f}\n") 
            f.write(f"Max Score: {float(np.max(y_values)):.6f}\n")
            if extra_summary:
                for key, value in extra_summary.items():
                    f.write(f"{key}: {value}\n")


    def _find_wavelength_index(self, wavelengths: np.ndarray, target_wl: float) -> int:
        return int(np.abs(wavelengths - target_wl).argmin())

    def _apply_wavelength_select(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        wavelength_range = config.get("wavelength_range", [300, 1500])
        if not isinstance(wavelength_range, (list, tuple)):
            raise ValueError("wavelength_select 的 wavelength_range 必须是 [start, end] 或 [[s1, e1], [s2, e2], ...]")

        if (
            len(wavelength_range) == 2
            and not any(isinstance(item, (list, tuple)) for item in wavelength_range)
        ):
            ranges = [(float(wavelength_range[0]), float(wavelength_range[1]))]
        else:
            ranges = []
            for item in wavelength_range:
                if not isinstance(item, (list, tuple)) or len(item) != 2:
                    raise ValueError("wavelength_select 的 wavelength_range 子项必须为长度为 2 的区间")
                ranges.append((float(item[0]), float(item[1])))

        selected_indices: List[int] = []
        selected_ranges: List[Tuple[float, float, int, int]] = []
        for start_wl, end_wl in ranges:
            start_idx = self._find_wavelength_index(wavelengths, start_wl)
            end_idx = self._find_wavelength_index(wavelengths, end_wl)
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx
            current_indices = list(range(start_idx, end_idx + 1))
            selected_indices.extend(current_indices)
            selected_ranges.append((float(wavelengths[start_idx]), float(wavelengths[end_idx]), start_idx, end_idx))

        unique_indices = np.asarray(sorted(set(selected_indices)), dtype=int)
        if unique_indices.size == 0:
            raise ValueError("wavelength_select 未选中任何波长点")

        x_selected = np.asarray(X[:, unique_indices], dtype=float)
        wavelengths_selected = np.asarray(wavelengths[unique_indices], dtype=float)
        self.selected_wavelengths = {
            "ranges": selected_ranges,
            "indices": unique_indices,
            "wavelengths": wavelengths_selected,
        }
        print(f"应用 wavelength_select: ranges={selected_ranges}, selected_points={unique_indices.size}")
        return x_selected, wavelengths_selected

    def _apply_smooth_gs(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        k = int(config.get("k", 3))
        sigma = float(config.get("sigma", 0.5))
        if k < 1:
            return np.asarray(X, dtype=float).copy(), np.asarray(wavelengths, dtype=float).copy()

        window = signal.windows.gaussian(2 * k + 1, std=max(sigma, 1e-12))
        kernel = window / np.sum(window)
        x_smoothed = np.apply_along_axis(lambda row: np.convolve(row, kernel, mode="same"), axis=1, arr=X)
        print(f"应用 smooth_gs: k={k}, sigma={sigma}")
        return np.asarray(x_smoothed, dtype=float), np.asarray(wavelengths, dtype=float).copy()

    def _baseline_asls(self, spectrum: np.ndarray, lam: float, p: float, niter: int) -> np.ndarray:
        length = spectrum.shape[0]
        diff_matrix = sparse.diags([1, -2, 1], [0, 1, 2], shape=(length - 2, length))  # type: ignore[arg-type]
        diff_matrix = diff_matrix.transpose().dot(diff_matrix)
        weights = np.ones(length)
        baseline = np.zeros(length)
        for _ in range(niter):
            weight_matrix = sparse.diags(weights, 0, shape=(length, length))  # type: ignore[arg-type]
            system = weight_matrix + lam * diff_matrix
            baseline = spsolve(system, weights * spectrum)
            weights = np.where(spectrum > baseline, p, 1 - p)
        return np.asarray(baseline, dtype=float)

    def _apply_background_asls(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        lam = float(config.get("lambda", 1e5))
        p = float(config.get("p", 0.01))
        niter = int(config.get("niter", 10))
        if lam <= 0:
            raise ValueError("background_asls 的 lambda 必须大于 0")
        if not (0.0 < p < 1.0):
            raise ValueError("background_asls 的 p 必须满足 0 < p < 1")
        if niter < 1:
            raise ValueError("background_asls 的 niter 必须大于等于 1")
        x_arr = np.asarray(X, dtype=float)
        corrected = np.zeros_like(x_arr)
        for row_idx in range(x_arr.shape[0]):
            baseline = self._baseline_asls(x_arr[row_idx, :], lam=lam, p=p, niter=niter)
            corrected[row_idx, :] = x_arr[row_idx, :] - baseline
        print(f"应用 background_asls: lambda={lam}, p={p}, niter={niter}")
        return corrected, np.asarray(wavelengths, dtype=float).copy()

    def _apply_background_emsc(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        x_arr = np.asarray(X, dtype=float)
        wavelengths_arr = np.asarray(wavelengths, dtype=float).reshape(-1)
        channels = x_arr.shape[1]

        wl_min = float(np.min(wavelengths_arr))
        wl_max = float(np.max(wavelengths_arr))
        if wl_max == wl_min:
            wl_scaled = np.linspace(-1.0, 1.0, channels)
        else:
            wl_scaled = ((wavelengths_arr - wl_min) / (wl_max - wl_min)) * 2.0 - 1.0

        M = int(config.get("M", 2))
        if M < 0:
            raise ValueError("background_emsc 的 M 必须为非负整数")

        r_ref_raw = config.get("R_ref", None)
        if r_ref_raw is None or str(r_ref_raw).strip().lower() in ("mean", "none", ""):
            reference = np.mean(x_arr, axis=0)
        else:
            reference = np.asarray(r_ref_raw, dtype=float).reshape(-1)
            if reference.shape[0] != channels:
                raise ValueError("background_emsc 的 R_ref 长度必须等于光谱通道数")

        p_m_raw = config.get("P_m", None)
        basis_list: List[np.ndarray] = []
        if p_m_raw is None:
            for power in range(1, M + 1):
                basis_list.append(np.asarray(wl_scaled ** power, dtype=float).reshape(-1))
        elif isinstance(p_m_raw, (list, tuple)):
            if len(p_m_raw) == 0:
                basis_list = []
            elif all(isinstance(v, (int, float, np.integer, np.floating)) for v in p_m_raw):
                for power_raw in p_m_raw:
                    power = int(power_raw)
                    if power < 1:
                        raise ValueError("background_emsc 的 P_m 若为幂次列表，幂次必须 >= 1")
                    basis_list.append(np.asarray(wl_scaled ** power, dtype=float).reshape(-1))
            else:
                for idx, basis in enumerate(p_m_raw):
                    basis_arr = np.asarray(basis, dtype=float).reshape(-1)
                    if basis_arr.shape[0] != channels:
                        raise ValueError(f"background_emsc 的 P_m[{idx}] 长度必须等于光谱通道数")
                    basis_list.append(basis_arr)
        else:
            raise ValueError("background_emsc 的 P_m 必须为列表（幂次列表或基函数数组列表）")

        design_columns: List[np.ndarray] = [np.ones(channels, dtype=float), reference]
        design_columns.extend(basis_list)
        design = np.column_stack(design_columns)
        corrected = np.zeros_like(x_arr)
        for row_idx in range(x_arr.shape[0]):
            coef, _, _, _ = np.linalg.lstsq(design, x_arr[row_idx, :], rcond=None)
            scale = float(coef[1])
            baseline = float(coef[0])
            for m_idx, basis in enumerate(basis_list):
                baseline = baseline + float(coef[2 + m_idx]) * basis
            if abs(scale) < 1e-12:
                scale = 1.0
            corrected[row_idx, :] = (x_arr[row_idx, :] - baseline) / scale

        print("应用 background_emsc")
        return corrected, wavelengths_arr.copy()

    def _apply_normalization_area(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        del config
        x_arr = np.asarray(X, dtype=float)
        wavelengths_arr = np.asarray(wavelengths, dtype=float).reshape(-1)
        if wavelengths_arr.shape[0] != x_arr.shape[1]:
            raise ValueError("normalization_area 要求 wavelengths 长度与 X 的特征维度一致")
        normalized = np.zeros_like(x_arr)
        for row_idx in range(x_arr.shape[0]):
            area = float(np.trapz(x_arr[row_idx, :], x=wavelengths_arr))
            if abs(area) < 1e-12:
                raise ValueError(f"normalization_area 要求样本 {row_idx} 的面积为非零，当前为 {area}")
            else:
                normalized[row_idx, :] = x_arr[row_idx, :] / area
        print("应用 normalization_area")
        return normalized, wavelengths_arr.copy()

    def _apply_normalization_vector(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        del config
        print("X的形状:", X.shape)
        x_arr = np.asarray(X, dtype=float)
        normalized = np.zeros_like(x_arr)
        for row_idx in range(x_arr.shape[0]):
            norm_value = float(np.linalg.norm(x_arr[row_idx, :]))
            if abs(norm_value) < 1e-12:
                raise ValueError(f"normalization_vector 要求样本 {row_idx} 的长度为非零，当前为 {norm_value}")
            else:
                normalized[row_idx, :] = x_arr[row_idx, :] / norm_value
        print("应用 normalization_vector")
        return normalized, np.asarray(wavelengths, dtype=float).copy()

    def _apply_normalization_norm0_1(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        del config
        x_arr = np.asarray(X, dtype=float)
        normalized = np.zeros_like(x_arr)
        for row_idx in range(x_arr.shape[0]):
            min_val = float(np.min(x_arr[row_idx, :]))
            max_val = float(np.max(x_arr[row_idx, :]))
            if max_val == min_val:
                normalized[row_idx, :] = x_arr[row_idx, :]
            else:
                normalized[row_idx, :] = (max_val - x_arr[row_idx, :]) / (max_val - min_val)
        print("应用 normalization_norm0_1")
        return normalized, np.asarray(wavelengths, dtype=float).copy()

    def _apply_normalization_div_const(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        weights_raw = config.get("w", None)
        if weights_raw is None:
            weights = np.ones(int(np.asarray(X).shape[0]), dtype=float)
        else:
            weights = np.asarray(weights_raw, dtype=float)
        if weights.ndim != 1 or weights.shape[0] != X.shape[0]:
            raise ValueError("normalization_div_const 需要一维权重 w，且长度与 X 的样本数一致")
        safe_weights = np.where(np.abs(weights) < 1e-12, 1.0, weights)
        print("应用 normalization_div_const")
        return np.asarray(X, dtype=float) / safe_weights[:, None], np.asarray(wavelengths, dtype=float).copy()

    def _apply_normalization_msc(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        del config
        x_arr = np.asarray(X, dtype=float)
        reference = np.mean(x_arr, axis=0)
        normalized = np.zeros_like(x_arr)
        for row_idx in range(x_arr.shape[0]):
            coef = np.polyfit(reference, x_arr[row_idx, :], 1)
            slope = float(coef[0])
            intercept = float(coef[1])
            if abs(slope) < 1e-12:
                slope = 1.0
            normalized[row_idx, :] = (x_arr[row_idx, :] - intercept) / slope
        print("应用 normalization_msc")
        return normalized, np.asarray(wavelengths, dtype=float).copy()

    def _apply_data_augmentation(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        scale_min = float(config.get("scale_min", 0.98))
        scale_max = float(config.get("scale_max", 1.02))
        noise_level = float(config.get("noise_level", 0.005))
        rng = np.random.default_rng(self._global_random_seed)
        x_arr = np.asarray(X, dtype=float)
        scales = rng.uniform(scale_min, scale_max, size=(x_arr.shape[0], 1))
        noise = rng.normal(0.0, noise_level, size=x_arr.shape)
        augmented = x_arr * scales + noise
        print(
            f"应用 others_data_augmentation: scale_min={scale_min}, scale_max={scale_max}, noise_level={noise_level}"
        )
        return augmented, np.asarray(wavelengths, dtype=float).copy()

    def _apply_none_zeroification(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        del config
        print("应用 others_none_zeroification")
        return np.maximum(0.0, np.asarray(X, dtype=float)), np.asarray(wavelengths, dtype=float).copy()

    def _apply_first_derivative(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        deriv_order_raw = config.get("deriv_order", None)
        if deriv_order_raw is None:
            deriv_order_raw = config.get("order", 1)
        deriv_order = int(deriv_order_raw)
        if deriv_order not in (1, 2):
            raise ValueError("others_first_derivative 仅支持 deriv_order=1 或 deriv_order=2")

        x_arr = np.asarray(X, dtype=float)
        if deriv_order == 1:
            derivative = np.diff(x_arr, n=1, axis=1)
            derivative = np.pad(derivative, ((0, 0), (0, 1)), mode="constant", constant_values=0.0)
        else:
            derivative = np.diff(x_arr, n=2, axis=1)
            derivative = np.pad(derivative, ((0, 0), (0, 2)), mode="constant", constant_values=0.0)

        print(f"应用 others_first_derivative: deriv_order={deriv_order}")
        return derivative, np.asarray(wavelengths, dtype=float).copy()


    def _hash_text(self, text: str, length: int = 16) -> str:
        digest = hashlib.sha1(str(text).encode("utf-8")).hexdigest()
        return digest[: int(length)]

    def _hash_obj(self, obj: Any, length: int = 16) -> str:
        dumped = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str, separators=(",", ":"))
        return self._hash_text(dumped, length=length)

    def _sanitize_name_fragment(self, text: str) -> str:
        forbidden_chars = '<>:"/\\|?*'
        normalized = "".join("_" if ch in forbidden_chars or ch.isspace() else ch for ch in str(text))
        normalized = normalized.strip("_")
        return normalized or "artifact"

    def _sequence_to_text(self, sequence: List[str]) -> str:
        cleaned = [str(item).strip() for item in sequence if str(item).strip()]
        return " -> ".join(cleaned) if cleaned else "no_preprocess"

    def _load_json_if_exists(self, path: str) -> Dict[str, Any]:
        if not path or not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}

    def _export_root(self) -> str:
        return os.path.join(self.repetition_results_dir, "reports", "repetition_evaluation")

    def _export_run_dir(self, run_hash: str) -> str:
        return os.path.join(self._export_root(), str(run_hash))

    def _compose_repetition_artifact_paths(
        self,
        config: Dict[str, Any],
        *,
        step_index: int,
        step_hash: str,
        run_hash: str,
    ) -> Dict[str, str]:
        reports_dir = str(config.get("artifact_reports_dir") or "").strip()
        plots_dir = str(config.get("artifact_plots_dir") or "").strip()
        artifact_stem = str(config.get("artifact_stem") or "").strip()
        artifact_hash = str(config.get("artifact_hash") or "").strip()

        if not reports_dir and str(config.get("csv_path") or "").strip():
            reports_dir = os.path.dirname(str(config.get("csv_path")).strip())
            artifact_stem = artifact_stem or os.path.splitext(os.path.basename(str(config.get("csv_path")).strip()))[0]
        if not plots_dir and str(config.get("plot_path") or "").strip():
            plots_dir = os.path.dirname(str(config.get("plot_path")).strip())
            artifact_stem = artifact_stem or os.path.splitext(os.path.basename(str(config.get("plot_path")).strip()))[0]

        if reports_dir and plots_dir:
            if not artifact_hash and artifact_stem:
                artifact_hash = self._hash_text(artifact_stem, length=16)
            stem_base = f"repeatability_{artifact_hash}" if artifact_hash else (artifact_stem or "repeatability")
            run_fragment = self._sanitize_name_fragment(run_hash) if run_hash else "run"
            step_stem = f"{stem_base}__run_{run_fragment}__step{int(step_index):02d}"
            return {
                "summary_path": os.path.join(reports_dir, f"{step_stem}__summary.json"),
                "within_csv_path": os.path.join(reports_dir, f"{step_stem}__within_samples.csv"),
                "within_plot_path": os.path.join(plots_dir, f"{step_stem}__within_samples.png"),
                "between_csv_path": os.path.join(reports_dir, f"{step_stem}__between_samples.csv"),
                "between_plot_path": os.path.join(plots_dir, f"{step_stem}__between_samples.png"),
                "normalized_scale_csv_path": os.path.join(reports_dir, f"{step_stem}__normalized_scale_scatter.csv"),
                "normalized_scale_plot_path": os.path.join(plots_dir, f"{step_stem}__normalized_scale_scatter.png"),
            }

        run_dir = self._export_run_dir(run_hash)
        os.makedirs(run_dir, exist_ok=True)
        return {
            "summary_path": os.path.join(run_dir, f"{step_hash}__summary.json"),
            "within_csv_path": os.path.join(run_dir, f"{step_hash}__within_samples.csv"),
            "within_plot_path": os.path.join(run_dir, f"{step_hash}__within_samples.png"),
            "between_csv_path": os.path.join(run_dir, f"{step_hash}__between_samples.csv"),
            "between_plot_path": os.path.join(run_dir, f"{step_hash}__between_samples.png"),
            "normalized_scale_csv_path": os.path.join(run_dir, f"{step_hash}__normalized_scale_scatter.csv"),
            "normalized_scale_plot_path": os.path.join(run_dir, f"{step_hash}__normalized_scale_scatter.png"),
        }

    def _to_jsonable(self, value: Any) -> Any:
        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, (np.integer, np.floating)):
            return value.item()
        if isinstance(value, dict):
            return {str(k): self._to_jsonable(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._to_jsonable(v) for v in value]
        return value

    def _write_json(self, path: str, payload: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._to_jsonable(payload), f, ensure_ascii=False, indent=2)

    def _upsert_repeatability_run_index(
        self,
        *,
        manifest_path: str,
        run_hash: str,
        pipeline_sequence: List[str],
        pipeline_base_method_ids: List[str],
        entry: Dict[str, Any],
    ) -> str:
        run_dir = os.path.dirname(str(manifest_path))
        index_path = os.path.join(run_dir, f"{run_hash}__repeatability_index.json")
        index_payload = self._load_json_if_exists(index_path)
        existing_entries = list(index_payload.get("artifacts") or [])
        kept_entries = []
        for item in existing_entries:
            if not isinstance(item, dict):
                continue
            if str(item.get("step_hash") or "") == str(entry.get("step_hash") or ""):
                continue
            kept_entries.append(item)
        kept_entries.append(dict(entry))
        kept_entries = sorted(kept_entries, key=lambda item: (int(item.get("step_index") or 0), str(item.get("step_id") or "")))

        payload = {
            "run_hash": run_hash,
            "manifest_path": manifest_path,
            "manifest_name": os.path.basename(manifest_path),
            "run_dir": run_dir,
            "pipeline_sequence": list(pipeline_sequence),
            "pipeline_sequence_text": self._sequence_to_text(list(pipeline_sequence)),
            "pipeline_base_method_ids": list(pipeline_base_method_ids),
            "artifact_count": int(len(kept_entries)),
            "artifacts": kept_entries,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        self._write_json(index_path, payload)

        manifest_payload = self._load_json_if_exists(manifest_path)
        manifest_payload.update(
            {
                "run_hash": run_hash,
                "manifest_name": os.path.basename(manifest_path),
                "pipeline_sequence": list(pipeline_sequence),
                "pipeline_sequence_text": self._sequence_to_text(list(pipeline_sequence)),
                "pipeline_base_method_ids": list(pipeline_base_method_ids),
                "repeatability_index_path": index_path,
                "repeatability_artifact_count": int(len(kept_entries)),
                "repeatability_artifacts": kept_entries,
            }
        )
        self._write_json(manifest_path, manifest_payload)
        return index_path

    def _new_run_hash(self, sequence: List[str]) -> str:
        seed = {
            "time": datetime.now().isoformat(timespec="microseconds"),
            "seq": list(sequence),
            "rand": int(np.random.default_rng().integers(0, 1_000_000_000)),
        }
        return self._hash_obj(seed, length=16)

    def _build_normalized_scale_records(
        self,
        X: np.ndarray,
        sample_ids: np.ndarray,
        *,
        scale_metric: str,
        eps: float,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        x_arr = np.asarray(X, dtype=float)
        sample_arr = np.asarray(sample_ids).reshape(-1)
        if x_arr.ndim != 2 or x_arr.shape[0] != sample_arr.shape[0]:
            raise ValueError("normalized scale records 要求 X 与 sample_ids 一一对应")

        records: List[Dict[str, Any]] = []
        all_anchor_policies: List[str] = []
        unique_sample_ids = np.unique(sample_arr)
        for sample_id in unique_sample_ids:
            group_indices = np.where(sample_arr == sample_id)[0]
            subset = x_arr[group_indices, :]
            raw_scale_values = self._compute_scale_values(subset, scale_metric=scale_metric).reshape(-1)
            valid_mask = raw_scale_values > float(eps)
            if np.any(valid_mask):
                anchor_scale_value = float(np.min(raw_scale_values[valid_mask]))
                normalized_values = raw_scale_values / anchor_scale_value
                anchor_policy = "min_positive_scale"
            else:
                anchor_scale_value = 0.0
                normalized_values = np.ones_like(raw_scale_values, dtype=float)
                anchor_policy = "all_zero_or_near_zero_group"
            all_anchor_policies.append(anchor_policy)

            for local_idx, global_idx in enumerate(group_indices):
                records.append(
                    {
                        "sample_id": int(sample_id),
                        "spectrum_index": int(local_idx + 1),
                        "global_row_index": int(global_idx),
                        "raw_scale_value": float(raw_scale_values[local_idx]),
                        "normalized_scale_value": float(normalized_values[local_idx]),
                        "anchor_scale_value": float(anchor_scale_value),
                        "anchor_policy": anchor_policy,
                        "scale_metric": str(scale_metric),
                    }
                )

        df = pd.DataFrame(records).sort_values(by=["sample_id", "spectrum_index"]).reset_index(drop=True)
        normalized_values_arr = df["normalized_scale_value"].to_numpy(dtype=float) if len(df) > 0 else np.asarray([], dtype=float)
        summary = {
            "sample_count": int(len(unique_sample_ids)),
            "record_count": int(len(df)),
            "anchor_policies": sorted(set(all_anchor_policies)),
            "min_normalized_scale_value": float(np.min(normalized_values_arr)) if normalized_values_arr.size > 0 else None,
            "max_normalized_scale_value": float(np.max(normalized_values_arr)) if normalized_values_arr.size > 0 else None,
            "mean_normalized_scale_value": float(np.mean(normalized_values_arr)) if normalized_values_arr.size > 0 else None,
            "unit": "unitless",
        }
        return df, summary

    def _export_normalized_scale_scatter_artifacts(
        self,
        scale_records: pd.DataFrame,
        *,
        plot_path: str,
        csv_path: str,
        title: str,
        scale_metric: str,
        summary: Optional[Dict[str, Any]] = None,
    ) -> None:
        csv_dir = os.path.dirname(csv_path) or "."
        plot_dir = os.path.dirname(plot_path) or "."
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(plot_dir, exist_ok=True)
        scale_records.to_csv(csv_path, index=False, encoding="utf-8-sig")

        fig, ax = plt.subplots(figsize=(10, 4))
        x_values = scale_records["sample_id"].to_numpy(dtype=float)
        y_values = scale_records["normalized_scale_value"].to_numpy(dtype=float)
        ax.scatter(x_values, y_values, s=22, alpha=0.9, edgecolors="face")
        ax.axhline(1.0, color="red", linestyle="--", linewidth=1.1, label="Normalized baseline = 1")
        ax.set_title(str(title))
        ax.set_xlabel("Sample ID")
        ax.set_ylabel("Normalized Scale (unitless)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

        plot_txt_dir = os.path.join(plot_dir, "plot_txt")
        os.makedirs(plot_txt_dir, exist_ok=True)
        txt_path = os.path.join(plot_txt_dir, f"{os.path.splitext(os.path.basename(plot_path))[0]}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"File: {os.path.basename(plot_path)}\n")
            f.write(f"Title: {title}\n")
            f.write("XLabel: Sample ID\n")
            f.write("YLabel: Normalized Scale (unitless)\n")
            f.write(f"ScaleMetric: {scale_metric}\n")
            f.write(f"Record Count: {int(scale_records.shape[0])}\n")
            f.write(f"Sample Count: {int(scale_records['sample_id'].nunique())}\n")
            f.write(
                "Normalization Rule: normalize each spectrum scale by the minimum effective scale "
                "within the same sample group\n"
            )
            if summary:
                for key, value in summary.items():
                    f.write(f"{key}: {value}\n")


    def _resolve_step03_artifact_context(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
        *,
        default_step_id: str,
    ) -> Dict[str, Any]:
        x_arr = np.asarray(X)
        wl_arr = np.asarray(wavelengths, dtype=float).reshape(-1)
        step_id = str(config.get("__step_id") or default_step_id)
        step_index = int(config.get("__step_index") or 0)
        base_method_id = str(config.get("__base_method_id") or default_step_id)
        run_hash = str(config.get("__run_hash") or (self._current_pipeline_run_id or "run"))
        manifest_path = str(config.get("__manifest_path") or "")
        step_hash = self._hash_obj({"run": run_hash, "step_id": step_id, "step_index": step_index}, length=16)
        artifact_paths = self._compose_repetition_artifact_paths(
            config,
            step_index=int(step_index),
            step_hash=step_hash,
            run_hash=run_hash,
        )
        return {
            "x_arr": x_arr,
            "wl_arr": wl_arr,
            "wl_min": float(np.min(wl_arr)) if wl_arr.size else None,
            "wl_max": float(np.max(wl_arr)) if wl_arr.size else None,
            "step_id": step_id,
            "step_index": step_index,
            "base_method_id": base_method_id,
            "run_hash": run_hash,
            "artifact_hash": str(config.get("artifact_hash") or "").strip(),
            "artifact_label": str(config.get("artifact_label") or "").strip(),
            "input_dataset": str(config.get("input_dataset") or "").strip(),
            "pipeline_sequence": list(config.get("__pipeline_sequence") or []),
            "pipeline_base_method_ids": list(config.get("__pipeline_base_method_ids") or []),
            "applied_sequence": list(config.get("__applied_sequence") or []),
            "applied_base_method_ids": list(config.get("__applied_base_method_ids") or []),
            "manifest_path": manifest_path,
            "step_hash": step_hash,
            "artifact_paths": artifact_paths,
        }


    def _apply_evaluate_repetition(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        eps = float(config.get("eps", 1e-12))
        scale_metric = self._normalize_repetition_scale_metric(config.get("scale_metric", "norm"))
        sample_indices = config.get("sample_indices")
        score = self.evaluate_repetition(
            X,
            sample_indices=sample_indices,
            eps=eps,
            scale_metric=scale_metric,
        )
        details = dict(self.last_repetition_details or {})
        print(f"应用 evaluate_repetition: score={score:.6f}, scale_metric={scale_metric}")
        if "between_sample_mean_score" in details:
            print(
                "  "
                f"between_sample_mean_score={float(details['between_sample_mean_score']):.6f}, "
                f"between_sample_difference_proxy={float(details.get('between_sample_difference_proxy', 0.0)):.6f}"
            )

        runtime = self._resolve_step03_artifact_context(
            X,
            wavelengths,
            config,
            default_step_id="evaluate_repetition",
        )
        x_arr = runtime["x_arr"]
        wl_arr = runtime["wl_arr"]
        summary_path = runtime["artifact_paths"]["summary_path"]
        within_csv_path = runtime["artifact_paths"]["within_csv_path"]
        within_plot_path = runtime["artifact_paths"]["within_plot_path"]
        between_csv_path = runtime["artifact_paths"]["between_csv_path"]
        between_plot_path = runtime["artifact_paths"]["between_plot_path"]
        pipeline_sequence_text = self._sequence_to_text(runtime["pipeline_sequence"])
        applied_sequence_text = self._sequence_to_text(runtime["applied_sequence"])

        self._write_json(
            summary_path,
            {
                "run_hash": runtime["run_hash"],
                "run_manifest_name": os.path.basename(runtime["manifest_path"]) if runtime["manifest_path"] else None,
                "run_manifest_dir": os.path.dirname(runtime["manifest_path"]) if runtime["manifest_path"] else None,
                "step_hash": runtime["step_hash"],
                "step_id": runtime["step_id"],
                "base_method_id": runtime["base_method_id"],
                "artifact_type": "evaluate_repetition",
                "step_index": int(runtime["step_index"]),
                "pipeline_sequence": runtime["pipeline_sequence"],
                "pipeline_sequence_text": pipeline_sequence_text,
                "pipeline_base_method_ids": runtime["pipeline_base_method_ids"],
                "applied_sequence": runtime["applied_sequence"],
                "report_sequence": runtime["applied_sequence"],
                "report_sequence_text": applied_sequence_text,
                "applied_base_method_ids": runtime["applied_base_method_ids"],
                "manifest_path": runtime["manifest_path"] or None,
                "score": float(score),
                "eps": float(eps),
                "scale_metric": scale_metric,
                "scale_metric_description": self._describe_repetition_scale_metric(scale_metric),
                "scoring_mode": "mean_reference_direction_scale",
                "complexity": "O(N)",
                "artifact_hash": runtime["artifact_hash"] or None,
                "artifact_label": runtime["artifact_label"] or None,
                "input_dataset": runtime["input_dataset"] or None,
                "score_details": details or None,
                "x_shape": list(x_arr.shape),
                "wavelengths_shape": list(wl_arr.shape),
                "wavelengths_min": runtime["wl_min"],
                "wavelengths_max": runtime["wl_max"],
                "selected_wavelengths": self.selected_wavelengths,
                "has_sample_indices": bool(sample_indices is not None),
                "artifact_paths": {
                    "summary_path": summary_path,
                    "within_csv_path": within_csv_path,
                    "within_plot_path": within_plot_path,
                    "between_csv_path": between_csv_path if sample_indices is not None else None,
                    "between_plot_path": between_plot_path if sample_indices is not None else None,
                    "normalized_scale_csv_path": None,
                    "normalized_scale_plot_path": None,
                },
                "created_at": datetime.now().isoformat(timespec="seconds"),
            },
        )

        title = str(config.get("title") or "Repeatability Score")
        within_title = str(config.get("within_title") or f"{title} - Within Samples")
        between_title = str(config.get("between_title") or f"{title} - Between Samples")

        record = {
            "run_hash": runtime["run_hash"],
            "step_hash": runtime["step_hash"],
            "step_id": runtime["step_id"],
            "base_method_id": runtime["base_method_id"],
            "artifact_type": "evaluate_repetition",
            "step_index": runtime["step_index"],
            "artifact_hash": runtime["artifact_hash"] or None,
            "artifact_label": runtime["artifact_label"] or None,
            "pipeline_sequence_text": pipeline_sequence_text,
            "report_sequence_text": applied_sequence_text,
            "score": float(score),
            "eps": float(eps),
            "scale_metric": scale_metric,
            "score_details": details or None,
            "summary_path": summary_path,
            "plot_path": within_plot_path,
            "csv_path": within_csv_path,
            "between_plot_path": between_plot_path if sample_indices is not None else None,
            "between_csv_path": between_csv_path if sample_indices is not None else None,
            "normalized_scale_plot_path": None,
            "normalized_scale_csv_path": None,
        }
        self.repetition_history.append(record)
        index_entry = {
            "run_hash": runtime["run_hash"],
            "step_hash": runtime["step_hash"],
            "step_index": int(runtime["step_index"]),
            "step_id": runtime["step_id"],
            "base_method_id": runtime["base_method_id"],
            "artifact_type": "evaluate_repetition",
            "artifact_hash": runtime["artifact_hash"] or None,
            "artifact_label": runtime["artifact_label"] or None,
            "input_dataset": runtime["input_dataset"] or None,
            "scale_metric": scale_metric,
            "pipeline_sequence": list(runtime["pipeline_sequence"]),
            "pipeline_sequence_text": pipeline_sequence_text,
            "report_sequence": list(runtime["applied_sequence"]),
            "report_sequence_text": applied_sequence_text,
            "manifest_path": runtime["manifest_path"] or None,
            "artifact_paths": {
                "summary_path": summary_path,
                "within_csv_path": within_csv_path,
                "within_plot_path": within_plot_path,
                "between_csv_path": between_csv_path if sample_indices is not None else None,
                "between_plot_path": between_plot_path if sample_indices is not None else None,
                "normalized_scale_csv_path": None,
                "normalized_scale_plot_path": None,
            },
        }
        repeatability_index_path = self._upsert_repeatability_run_index(
            manifest_path=runtime["manifest_path"],
            run_hash=runtime["run_hash"],
            pipeline_sequence=runtime["pipeline_sequence"],
            pipeline_base_method_ids=runtime["pipeline_base_method_ids"],
            entry=index_entry,
        )
        summary_payload = self._load_json_if_exists(summary_path)
        summary_payload["repeatability_index_path"] = repeatability_index_path
        summary_payload["report_lookup_hint"] = (
            f"run_hash={runtime['run_hash']}; step={int(runtime['step_index']):02d}; "
            f"report_sequence={applied_sequence_text}"
        )
        self._write_json(summary_path, summary_payload)

        if sample_indices is not None:
            sample_ids = np.asarray(sample_indices).reshape(-1)
            x_arr = np.asarray(X, dtype=float)
            if sample_ids.shape[0] == x_arr.shape[0]:
                records: List[Dict[str, Any]] = []
                unique_sample_ids = np.unique(sample_ids)
                sample_sizes: List[int] = []
                sample_mean_spectra: List[np.ndarray] = []
                for sample_id in unique_sample_ids:
                    group_indices = np.where(sample_ids == sample_id)[0]
                    subset = x_arr[group_indices, :]
                    group_score, comparison_count, mean_similarity = self._compute_repetition_score(
                        subset,
                        eps=eps,
                        scale_metric=scale_metric,
                    )
                    records.append(
                        {
                            "sample_id": int(sample_id),
                            "data_point_count": int(group_indices.size),
                            "comparison_count": int(comparison_count),
                            "reference_mode": "sample_mean_spectrum",
                            "scale_metric": scale_metric,
                            "mean_to_reference_similarity": float(mean_similarity),
                            "score": float(group_score),
                        }
                    )
                    sample_sizes.append(int(group_indices.size))
                    sample_mean_spectra.append(np.mean(subset, axis=0))
                sample_scores = pd.DataFrame(records).sort_values(by="sample_id").reset_index(drop=True)
                if len(sample_scores) > 0:
                    self._export_repetition_artifacts(
                        sample_scores=sample_scores,
                        average_score=float(score),
                        plot_path=within_plot_path,
                        csv_path=within_csv_path,
                        title=within_title,
                        extra_summary={
                            "ScoringMode": "mean_reference_direction_scale",
                            "Complexity": "O(N)",
                            "ScaleMetric": scale_metric,
                            "WithinSampleAverageScore": f"{float(details.get('within_sample_average_score', score)):.6f}",
                            "BetweenSampleMeanScore": f"{float(details.get('between_sample_mean_score', 100.0)):.6f}",
                            "BetweenSampleDifferenceProxy": f"{float(details.get('between_sample_difference_proxy', 0.0)):.6f}",
                        },
                    )
                if sample_mean_spectra:
                    sample_mean_matrix = np.asarray(sample_mean_spectra, dtype=float)
                    between_components = self._compute_mean_reference_direction_scale_components(
                        sample_mean_matrix,
                        eps=eps,
                        scale_metric=scale_metric,
                    )
                    between_similarity = np.asarray(between_components["similarity"], dtype=float)
                    between_records: List[Dict[str, Any]] = []
                    for idx, sample_id in enumerate(unique_sample_ids):
                        between_records.append(
                            {
                                "sample_id": int(sample_id),
                                "data_point_count": int(sample_sizes[idx]),
                                "comparison_count": int(sample_mean_matrix.shape[0]),
                                "reference_mode": "global_sample_mean_spectrum",
                                "scale_metric": scale_metric,
                                "mean_to_reference_similarity": float(between_similarity[idx]),
                                "score": float(np.clip(100.0 * between_similarity[idx], 0.0, 100.0)),
                            }
                        )
                    between_scores = pd.DataFrame(between_records).sort_values(by="sample_id").reset_index(drop=True)
                    self._export_repetition_artifacts(
                        sample_scores=between_scores,
                        average_score=float(details.get("between_sample_mean_score", 100.0)),
                        plot_path=between_plot_path,
                        csv_path=between_csv_path,
                        title=between_title,
                        extra_summary={
                            "ScoringMode": "mean_reference_direction_scale",
                            "Complexity": "O(N)",
                            "ScaleMetric": scale_metric,
                            "BetweenSampleMeanScore": f"{float(details.get('between_sample_mean_score', 100.0)):.6f}",
                            "BetweenSampleDifferenceProxy": f"{float(details.get('between_sample_difference_proxy', 0.0)):.6f}",
                            "SampleCount": int(sample_mean_matrix.shape[0]),
                        },
                    )
        return np.asarray(X, dtype=float).copy(), np.asarray(wavelengths, dtype=float).copy()

    def _apply_normalized_scale_scatter(
        self,
        X: np.ndarray,
        wavelengths: np.ndarray,
        config: Dict[str, Any],
    ) -> Tuple[np.ndarray, np.ndarray]:
        eps = float(config.get("eps", 1e-12))
        if eps <= 0:
            raise ValueError("normalized_scale_scatter 的 eps 必须大于 0")
        scale_metric = self._normalize_repetition_scale_metric(config.get("scale_metric", "norm"))
        sample_indices = config.get("sample_indices")
        if sample_indices is None:
            raise ValueError("normalized_scale_scatter 要求提供 sample_indices")

        sample_ids = np.asarray(sample_indices).reshape(-1)
        x_arr = np.asarray(X, dtype=float)
        if sample_ids.shape[0] != x_arr.shape[0]:
            raise ValueError("normalized_scale_scatter 要求 X 与 sample_indices 一一对应")

        runtime = self._resolve_step03_artifact_context(
            X,
            wavelengths,
            config,
            default_step_id="normalized_scale_scatter",
        )
        summary_path = runtime["artifact_paths"]["summary_path"]
        normalized_scale_csv_path = runtime["artifact_paths"]["normalized_scale_csv_path"]
        normalized_scale_plot_path = runtime["artifact_paths"]["normalized_scale_plot_path"]
        pipeline_sequence_text = self._sequence_to_text(runtime["pipeline_sequence"])
        applied_sequence_text = self._sequence_to_text(runtime["applied_sequence"])
        title = str(config.get("title") or "Normalized Scale Scatter")

        print(f"应用 normalized_scale_scatter: scale_metric={scale_metric}")
        scale_records, normalized_scale_summary = self._build_normalized_scale_records(
            x_arr,
            sample_ids,
            scale_metric=scale_metric,
            eps=eps,
        )
        self._export_normalized_scale_scatter_artifacts(
            scale_records,
            plot_path=normalized_scale_plot_path,
            csv_path=normalized_scale_csv_path,
            title=title,
            scale_metric=scale_metric,
            summary=normalized_scale_summary,
        )

        self._write_json(
            summary_path,
            {
                "run_hash": runtime["run_hash"],
                "run_manifest_name": os.path.basename(runtime["manifest_path"]) if runtime["manifest_path"] else None,
                "run_manifest_dir": os.path.dirname(runtime["manifest_path"]) if runtime["manifest_path"] else None,
                "step_hash": runtime["step_hash"],
                "step_id": runtime["step_id"],
                "base_method_id": runtime["base_method_id"],
                "artifact_type": "normalized_scale_scatter",
                "step_index": int(runtime["step_index"]),
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
                "scale_metric": scale_metric,
                "scale_metric_description": self._describe_repetition_scale_metric(scale_metric),
                "artifact_hash": runtime["artifact_hash"] or None,
                "artifact_label": runtime["artifact_label"] or None,
                "input_dataset": runtime["input_dataset"] or None,
                "score_details": None,
                "x_shape": list(runtime["x_arr"].shape),
                "wavelengths_shape": list(runtime["wl_arr"].shape),
                "wavelengths_min": runtime["wl_min"],
                "wavelengths_max": runtime["wl_max"],
                "selected_wavelengths": self.selected_wavelengths,
                "has_sample_indices": True,
                "normalized_scale_summary": normalized_scale_summary,
                "artifact_paths": {
                    "summary_path": summary_path,
                    "within_csv_path": None,
                    "within_plot_path": None,
                    "between_csv_path": None,
                    "between_plot_path": None,
                    "normalized_scale_csv_path": normalized_scale_csv_path,
                    "normalized_scale_plot_path": normalized_scale_plot_path,
                },
                "created_at": datetime.now().isoformat(timespec="seconds"),
            },
        )

        record = {
            "run_hash": runtime["run_hash"],
            "step_hash": runtime["step_hash"],
            "step_id": runtime["step_id"],
            "base_method_id": runtime["base_method_id"],
            "artifact_type": "normalized_scale_scatter",
            "step_index": runtime["step_index"],
            "artifact_hash": runtime["artifact_hash"] or None,
            "artifact_label": runtime["artifact_label"] or None,
            "pipeline_sequence_text": pipeline_sequence_text,
            "report_sequence_text": applied_sequence_text,
            "score": None,
            "eps": float(eps),
            "scale_metric": scale_metric,
            "score_details": None,
            "summary_path": summary_path,
            "plot_path": normalized_scale_plot_path,
            "csv_path": normalized_scale_csv_path,
            "between_plot_path": None,
            "between_csv_path": None,
            "normalized_scale_plot_path": normalized_scale_plot_path,
            "normalized_scale_csv_path": normalized_scale_csv_path,
        }
        self.repetition_history.append(record)
        index_entry = {
            "run_hash": runtime["run_hash"],
            "step_hash": runtime["step_hash"],
            "step_index": int(runtime["step_index"]),
            "step_id": runtime["step_id"],
            "base_method_id": runtime["base_method_id"],
            "artifact_type": "normalized_scale_scatter",
            "artifact_hash": runtime["artifact_hash"] or None,
            "artifact_label": runtime["artifact_label"] or None,
            "input_dataset": runtime["input_dataset"] or None,
            "scale_metric": scale_metric,
            "pipeline_sequence": list(runtime["pipeline_sequence"]),
            "pipeline_sequence_text": pipeline_sequence_text,
            "report_sequence": list(runtime["applied_sequence"]),
            "report_sequence_text": applied_sequence_text,
            "manifest_path": runtime["manifest_path"] or None,
            "artifact_paths": {
                "summary_path": summary_path,
                "within_csv_path": None,
                "within_plot_path": None,
                "between_csv_path": None,
                "between_plot_path": None,
                "normalized_scale_csv_path": normalized_scale_csv_path,
                "normalized_scale_plot_path": normalized_scale_plot_path,
            },
        }
        repeatability_index_path = self._upsert_repeatability_run_index(
            manifest_path=runtime["manifest_path"],
            run_hash=runtime["run_hash"],
            pipeline_sequence=runtime["pipeline_sequence"],
            pipeline_base_method_ids=runtime["pipeline_base_method_ids"],
            entry=index_entry,
        )
        summary_payload = self._load_json_if_exists(summary_path)
        summary_payload["repeatability_index_path"] = repeatability_index_path
        summary_payload["report_lookup_hint"] = (
            f"run_hash={runtime['run_hash']}; step={int(runtime['step_index']):02d}; "
            f"report_sequence={applied_sequence_text}"
        )
        self._write_json(summary_path, summary_payload)
        return np.asarray(X, dtype=float).copy(), np.asarray(wavelengths, dtype=float).copy()

    def preprocess_pipeline(self, X: np.ndarray, wavelengths: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        print(f"开始处理数据，原始形状: {X.shape}")
        x_processed = np.asarray(X, dtype=float).copy()
        wavelengths_processed = np.asarray(wavelengths, dtype=float).copy()

        method_sequence = config.get("preprocessing_sequence", [])
        if not isinstance(method_sequence, list):
            raise ValueError("preprocessing_sequence 必须是字符串列表")

        resolved_sequence: List[str] = []
        step_id_to_method_id: Dict[str, str] = {}
        for method_name in method_sequence:
            step_id = str(method_name).strip()
            if not step_id:
                continue
            base_method_id = step_id.split("#", 1)[0].split(":", 1)[0].strip()
            if base_method_id not in self._method_registry:
                raise ValueError(
                    f"非法预处理方法名: {method_name}。允许 canonical method_id: {list(self._method_registry.keys())}"
                )
            resolved_sequence.append(step_id)
            step_id_to_method_id[step_id] = base_method_id

        params_raw = config.get("preprocessing_method_params", {})
        if not isinstance(params_raw, dict):
            raise ValueError("preprocessing_method_params 必须是字典")

        resolved_params: Dict[str, Dict[str, Any]] = {}
        for method_name, method_param in params_raw.items():
            param_key = str(method_name).strip()
            if not param_key:
                continue
            base_method_id = param_key.split("#", 1)[0].split(":", 1)[0].strip()
            if base_method_id not in self._method_registry:
                raise ValueError(
                    f"非法预处理方法名: {method_name}。允许 canonical method_id: {list(self._method_registry.keys())}"
                )
            if method_param is None:
                resolved_params[param_key] = {}
                continue
            if not isinstance(method_param, dict):
                raise ValueError(f"preprocessing_method_params[{method_name}] 必须是字典")
            resolved_params[param_key] = dict(method_param)

        print("\n=== 开始预处理流水线 ===")
        print(f"原始数据形状: {x_processed.shape}")
        run_hash = self._new_run_hash(resolved_sequence)
        self._current_pipeline_run_id = run_hash
        print(f"Pipeline Run Hash: {run_hash}")

        run_dir = self._export_run_dir(run_hash)
        os.makedirs(run_dir, exist_ok=True)
        pipeline_base_method_ids = [step_id_to_method_id[sid] for sid in resolved_sequence]
        manifest_path = os.path.join(run_dir, f"{run_hash}__manifest.json")
        self._write_json(
            manifest_path,
            {
                "run_hash": run_hash,
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "pipeline_sequence": list(resolved_sequence),
                "pipeline_base_method_ids": list(pipeline_base_method_ids),
                "x_shape": list(np.asarray(X).shape),
                "wavelengths_shape": list(np.asarray(wavelengths).shape),
            },
        )

        for step_index, step_id in enumerate(resolved_sequence, start=1):
            base_method_id = step_id_to_method_id[step_id]
            step_params = dict(resolved_params.get(step_id) or resolved_params.get(base_method_id) or {})
            step_params["__step_id"] = step_id
            step_params["__step_index"] = int(step_index)
            step_params["__base_method_id"] = base_method_id
            step_params["__run_hash"] = run_hash
            step_params["__pipeline_sequence"] = list(resolved_sequence)
            step_params["__pipeline_base_method_ids"] = list(pipeline_base_method_ids)
            step_params["__applied_sequence"] = list(resolved_sequence[:step_index])
            step_params["__applied_base_method_ids"] = list(pipeline_base_method_ids[:step_index])
            step_params["__manifest_path"] = manifest_path
            x_processed, wavelengths_processed = self._method_registry[base_method_id](
                np.asarray(x_processed, dtype=float),
                np.asarray(wavelengths_processed, dtype=float),
                step_params,
            )

        self.last_pipeline_sequence = list(resolved_sequence)
        print(f"预处理方法执行顺序: {resolved_sequence}")
        print(f"预处理后数据形状: {x_processed.shape}")
        print("=== 预处理流水线完成 ===\n")

        self.save_processed_data(x_processed, wavelengths_processed)
        self._current_pipeline_run_id = None
        return x_processed, wavelengths_processed

    def evaluate_repetition(
        self,
        X: np.ndarray,
        eps: float,
        sample_indices: Optional[np.ndarray] = None,
        scale_metric: str = "norm",
    ) -> float:
        if eps <= 0:
            raise ValueError("evaluate_repetition 的 eps 必须大于 0")
        x_arr = np.asarray(X, dtype=float)
        if x_arr.ndim != 2 or x_arr.shape[0] == 0:
            raise ValueError("evaluate_repetition 要求输入为二维且非空矩阵")
        metric = self._normalize_repetition_scale_metric(scale_metric)

        if sample_indices is None:
            score, comparison_count, mean_similarity = self._compute_repetition_score(
                x_arr,
                eps=eps,
                scale_metric=metric,
            )
            self.last_repetition_score = float(score)
            self.last_repetition_details = {
                "reference_mode": "global_mean_spectrum",
                "scale_metric": metric,
                "scale_metric_description": self._describe_repetition_scale_metric(metric),
                "comparison_count": int(comparison_count),
                "mean_to_reference_similarity": float(mean_similarity),
                "overall_score": float(score),
            }
            return float(score)

        sample_ids = np.asarray(sample_indices).reshape(-1)
        if sample_ids.shape[0] != x_arr.shape[0]:
            raise ValueError("sample_indices 长度必须与 X 的样本数一致")

        sample_scores: List[float] = []
        sample_mean_spectra: List[np.ndarray] = []
        for sample_id in np.unique(sample_ids):
            group_indices = np.where(sample_ids == sample_id)[0]
            subset = x_arr[group_indices, :]
            group_score, _, _ = self._compute_repetition_score(
                subset,
                eps=eps,
                scale_metric=metric,
            )
            sample_scores.append(float(group_score))
            sample_mean_spectra.append(np.mean(subset, axis=0))

        if not sample_scores:
            self.last_repetition_score = 100.0
            self.last_repetition_details = {
                "reference_mode": "sample_mean_spectrum",
                "scale_metric": metric,
                "scale_metric_description": self._describe_repetition_scale_metric(metric),
                "within_sample_average_score": 100.0,
                "between_sample_mean_score": 100.0,
                "between_sample_difference_proxy": 0.0,
            }
            return 100.0

        within_score = float(np.mean(sample_scores))
        within_score = float(np.clip(within_score, 0.0, 100.0))

        sample_mean_matrix = np.asarray(sample_mean_spectra, dtype=float)
        between_score, between_comparison_count, between_mean_similarity = self._compute_repetition_score(
            sample_mean_matrix,
            eps=eps,
            scale_metric=metric,
        )
        between_difference_proxy = float(np.clip(100.0 - float(between_score), 0.0, 100.0))

        self.last_repetition_score = float(within_score)
        self.last_repetition_details = {
            "reference_mode": "sample_mean_spectrum",
            "scale_metric": metric,
            "scale_metric_description": self._describe_repetition_scale_metric(metric),
            "within_sample_average_score": float(within_score),
            "between_sample_mean_score": float(between_score),
            "between_sample_difference_proxy": float(between_difference_proxy),
            "between_sample_mean_to_reference_similarity": float(between_mean_similarity),
            "sample_mean_comparison_count": int(between_comparison_count),
            "sample_count": int(sample_mean_matrix.shape[0]),
        }
        return float(within_score)

    def _compute_repetition_score(
        self,
        X: np.ndarray,
        eps: float,
        scale_metric: str = "norm",
    ) -> Tuple[float, int, float]:
        return self._compute_mean_reference_direction_scale_score(
            X,
            eps=eps,
            scale_metric=scale_metric,
        )

    def get_preprocessing_info(self) -> Dict[str, Any]:
        return {
            "registered_methods": list(self._method_registry.keys()),
            "selected_wavelengths": self.selected_wavelengths,
            "last_repetition_score": self.last_repetition_score,
            "last_repetition_details": self.last_repetition_details,
            "last_pipeline_sequence": self.last_pipeline_sequence,
            "repetition_history": list(self.repetition_history),
        }

    def save_processed_data(self, x_data: np.ndarray, wavelengths: np.ndarray) -> str:
        os.makedirs(self.output_dir, exist_ok=True)
        x_processed_path = os.path.join(self.output_dir, "x_processed.csv")

        x_arr = np.asarray(x_data, dtype=float)
        wavelengths_arr = np.asarray(wavelengths, dtype=float).reshape(-1)
        if x_arr.ndim != 2:
            raise ValueError("save_processed_data 要求 x_data 为二维矩阵")
        if wavelengths_arr.shape[0] != x_arr.shape[1]:
            raise ValueError("save_processed_data 要求 wavelengths 长度与 x_data 列数一致")

        pd.DataFrame(x_arr, columns=wavelengths_arr).to_csv(x_processed_path, index=False)
        print("处理后数据已保存:")
        print(f"  X数据: {x_processed_path}")
        return x_processed_path
