# SmartQuark - Agent Customization Rules & Guidelines / 代理人定制规范与指南 🤖

This document defines project-scoped guidelines and rules for coding, building, and maintaining the SmartQuark application.
本项目定义了 SmartQuark 应用程序开发、编译和维护的项目级规范与准则。

---

## 🐍 Python Environment & GUI Constraints / Python 环境与 GUI 约束

### English
* **Python Compatibility**: Code must remain strictly compatible with **Python 3.8.10**. Do not use features from Python 3.9+ (e.g., `removeprefix`, union operators `|` in type hints, etc.).
* **GUI Framework**: Built using Python's built-in `tkinter` and `ttk`.
  * Ensure the window is responsive and resizable.
  * Do not block the main Tkinter mainloop. All heavy network requests, file listings, and deletions **must** run asynchronously in a background worker thread (`threading.Thread`).
  * **Thread Safety**: Never read UI widget values (e.g., `Entry.get()`) from a background thread. Extract all widget values in the main thread **before** launching the worker, and pass them as function arguments.
  * Cookie entry fields should default to masked display and provide a "show/hide" toggle for local personal use.
* **Network Requests**:
  * All `requests` calls **must** include a `timeout` parameter (default: 30s for Quark, 10s for Baidu).
  * Polling loops (e.g., `query_task`) **must** have a maximum retry limit and check `stop_requested` to allow user cancellation. Never use bare `while True` without exit conditions.
* **Configuration Persistence**:
  * Persistent user configurations are stored in `gui_config.json`.
  * `CONFIG_FILE` path **must** use `get_app_dir()` to resolve an absolute path, ensuring stability when launched from shortcuts or other working directories.
  * When loading configurations, ensure that new default keyword filters (e.g., `进群`, `领取`, `5分打印`, `必看`, `必读`, `加微`, `更多课程`, `免费大放送`, `更多整理`) are **automatically merged** into the loaded configurations so they are active on start.

### 中文
* **Python 兼容性**：代码必须严格兼容 **Python 3.8.10**。严禁使用 Python 3.9 及以上版本的新特性（例如：`removeprefix` 方法、类型提示中的联合运算符 `|` 等）。
* **GUI 框架**：使用 Python 内置的 `tkinter` 和 `ttk` 构建。
  * 确保窗口具有良好的自适应响应能力并且可调整大小。
  * 严禁阻塞 Tkinter 主事件循环。所有耗时的网络请求、文件列表获取及删除操作**必须**在后台工作线程 (`threading.Thread`) 中异步运行。
  * **线程安全**：严禁在后台线程中直接读取 UI 控件值（如 `Entry.get()`）。必须在主线程中提取所有控件值，再作为函数参数传入后台线程。
  * Cookie 输入框默认应隐藏显示，并提供“显示/隐藏”切换按钮，便于个人本机使用。
* **网络请求**：
  * 所有 `requests` 调用**必须**包含 `timeout` 参数（夸克默认 30 秒，百度默认 10 秒）。
  * 轮询循环（如 `query_task`）**必须**设置最大重试次数，并检查 `stop_requested` 以支持用户取消。严禁使用无退出条件的 `while True`。
* **配置持久化**：
  * 用户持久化配置保存在 `gui_config.json` 中。
  * `CONFIG_FILE` 路径**必须**使用 `get_app_dir()` 拼接为绝对路径，确保从快捷方式或其他工作目录启动时路径稳定。
  * 加载配置时，必须**自动合并**新增的默认过滤词（如：`进群`、`领取`、`5分打印`、`必看`、`必读`、`加微`、`更多课程`、`免费大放送`、`更多整理`）至已读取的配置中，确保它们在启动时自动处于激活状态。

---

## 🧹 Ad-Cleaning Heuristics & Rules / 广告清理启发式规则

