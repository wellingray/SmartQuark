# SmartQuark - Smart Transfer & Ad-Cleaning Assistant 🚀

[![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)](#)
[![Python Version](https://img.shields.io/badge/python-3.8.10-green.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#)

**SmartQuark** is a Windows desktop productivity tool designed for content creators, community managers, and resource sharing enthusiasts. It supports batch transfer from both **Quark Cloud Drive** and **Baidu Netdisk**, automatically extracts share links and passwords (extraction codes) from pasted text, transfers them to your personal cloud drive in one click, performs deep recursive scanning to thoroughly remove third-party ads, promotional images, traffic-driving web pages and other junk files, generates brand-new share links and seamlessly replaces them back into the original formatted text, and supports one-click export of results to Excel files!

---

## 🌟 Core Features

*   🔗 **Smart Link & Extraction Code Recognition**: Automatically extracts Quark Cloud Drive links and Baidu Netdisk links (supports `s/1...` and `init?surl=...` formats) from pasted text via regex, and accurately identifies nearby 4-digit extraction codes or the `?pwd=` parameter in URLs.
*   📂 **Deep Multi-Cloud Support**:
    *   **Quark Cloud Drive**: Supports high-speed saving and ad cleaning.
    *   **Baidu Netdisk**: Supports full Web API simulation login, list query, anti-ban transfer, file cleanup, and share link re-creation.
*   📅 **Auto Date Archiving**: All transferred resources are structured and archived into `/微信群日更/YYYY/MM/DD/{ResourceName}/` folders in your cloud drive, keeping everything well organized.
*   🧼 **Deep Ad Cleaning with Size-Based Heuristics**:
    *   **Deep Recursion**: Recursively scans all subfolders under the transferred directory.
    *   **Promotional Folder Direct Deletion**: Folders with names containing clear promotional update features such as "追更", "每日更新", "更新就速存", "点我", "更①哈" will be deleted entirely without recursive scanning or renaming; ordinary "更新说明" (update notes) folders are not affected.
    *   **Image/Webpage Ad Direct Deletion**: For common extensions (`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.html`, `.url`, `.lnk`), files whose names contain sensitive keywords (such as `微信`, `公众号`, `5分打印`, `必看`, `必读`, etc.) will be physically deleted directly.
    *   **Size-Based Heuristics**: If an image is smaller than **150KB** and its filename contains any promotional character (such as `群`, `领`, `扫`, `码`, etc.), or if it is smaller than **100KB** and its filename consists purely of digits, timestamps, hyphens or underscores (e.g., `20250727-40652200.jpg`), or if it is any webpage or shortcut file, it will be forcibly deleted as a traffic-driving ad.
    *   **Core & Non-Core Document Cleaning**: For large resources like videos and archives, only sensitive keywords are stripped via renaming; for core documents such as `.docx`, `.pdf`, `.txt`, `.epub`, if the file size is **less than 100KB** and matches sensitive keywords, it will be judged as a micro traffic-driving document and physically deleted directly.
*   📝 **Perfect WeChat Text Format Preservation**: After conversion, the WeChat output box preserves all your original paragraphs, spaces, text formatting — only the links and extraction codes are precisely modified.
*   📊 **One-Click Excel Export**: Supports one-click export of successfully converted `(Resource Name, Resource Address)` data to an Excel spreadsheet. Exported Baidu Netdisk links are automatically reconstructed into direct-link format (e.g., `https://pan.baidu.com/s/xxxx?pwd=yyyy`), with Chinese characters like "提取码" removed, making it easy to import into systems or databases.
*   🔒 **Auto Configuration Memory & Merge**: Quark/Baidu cookies and filter keyword lists support local persistent storage in [gui_config.json](file:///D:/Antigravity/tools/SmartQuark/gui_config.json). Cookie input fields are hidden by default and can be toggled with "Show/Hide"; even after upgrading, newly added default ad keywords will automatically merge with your historical configuration, eliminating manual maintenance.
*   ⚡ **Multi-Threaded Concurrency Safety**: All transfer and cleaning operations are handled by background threads, completely eliminating window "freezing" and "not responding" issues.
*   🛡️ **Exception Protection & Timeout Mechanism**:
    *   The background transfer process includes top-level exception protection — no unexpected error will cause the UI to freeze, and button states are automatically restored.
    *   Quark Cloud Drive requests default to a 30-second timeout; task polling has a maximum retry limit (120 times) and supports manual user interruption, completely eliminating permanent thread hangs.
    *   All failed Baidu Netdisk API calls are logged in detail (`logging.error`) for easy diagnosis of cookie expiration, API changes, risk control, and other issues.

---

## 🖥️ UI Layout Preview

```
+------------------------------------------------------------------------------------+
|                      SmartQuark - Smart Transfer & Ad-Cleaning Assistant v1.0       |
+------------------------------------------------------------------------------------+
| Quark Cookie: [*******************************] [Show] [Remember Cookie] |
| Baidu Cookie: [*******************************] [Show] [Clear Cookie]   |
| Transfer Date: [ 2026/06/18 ]        Ad Filter Keywords: [ WeChat,Scan,JoinGroup,...] |
+------------------------------------------------------------------------------------+
| [ 1. Paste text with old Quark/Baidu links ]   | [ 2. Converted new text ]          |
|                                                |                                     |
| 【Baidu Resource】                             | 【Baidu Resource】                  |
| Link: https://pan.baidu.com/s/old1            | Link: https://pan.baidu.com/s/new1  |
| Extraction Code: abcd                         | Extraction Code: x1y2              |
|                                                |                                     |
+------------------------------------------------------------------------------------+
|                                                | [ Copy New Text ] [ Export Excel ]  |
+------------------------------------------------------------------------------------+
| [ Runtime Status Log ]                         | [ Ad Cleaning & Renaming Log ]      |
| [08:50:01] Login successful: Baidu User XXXX  | [08:50:05] Baidu Resource [Data] Ad files: |
| [08:50:02] Cleaning Baidu ad files...         |            - 5分打印.png deleted     |
| [08:50:10] Resource processing successful!    |                                     |
+------------------------------------------------------------------------------------+
|                     [  START BATCH TRANSFER & AD CLEANING  ]                     |
+------------------------------------------------------------------------------------+
```

---

## 📁 Project Structure

```
SmartQuark/
├── smart_quark.py          # Main program source code (GUI + Quark/Baidu Netdisk API + ad cleaning logic)
├── requirements.txt        # Python dependencies (requests, openpyxl)
├── .gitignore              # Git ignore rules
├── AGENTS.md               # AI agent development guidelines
├── README.md               # Project documentation (Chinese)
├── README_EN.md            # Project documentation (English)
├── tests/
│   ├── __init__.py
│   └── test_core.py        # Unit tests (core cleaning, link parsing, export & UI helper behaviors)
└── dist/
    └── SmartQuark.exe       # Compiled standalone executable
```

---

## 🛠️ Installation & Deployment

### 1. Clone / Download the Repository
```bash
git clone https://github.com/your-username/SmartQuark.git
cd SmartQuark
```

### 2. Runtime Environment
Ensure Python 3.8.10 is installed on your Windows system.

### 3. Install Dependencies
This project includes networking and Excel processing libraries:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Run from the console or terminal:
```bash
python smart_quark.py
```

---

## 🔑 How to Get Cookies

Since cloud drives have no public third-party API, the tool requires your cookies to simulate web-based transfer and share operations:

### Getting Quark Cloud Drive Cookie:
1. Open and log in to [Quark Cloud Drive Web](https://pan.quark.cn/) in your browser.
2. After successful login, press **F12** to open Developer Tools, then switch to the **Network** tab.
3. Refresh the page, and click any request named `info`, `sort`, or `list` in the network request list.
4. On the right side under **Headers** -> **Request Headers**, copy the full **`Cookie`** value.

### Getting Baidu Netdisk Cookie:
1. Open and log in to [Baidu Netdisk Web](https://pan.baidu.com/) in your browser.
2. After successful login, press **F12** to open Developer Tools, then switch to the **Network** tab.
3. Refresh the page, and click a request in the network request list (e.g., a `list` or `main` API request).
4. Find **`Cookie`** in its **Request Headers**, copy the full value, and paste it into the tool's `Baidu Cookie` input field.

---

## 🔮 Building a Standalone Executable (No Python Required)

If you need to run this software on a Windows computer without a Python environment, you can use PyInstaller to compile it into a standalone `.exe` application:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name SmartQuark smart_quark.py
```
After compilation, you can find the packaged single-file executable `SmartQuark.exe` in the `dist/` directory.

---

## 🧪 Running Unit Tests

The project includes 74 unit test cases covering filename cleaning, link parsing, ad classification, promotional folder deletion, interruptible waiting, Excel export behavior, and cookie show/hide toggle behavior:

```bash
python -m unittest tests.test_core -v
```

---

## ⚖️ License

This project is open-sourced under the [MIT License](file:///D:/Antigravity/tools/SmartQuark/LICENSE). It is intended for technical research and learning purposes only. Do not use it for commercial or illegal purposes.
