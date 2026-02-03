### 5. 测试规范

#### 5.1 测试体系架构
- **测试框架**: 统一使用 `pytest`。
- **测试目录**: 所有测试代码存放于项目根目录下的 `test/` 文件夹。
    - `test/unit/`: **单元测试**。针对单个函数、类或模块的测试，不依赖外部环境（如数据库、网络）。
    - `test/integration/`: **集成测试**。测试多个模块间的交互，或完整的工作流。
    - `test/data/`: 存放测试所需的静态数据文件（如 CSV, JSON 样本）。

#### 5.2 命名与编写规范
- **文件命名**: `test_<模块名>.py` (例如 `test_data_loader.py`)。
- **类命名**: `class Test<功能名>:`。
- **函数命名**: `def test_<场景>_<预期结果>():` (例如 `test_load_invalid_file_raises_error`).
- **断言**: 使用标准的 `assert` 语句。
    - **错误示例**: `self.assertEqual(a, b)` (unittest 风格)
    - **正确示例**: `assert a == b` (pytest 风格)

#### 5.3 测试执行与环境
- **执行命令**: 必须在my-uv规定的虚拟环境下执行。
    ```powershell
    if (-not $env:PROJECT_ENV_NAME) { . SpecMd/scripts/get_env_name.ps1 | Out-Null }
    my-uv activate $env:PROJECT_ENV_NAME
    pytest test/ -v
    ```
- **Fixture 管理**: 
    - 通用 Fixture (如临时目录、模拟配置) 必须定义在 `test/conftest.py` 中。
    - 避免在测试函数内部进行复杂的初始化。

#### 5.4 测试报告输出标准
- **控制台输出**: 保持 `pytest` 的标准输出，失败时显示详细 diff。
- **文件输出** (如果 Agent 生成):
    - 格式: Markdown
    - 内容必须包含:
        1.  **测试概览**: 通过率、总耗时。
        2.  **失败用例详情**: 
            - 用例名称
            - 错误类型 (e.g., `ValueError`)
            - 关键堆栈信息 (Traceback)
        3.  **覆盖率报告** (可选): 使用 `pytest-cov` 生成的摘要。

#### 5.5 文件层级测试 (可选)
- 仅对于无副作用的纯工具函数文件，允许在文件底部添加 `if __name__ == '__main__':` 进行简单的冒烟测试。
- 正式测试必须放在 `test/` 目录下。