### English
* **Resource Preservation**: Core files (such as `.mp4`, `.zip`, `.rar`, `.pdf`, `.epub`, etc.) must **never** be deleted. If they contain sensitive words in their filenames, rename them instead.
* **Image & Webpage Ad Cleanup**:
  * Delete files with extensions `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.html`, `.url`, `.lnk` if they match the blacklist keywords.
  * **Size-based Heuristic**: Any image file smaller than **150KB** that contains any single promo character (e.g., `群`, `领`, `众`, `信`, `微`, `扫`, `码`, `加`, `粉`, `福利`) must be deleted automatically.
  * **Numeric/Timestamp Heuristic**: Any image file smaller than **100KB** whose filename (excluding extension) consists purely of digits, hyphens, or underscores (e.g., `20250727-40652200.jpg`) must be deleted automatically.
  * **Small Document/Core Cleanup**: Any document or core file (such as `.docx`, `.pdf`, `.txt`, `.epub`, etc.) smaller than **100KB** that matches any sensitive blacklist keyword must be deleted automatically instead of renamed.
  * **Shortcut Cleanup**: Any `.html`, `.url`, or `.lnk` file is considered a promotion and must be deleted.
  * **Domain & Website Cleanup**: Detect domain/website name patterns (e.g., `cunlove.cn`, `www.xx.com`) in filenames. If found, treat the file as sensitive (delete if it's an image/shortcut/webpage/small-doc <100KB, or strip the domain name and any enclosing bracket like `【...domain...】` during renaming if it is a core resource >=100KB).

### 中文
* **核心资源保护**：核心文件（如 `.mp4`, `.zip`, `.rar`, `.pdf`, `.epub` 等）**严禁直接删除**。若其文件名包含敏感词，应通过重命名将其剥离净化。
* **图片及网页广告清理**：
  * 对于 `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.html`, `.url`, `.lnk` 扩展名的文件，如果匹配黑名单敏感词，则直接物理删除。
  * **基于体积的启发式规则**：任何小于 **150KB** 且包含任意推广单字（例如：`群`、`领`、`众`、`信`、`微`、`扫`、`码`、`加`、`粉`、`福利`）的图片文件，必须自动执行物理删除。
  * **纯数字/时间戳名图片清理**：任何小于 **100KB** 且文件名（不含后缀）完全由数字、减号或下划线组成（例如：`20250727-40652200.jpg`）的图片文件，必须自动执行物理删除。
  * **小体积核心文档清理**：任何小于 **100KB** 且匹配到敏感词的核心资源（如 `.docx`, `.pdf`, `.txt`, `.epub` 等），必须自动执行物理删除，不再进行重命名。
  * **快捷链接清理**：任何 `.html`、`.url` 或 `.lnk` 文件均直接视为广告推广，一律自动物理删除。
  * **网址与域名清理**：自动检测文件名中的网址与域名特征（如 `cunlove.cn`、`www.xx.com`）。如果存在，一律判定为敏感广告（若为图片、网页或小于100KB的核心文档等则直接物理删除；若为大于等于100KB的核心资源文件，则在重命名时将域名及包含该域名的括号如 `【...域名...】` 整体进行剥离净化）。

---

## 📊 Exporting & Formatting Rules / 导出与排版规范

### English
* **WeChat Content Textbox**: Keep the original human-readable WeChat layout format intact (e.g., `链接 提取码: xxxx`) so that users can copy/paste it directly to group chats.
* **Excel Exporting**:
  * The export function creates a fresh workbook directly; do not depend on `Import_Template/资源导入模板.xlsx` or any other Excel template file.
  * Format links cleanly for columns A (Resource Name) and B (Resource Address).
  * Baidu Netdisk links must **never** contain the Chinese characters "提取码".
  * Format password parameters directly into the URL query string: use `?pwd={pwd}` if the link has no parameters, or `&pwd={pwd}` if it does.

### 中文
* **微信输出文本框**：保留微信群友好的可读排版格式（例如：`链接 提取码: xxxx`），便于用户一键复制后直接粘贴发布到微信群中。
* **Excel 一键导出**：
  * 导出功能直接创建新的工作簿；不要依赖 `Import_Template/资源导入模板.xlsx` 或任何其他 Excel 模板文件。
  * A 列（资源名称）和 B 列（资源地址）链接格式应整洁规范。
  * 导出的百度网盘资源地址中**严禁包含"提取码"等中文字符**。
  * 必须将密码参数直接转换为 URL 查询字符串形式：如果原链接无参数则使用 `?pwd={pwd}`，已有参数则使用 `&pwd={pwd}`。

---

## 🚨 Error Handling & Robustness / 异常处理与健壮性

### English
* **Top-level Exception Guard**: The `run_transfer_process` method **must** wrap its entire body in `try/except`. Any uncaught exception must call `finish_process("failed")` to restore UI button states and display an error message. The UI must **never** freeze due to an unhandled background thread exception.
* **No Silent Exception Swallowing**: Never use bare `except Exception: pass`. All exception handlers **must** log the error reason via `logging.error(f"context: {e}")` at minimum, so issues like expired cookies, API changes, or rate limiting can be diagnosed.

### 中文
* **顶层异常防护**：`run_transfer_process` 方法的整个函数体**必须**包裹在 `try/except` 中。任何未捕获的异常都必须调用 `finish_process("failed")` 恢复 UI 按钮状态并显示错误提示。严禁因后台线程的未处理异常导致界面卡死。
* **禁止静默吞掉异常**：严禁使用 `except Exception: pass`。所有异常处理**必须**至少通过 `logging.error(f"上下文: {e}")` 记录错误原因，以便排查 Cookie 过期、接口变更、风控等问题。

---

## 🧪 Testing / 测试规范

### English
* **Unit Tests**: Core pure functions (`clean_filename`, `parse_baidu_links`, ad file classification logic) **must** have unit test coverage under `tests/`.
* **Test Runner**: Tests are run with `python -m unittest tests.test_core -v` using the `.venv38` Python environment.
* **Before Merging**: All existing tests must pass before committing changes to core logic functions.

### 中文
* **单元测试**：核心纯函数（`clean_filename`、`parse_baidu_links`、广告文件分类逻辑）**必须**在 `tests/` 目录下有单元测试覆盖。
* **测试执行**：使用 `.venv38` Python 环境运行 `python -m unittest tests.test_core -v`。
* **提交前检查**：修改核心逻辑函数前，必须确保所有已有测试通过。

---

## 📦 Build & Release Protocol / 构建与打包协议

### English
* **PyInstaller Compilation**: Build the standalone, windowless executable inside the local `.venv38` environment:
  ```powershell
  d:\Antigravity\tools\SmartQuark\.venv38\Scripts\pyinstaller.exe --onefile --noconsole --name SmartQuark smart_quark.py
  ```
* **Process Locking Check**: Always stop running instances of `SmartQuark.exe` before rebuilding to prevent file lock errors:
  ```powershell
  Stop-Process -Name "SmartQuark" -Force -ErrorAction SilentlyContinue
  ```

### 中文
* **PyInstaller 编译**：在本地的 `.venv38` 虚拟环境中编译无控制台窗口的独立可执行程序：
  ```powershell
  d:\Antigravity\tools\SmartQuark\.venv38\Scripts\pyinstaller.exe --onefile --noconsole --name SmartQuark smart_quark.py
  ```
* **防止文件占用锁定**：重新编译打包前，务必先强制终止运行中的 `SmartQuark.exe` 实例，以防止因文件写入锁定导致打包报错：
  ```powershell
  Stop-Process -Name "SmartQuark" -Force -ErrorAction SilentlyContinue
  ```
