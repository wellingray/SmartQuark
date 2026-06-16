import os
import re
import sys
import io
import time
import random
import json
import logging
import threading
import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

# 强制标准输出采用 UTF-8 编码，若为 None (如 PyInstaller --noconsole 模式) 则重定向到 devnull
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
elif hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')
elif hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class QuarkBatchTransfer:
    BASE_URL = "https://drive-pc.quark.cn"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def __init__(self, cookie: str):
        self.cookie = cookie.strip()
        self.headers = {
            "cookie": self.cookie,
            "content-type": "application/json",
            "user-agent": self.USER_AGENT,
            "origin": "https://pan.quark.cn",
            "referer": "https://pan.quark.cn/"
        }

    def _send_request(self, method, url, **kwargs):
        if "headers" not in kwargs:
            kwargs["headers"] = self.headers
        try:
            response = requests.request(method, url, **kwargs)
            return response
        except Exception as e:
            logging.error(f"网络请求异常: {e}")
            return None

    def get_account_info(self):
        url = "https://pan.quark.cn/account/info"
        querystring = {"fr": "pc", "platform": "pc"}
        resp = self._send_request("GET", url, params=querystring)
        if resp and resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("data"):
                return res_json["data"]
        return None

    def get_fids(self, file_paths):
        url = f"{self.BASE_URL}/1/clouddrive/file/info/path_list"
        querystring = {"pr": "ucpro", "fr": "pc"}
        payload = {"file_path": file_paths, "namespace": "0"}
        resp = self._send_request("POST", url, json=payload, params=querystring)
        if resp and resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("code") == 0:
                return res_json.get("data", [])
        return []

    def mkdir(self, dir_path):
        url = f"{self.BASE_URL}/1/clouddrive/file"
        querystring = {"pr": "ucpro", "fr": "pc", "uc_param_str": ""}
        payload = {
            "pdir_fid": "0",
            "file_name": "",
            "dir_path": dir_path,
            "dir_init_lock": False,
        }
        resp = self._send_request("POST", url, json=payload, params=querystring)
        if resp and resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("code") == 0:
                return res_json.get("data")
        return None

    def get_stoken(self, pwd_id):
        url = f"{self.BASE_URL}/1/clouddrive/share/sharepage/token"
        querystring = {"pr": "ucpro", "fr": "pc"}
        payload = {"pwd_id": pwd_id, "passcode": ""}
        resp = self._send_request("POST", url, json=payload, params=querystring)
        if resp and resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("code") == 0 and res_json.get("data"):
                return res_json["data"].get("stoken")
        return None

    def get_detail(self, pwd_id, stoken):
        list_merge = []
        page = 1
        while True:
            url = f"{self.BASE_URL}/1/clouddrive/share/sharepage/detail"
            querystring = {
                "pr": "ucpro",
                "fr": "pc",
                "pwd_id": pwd_id,
                "stoken": stoken,
                "pdir_fid": "0",
                "force": "0",
                "_page": page,
                "_size": "50",
                "_fetch_banner": "0",
                "_fetch_share": "0",
                "_fetch_total": "1",
                "_sort": "file_type:asc,updated_at:desc",
                "ver": "2",
            }
            resp = self._send_request("GET", url, params=querystring)
            if not resp or resp.status_code != 200:
                break
            res_json = resp.json()
            if res_json.get("code") != 0:
                break
            if res_json.get("data", {}).get("list"):
                list_merge += res_json["data"]["list"]
                page += 1
            else:
                break
            if len(list_merge) >= res_json.get("metadata", {}).get("_total", 0):
                break
        return list_merge

    def save_file(self, fid_list, fid_token_list, to_pdir_fid, pwd_id, stoken):
        url = "https://drive.quark.cn/1/clouddrive/share/sharepage/save"
        querystring = {
            "pr": "ucpro",
            "fr": "pc",
            "uc_param_str": "",
            "app": "clouddrive",
            "__dt": int(random.uniform(1, 5) * 60 * 1000),
            "__t": int(time.time() * 1000),
        }
        payload = {
            "fid_list": fid_list,
            "fid_token_list": fid_token_list,
            "to_pdir_fid": to_pdir_fid,
            "pwd_id": pwd_id,
            "stoken": stoken,
            "pdir_fid": "0",
            "scene": "link",
        }
        resp = self._send_request("POST", url, json=payload, params=querystring)
        if resp and resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("code") == 0 and res_json.get("data"):
                return res_json["data"].get("task_id")
        return None

    def ls_dir(self, pdir_fid):
        list_merge = []
        page = 1
        while True:
            url = f"{self.BASE_URL}/1/clouddrive/file/sort"
            querystring = {
                "pr": "ucpro",
                "fr": "pc",
                "uc_param_str": "",
                "pdir_fid": pdir_fid,
                "_page": page,
                "_size": "50",
                "_fetch_total": "1",
                "_fetch_sub_dirs": "0",
                "_sort": "file_type:asc,updated_at:desc",
                "fetch_all_file": 1,
                "fetch_risk_file_name": 1,
            }
            resp = self._send_request("GET", url, params=querystring)
            if not resp or resp.status_code != 200:
                break
            res_json = resp.json()
            if res_json.get("code") != 0:
                return res_json
            if res_json.get("data", {}).get("list"):
                list_merge += res_json["data"]["list"]
                page += 1
            else:
                break
            if len(list_merge) >= res_json.get("metadata", {}).get("_total", 0):
                break
        return {"code": 0, "data": {"list": list_merge}}

    def delete(self, filelist):
        url = f"{self.BASE_URL}/1/clouddrive/file/delete"
        querystring = {"pr": "ucpro", "fr": "pc", "uc_param_str": ""}
        payload = {"action_type": 2, "filelist": filelist, "exclude_fids": []}
        resp = self._send_request("POST", url, json=payload, params=querystring)
        if resp and resp.status_code == 200:
            return resp.json()
        return None

    def share_files(self, fid_list, title):
        url = f"{self.BASE_URL}/1/clouddrive/share"
        querystring = {"pr": "ucpro", "fr": "pc", "uc_param_str": ""}
        payload = {
            "fid_list": fid_list,
            "title": title,
            "url_type": 1,      # 无密公开分享
            "expired_type": 1   # 永久有效
        }
        resp = self._send_request("POST", url, json=payload, params=querystring)
        if resp and resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("code") == 0 and res_json.get("data"):
                return res_json["data"].get("task_id")
        return None

    def query_task(self, task_id):
        retry_index = 0
        while True:
            url = f"{self.BASE_URL}/1/clouddrive/task"
            querystring = {
                "pr": "ucpro",
                "fr": "pc",
                "uc_param_str": "",
                "task_id": task_id,
                "retry_index": retry_index,
                "__dt": int(random.uniform(1, 5) * 60 * 1000),
                "__t": int(time.time() * 1000),
            }
            resp = self._send_request("GET", url, params=querystring)
            if not resp or resp.status_code != 200:
                time.sleep(1)
                continue
            res_json = resp.json()
            if res_json.get("status") != 200:
                return None
            
            task_status = res_json.get("data", {}).get("status")
            if task_status == 2:  # 成功
                return res_json
            elif task_status == 3:  # 失败
                return None
            else:
                retry_index += 1
                time.sleep(1)

    def get_share_link(self, share_id):
        url = f"{self.BASE_URL}/1/clouddrive/share/password"
        querystring = {"pr": "ucpro", "fr": "pc", "uc_param_str": ""}
        payload = {"share_id": share_id}
        resp = self._send_request("POST", url, json=payload, params=querystring)
        if resp and resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("code") == 0 and res_json.get("data"):
                return res_json["data"].get("share_url")
        return None


def get_id_from_url(url: str) -> str:
    pattern = r"/s/([a-zA-Z0-9]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return ""


class QuarkGUITool:
    CONFIG_FILE = "gui_config.json"

    def __init__(self, root):
        self.root = root
        self.root.title("SmartQuark - 智能转存与广告清理助手 v1.0")
        self.root.geometry("980x780")
        self.root.minsize(920, 720)

        # 加载配置
        self.config = self.load_config()

        # UI 字体及颜色配置
        self.font_title = ("Microsoft YaHei", 10, "bold")
        self.font_normal = ("Microsoft YaHei", 10)
        self.bg_color = "#f4f5f7"
        
        self.root.configure(bg=self.bg_color)
        
        self.transfer_thread = None
        self.stop_requested = False

        self.create_widgets()
        self.load_values_from_config()

    def create_widgets(self):
        # 1. 顶部配置框
        top_frame = tk.LabelFrame(self.root, text="基本参数配置", font=self.font_title, bg=self.bg_color, padx=10, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=10)

        # Cookie 输入
        tk.Label(top_frame, text="夸克 Cookie:", font=self.font_normal, bg=self.bg_color).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cookie_entry = ttk.Entry(top_frame, font=self.font_normal)
        self.cookie_entry.grid(row=0, column=1, columnspan=4, sticky=tk.EW, padx=5, pady=5)
        top_frame.columnconfigure(1, weight=1)

        self.remember_var = tk.BooleanVar(value=True)
        self.remember_cb = ttk.Checkbutton(top_frame, text="记住 Cookie", variable=self.remember_var)
        self.remember_cb.grid(row=0, column=5, padx=5, pady=5)

        # 日期 & 敏感词输入
        tk.Label(top_frame, text="转存日期:", font=self.font_normal, bg=self.bg_color).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(top_frame, font=self.font_normal, width=15)
        self.date_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y/%m/%d"))
        
        tk.Label(top_frame, text=" (格式: YYYY/MM/DD) ", font=self.font_normal, bg=self.bg_color, fg="#666").grid(row=1, column=2, sticky=tk.W)

        tk.Label(top_frame, text="广告敏感词 (逗号分隔):", font=self.font_normal, bg=self.bg_color).grid(row=1, column=3, sticky=tk.E, padx=5, pady=5)
        self.kw_entry = ttk.Entry(top_frame, font=self.font_normal)
        self.kw_entry.grid(row=1, column=4, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        self.kw_entry.insert(0, "微信,扫码,获取更多,加群")

        # 2. 底部操作栏
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=(0, 15))

        self.start_btn = tk.Button(btn_frame, text="开始批量转存与广告清理", font=("Microsoft YaHei", 11, "bold"), bg="#28a745", fg="white", activebackground="#218838", activeforeground="white", relief=tk.FLAT, pady=8, command=self.start_transfer)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.stop_btn = tk.Button(btn_frame, text="停止任务", font=("Microsoft YaHei", 11, "bold"), bg="#dc3545", fg="white", activebackground="#c82333", activeforeground="white", relief=tk.FLAT, pady=8, state="disabled", width=15, command=self.stop_transfer)
        self.stop_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 3. 下部日志显示区
        bottom_frame = tk.Frame(self.root, bg=self.bg_color)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=10)
        bottom_frame.columnconfigure(0, weight=3)
        bottom_frame.columnconfigure(1, weight=2)

        # 执行日志
        log_frame = tk.LabelFrame(bottom_frame, text="运行状态日志", font=self.font_title, bg=self.bg_color, padx=5, pady=5)
        log_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5))
        self.log_text = tk.Text(log_frame, font=self.font_normal, height=8, bg="#1e1e1e", fg="#d4d4d4", state="disabled", wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 广告清理日志
        ad_frame = tk.LabelFrame(bottom_frame, text="广告清理日志", font=self.font_title, bg=self.bg_color, padx=5, pady=5)
        ad_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=(5, 0))
        self.ad_log_text = tk.Text(ad_frame, font=self.font_normal, height=8, bg="#1e1e1e", fg="#ff6b6b", state="disabled", wrap=tk.WORD)
        self.ad_log_text.pack(fill=tk.BOTH, expand=True)

        # 4. 中部文案处理区
        mid_frame = tk.Frame(self.root, bg=self.bg_color)
        mid_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=5)
        mid_frame.columnconfigure(0, weight=1)
        mid_frame.columnconfigure(1, weight=1)
        mid_frame.rowconfigure(0, weight=1)

        # 左侧输入
        left_frame = tk.LabelFrame(mid_frame, text=" 1. 请粘贴包含旧夸克链接的文案 ", font=self.font_title, bg=self.bg_color, padx=5, pady=5)
        left_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 5))
        
        self.input_text = tk.Text(left_frame, font=self.font_normal, wrap=tk.WORD, undo=True)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        # 右侧输出
        right_frame = tk.LabelFrame(mid_frame, text=" 2. 转换替换后的新文案 ", font=self.font_title, bg=self.bg_color, padx=5, pady=5)
        right_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=(5, 0))

        self.copy_btn = ttk.Button(right_frame, text="一键复制新文案", command=self.copy_output)
        self.copy_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        self.output_text = tk.Text(right_frame, font=self.font_normal, wrap=tk.WORD)
        self.output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        config_data = {
            "cookie": self.cookie_entry.get().strip() if self.remember_var.get() else "",
            "remember": self.remember_var.get(),
            "keywords": self.kw_entry.get().strip(),
        }
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_values_from_config(self):
        if self.config:
            if self.config.get("remember"):
                self.cookie_entry.insert(0, self.config.get("cookie", ""))
                self.remember_var.set(True)
            else:
                self.remember_var.set(False)
            
            if self.config.get("keywords"):
                self.kw_entry.delete(0, tk.END)
                self.kw_entry.insert(0, self.config.get("keywords"))

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}\n"
        self.root.after(0, self._insert_log, formatted)

    def _insert_log(self, text):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def log_ad_deletion(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}\n"
        self.root.after(0, self._insert_ad_log, formatted)

    def _insert_ad_log(self, text):
        self.ad_log_text.configure(state="normal")
        self.ad_log_text.insert(tk.END, text)
        self.ad_log_text.see(tk.END)
        self.ad_log_text.configure(state="disabled")

    def update_output_text(self, text):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)

    def copy_output(self):
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("警告", "没有可复制的内容！")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("成功", "文案已成功复制到剪贴板！")

    def start_transfer(self):
        cookie = self.cookie_entry.get().strip()
        if not cookie:
            messagebox.showerror("错误", "请输入有效的夸克 Cookie！")
            return
        
        input_content = self.input_text.get("1.0", tk.END).strip()
        if not input_content:
            messagebox.showerror("错误", "请输入或粘贴待转换的微信文案！")
            return

        date_str = self.date_entry.get().strip().replace("-", "/").replace(".", "/")
        if not re.match(r"^\d{4}/\d{2}/\d{2}$", date_str):
            messagebox.showerror("错误", "日期格式不正确！请输入形如 YYYY/MM/DD 的日期。")
            return

        # 临时保存设置
        self.save_config()

        # 初始化状态并启动后台线程
        self.start_btn.configure(state="disabled", bg="#6c757d")
        self.stop_btn.configure(state="normal")
        self.stop_requested = False
        
        # 清空输出与日志
        self.update_output_text("")
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")
        self.ad_log_text.configure(state="normal")
        self.ad_log_text.delete("1.0", tk.END)
        self.ad_log_text.configure(state="disabled")

        self.transfer_thread = threading.Thread(target=self.run_transfer_process, args=(cookie, date_str, input_content))
        self.transfer_thread.daemon = True
        self.transfer_thread.start()

    def stop_transfer(self):
        if self.transfer_thread and self.transfer_thread.is_alive():
            self.stop_requested = True
            self.log_message("收到停止指令，正在安全退出当前转存任务...")
            self.stop_btn.configure(state="disabled")

    def run_transfer_process(self, cookie, date_str, original_text):
        transfer = QuarkBatchTransfer(cookie)
        
        self.log_message("正在验证 Cookie 有效性...")
        account_info = transfer.get_account_info()
        if not account_info:
            self.log_message("Cookie 验证失败！请检查您的 Cookie 是否已过期。")
            self.root.after(0, self.finish_process)
            return

        nickname = account_info.get("nickname", "未知用户")
        self.log_message(f"登录成功！账号昵称: {nickname}")

        # 提取敏感词列表
        kw_str = self.kw_entry.get().strip()
        blacklist_keywords = [k.strip() for k in re.split(r"[,，]", kw_str) if k.strip()]
        self.log_message(f"过滤广告敏感词: {blacklist_keywords}")

        # 解析出目标文件夹目录
        dest_path = f"/微信群日更/{date_str}"
        self.log_message(f"目标网盘目录: {dest_path}")

        # 检查或创建路径
        fids_info = transfer.get_fids([dest_path])
        dest_fid = None
        for item in fids_info:
            if item.get("file_path") == dest_path:
                dest_fid = item.get("fid")
                break
        
        if self.stop_requested:
            self.log_message("任务已中止。")
            self.root.after(0, self.finish_process)
            return

        if not dest_fid:
            self.log_message("目标日期目录不存在，正在自动创建...")
            mkdir_res = transfer.mkdir(dest_path)
            if mkdir_res:
                dest_fid = mkdir_res.get("fid")
                self.log_message(f"日期目录创建成功，fid: {dest_fid}")
            else:
                self.log_message("创建日期目录失败，任务退出。")
                self.root.after(0, self.finish_process)
                return
        else:
            self.log_message(f"目录已存在，使用当前 fid: {dest_fid}")

        # 提取所有的夸克链接
        links = list(set(re.findall(r"https://pan\.quark\.cn/s/[a-zA-Z0-9]+", original_text)))
        total_links = len(links)
        self.log_message(f"在文案中共识别出 {total_links} 个独立夸克网盘链接。")

        if total_links == 0:
            self.log_message("无待转存链接，任务结束。")
            self.root.after(0, self.update_output_text, original_text)
            self.root.after(0, self.finish_process)
            return

        batch_fid = None
        link_map = {}
        current_text = original_text

        for idx, old_link in enumerate(links, 1):
            if self.stop_requested:
                self.log_message("任务被用户中止。已完成的转换已保存。")
                break

            self.log_message(f"--------------------------------------------------")
            self.log_message(f"[{idx}/{total_links}] 正在处理链接: {old_link}")
            
            pwd_id = get_id_from_url(old_link)
            if not pwd_id:
                self.log_message("解析链接 ID 失败，跳过。")
                continue

            # 1. 获取 stoken
            stoken = transfer.get_stoken(pwd_id)
            if not stoken:
                self.log_message("获取分享 Token 失败，链接可能已失效或被风控限制。")
                continue

            # 2. 获取分享详情
            detail_list = transfer.get_detail(pwd_id, stoken)
            if not detail_list:
                self.log_message("获取分享详情失败，或者分享文件夹已空。")
                continue

            # 提取保存名（以分享中首个文件名命名）
            book_name = detail_list[0].get("file_name", "未知资源")
            self.log_message(f"识别出资源名称: {book_name}")

            # 如果是该批次第一个成功获取详情的资源，创建“核心资源+等”归档文件夹
            if batch_fid is None:
                # 过滤文件名中的非法字符
                safe_book_name = re.sub(r'[\\/:*?"<>|]', "_", book_name)
                batch_folder_name = f"{safe_book_name}等"
                batch_folder_path = f"{dest_path}/{batch_folder_name}"
                self.log_message(f"创建批次归档文件夹: {batch_folder_path}")
                
                fids_info = transfer.get_fids([batch_folder_path])
                for item in fids_info:
                    if item.get("file_path") == batch_folder_path:
                        batch_fid = item.get("fid")
                        break
                
                if not batch_fid:
                    mkdir_res = transfer.mkdir(batch_folder_path)
                    if mkdir_res:
                        batch_fid = mkdir_res.get("fid")
                        self.log_message(f"批次归档文件夹创建成功，fid: {batch_fid}")
                    else:
                        self.log_message("创建批次归档文件夹失败，将直接保存至日期根目录。")
                        batch_fid = dest_fid

            target_save_fid = batch_fid if batch_fid else dest_fid

            fid_list = [item["fid"] for item in detail_list]
            fid_token_list = [item["share_fid_token"] for item in detail_list]

            # 3. 转存文件
            save_task_id = transfer.save_file(fid_list, fid_token_list, target_save_fid, pwd_id, stoken)
            if not save_task_id:
                self.log_message("创建转存任务失败。")
                continue

            save_res = transfer.query_task(save_task_id)
            if not save_res:
                self.log_message("转存任务在网盘执行失败。")
                continue

            save_as_top_fids = save_res.get("data", {}).get("save_as", {}).get("save_as_top_fids")
            if not save_as_top_fids:
                self.log_message("未取得保存后的文件 ID 列表。")
                continue

            # 4. 广告清理
            for saved_fid in save_as_top_fids:
                # 遍历文件夹看有无广告
                contents = transfer.ls_dir(saved_fid)
                if contents and isinstance(contents, dict) and contents.get("code") == 0:
                    file_list = contents.get("data", {}).get("list", [])
                    ad_fids = []
                    ad_names = []
                    for file_item in file_list:
                        name = file_item.get("file_name", "")
                        is_ad = False
                        for kw in blacklist_keywords:
                            if kw and kw in name:
                                is_ad = True
                                break
                        if is_ad:
                            ad_fids.append(file_item.get("fid"))
                            ad_names.append(name)
                    
                    if ad_fids:
                        del_res = transfer.delete(ad_fids)
                        if del_res and del_res.get("code") == 0:
                            for name in ad_names:
                                self.log_ad_deletion(f"资源 [{book_name}] 广告 [{name}] 已删除")
                        else:
                            self.log_ad_deletion(f"资源 [{book_name}] 广告删除失败: {del_res}")

            # 5. 重新分享
            share_task_id = transfer.share_files(save_as_top_fids, book_name)
            if not share_task_id:
                self.log_message("创建分享任务失败。")
                continue

            share_res = transfer.query_task(share_task_id)
            if not share_res:
                self.log_message("重新分享任务执行失败。")
                continue

            share_id = share_res.get("data", {}).get("share_id")
            if not share_id:
                self.log_message("未获取到有效的分享 ID。")
                continue

            # 6. 获取新分享链接
            new_share_link = transfer.get_share_link(share_id)
            if not new_share_link:
                self.log_message("获取新分享链接失败。")
                continue

            # 映射新老链接
            link_map[old_link] = new_share_link
            self.log_message(f"转存及清理成功！新链接: {new_share_link}")

            # 实时更新输出文案，提升用户感知
            current_text = current_text.replace(old_link, new_share_link)
            self.root.after(0, self.update_output_text, current_text)

            # 防风控休眠
            if idx < total_links:
                sleep_time = random.uniform(3.0, 5.0)
                self.log_message(f"休眠 {sleep_time:.2f} 秒以保护账号...")
                time.sleep(sleep_time)

        self.log_message(f"\n==================================================")
        self.log_message(f"批量转存与广告清理流程结束！")
        self.log_message(f"==================================================")
        
        self.root.after(0, self.finish_process)

    def finish_process(self):
        self.start_btn.configure(state="normal", bg="#28a745")
        self.stop_btn.configure(state="disabled")
        messagebox.showinfo("完成", "批量转存和链接替换已完成！")


if __name__ == '__main__':
    root = tk.Tk()
    app = QuarkGUITool(root)
    root.mainloop()
