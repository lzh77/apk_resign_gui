"""
APK重签名GUI应用程序
应用程序的主入口点
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import tempfile
import zipfile
import subprocess
import shutil
from pathlib import Path
import json
import threading
import queue

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    print("Warning: tkinterdnd2 not found. Drag and drop functionality will be disabled.")
    TkinterDnD = None

from constants import VERSION
from config_manager import ConfigManager
from signing_processor import SigningProcessor
from profile_dialog import ManageProfilesDialog


class APKResignGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"APK重签名工具 v{VERSION}")
        self.root.geometry("600x400")  # 调整大小适应新布局
        
        # 设置窗口图标
        self.set_window_icon()
        
        # 初始化配置管理器
        self.config_manager = ConfigManager("~//.apk_resign_gui_config.json")
        
        # 初始化变量
        self.sdk_path = tk.StringVar(value=self.config_manager.get_sdk_path())
        self.apk_path = tk.StringVar()
        
        # 当前选中的签名配置
        self.current_profile = tk.StringVar(value="default")
        
        # 用于进度更新的队列
        self.progress_queue = queue.Queue()
        
        # 创建控件
        self.create_widgets()
        
        # 更新签名配置下拉菜单
        self.update_profiles_list()
    
    def set_window_icon(self):
        """设置窗口图标"""
        import sys
        if getattr(sys, 'frozen', False):
            # 如果是PyInstaller打包后的可执行文件
            import os
            # 获取可执行文件所在的目录
            bundle_dir = sys._MEIPASS
            icon_path = os.path.join(bundle_dir, 'icon.ico')
        else:
            # 开发环境中
            icon_path = "icon.ico"
        
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"加载主窗口图标失败: {e}")
        else:
            print(f"图标文件不存在: {icon_path}")

    def save_config(self):
        """保存配置到文件"""
        self.config_manager.save_config(self.sdk_path.get())

    def create_widgets(self):
        """创建并布局GUI控件"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="APK重签名工具", font=("Microsoft YaHei", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 更新根窗口的权重，使网格能正确拉伸
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # SDK路径选择
        ttk.Label(main_frame, text="Android SDK路径:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        sdk_entry = ttk.Entry(main_frame, textvariable=self.sdk_path, width=50)
        sdk_entry.grid(row=1, column=1, columnspan=2, padx=(10, 0), pady=(0, 5))
        ttk.Button(main_frame, text="浏览", command=self.browse_sdk).grid(row=1, column=3, padx=(10, 0), pady=(0, 5))
        
        # 签名配置选择
        ttk.Label(main_frame, text="签名配置:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.profiles_combo = ttk.Combobox(main_frame, textvariable=self.current_profile, state="readonly", width=50)
        self.profiles_combo.grid(row=2, column=1, padx=(10, 0), pady=(0, 5))
        ttk.Button(main_frame, text="管理", command=self.manage_profiles).grid(row=2, column=2, padx=(10, 0), pady=(0, 5))
        
        # APK文件选择
        ttk.Label(main_frame, text="选择APK文件:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        apk_entry = ttk.Entry(main_frame, textvariable=self.apk_path, width=50)
        apk_entry.grid(row=3, column=1, padx=(10, 0), pady=(0, 5))
        # 启用APK文件拖拽功能
        if hasattr(self.root, 'dnd_bind'):
            apk_entry.drop_target_register(DND_FILES)
            apk_entry.dnd_bind('<<Drop>>', self.on_apk_drop)
        ttk.Button(main_frame, text="浏览", command=self.browse_apk).grid(row=3, column=2, padx=(10, 0), pady=(0, 5))
        
        # 处理按钮
        ttk.Button(main_frame, text="重签名APK", command=self.resign_apk).grid(row=8, column=0, columnspan=4, pady=(20, 0))
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='determinate', length=400)
        self.progress.grid(row=9, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪", foreground="blue")
        self.status_label.grid(row=10, column=0, columnspan=4, pady=(10, 0))

    def update_profiles_list(self):
        """更新签名配置列表"""
        profiles = list(self.config_manager.get_all_profiles().keys())
        self.profiles_combo['values'] = profiles
        if self.current_profile.get() in profiles:
            self.profiles_combo.set(self.current_profile.get())
        elif profiles:
            self.current_profile.set(profiles[0])

    def manage_profiles(self):
        """管理签名配置"""
        ManageProfilesDialog(self.root, self)

    def browse_sdk(self):
        """打开文件对话框选择Android SDK目录"""
        directory = filedialog.askdirectory(
            title="选择Android SDK目录",
            initialdir=self.sdk_path.get() or os.path.expanduser("~/AppData/Local/Android/Sdk")
        )
        if directory:
            self.sdk_path.set(directory)
            # 立即保存配置
            self.save_config()

    def browse_apk(self):
        """打开文件对话框选择APK文件"""
        filename = filedialog.askopenfilename(
            title="选择APK文件",
            filetypes=[("APK文件", "*.apk"), ("所有文件", "*.*")]
        )
        if filename:
            self.apk_path.set(filename)

    def on_apk_drop(self, event):
        """处理APK文件拖拽事件"""
        # 获取拖拽的文件路径
        dropped_file = self.root.tk.splitlist(event.data)[0]  # 只取第一个文件
        # 检查文件扩展名
        if dropped_file.lower().endswith('.apk'):
            self.apk_path.set(dropped_file)
        else:
            messagebox.showerror("错误", "请选择有效的APK文件")

    def resign_apk(self):
        """处理APK重签名过程"""
        if not self.apk_path.get():
            messagebox.showerror("错误", "请选择一个APK文件")
            return
            
        # 获取当前配置
        profile_name = self.current_profile.get()
        profile = self.config_manager.get_profile(profile_name)
        
        keystore_path = profile.get("keystore_path", "")
        storepass = profile.get("storepass", "")
        key_alias = profile.get("key_alias", "")
        
        if not keystore_path:
            messagebox.showerror("错误", f"签名配置 '{profile_name}' 中未设置密钥库路径")
            return
            
        if not storepass:
            messagebox.showerror("错误", f"签名配置 '{profile_name}' 中未设置密码")
            return
            
        if not key_alias:
            messagebox.showerror("错误", f"签名配置 '{profile_name}' 中未设置密钥别名")
            return
        
        # 保存配置
        self.save_config()
        
        # 检查是否有必要的工具
        processor = SigningProcessor(self.sdk_path.get())
        tool_check_result = processor.check_tools()
        if not tool_check_result[0]:
            messagebox.showerror("错误", f"缺少必要的工具: {tool_check_result[1]}，请确保已安装Android SDK并在PATH中\n\n调试信息：{tool_check_result[2]}")
            return
        
        # 开始处理
        self.status_label.config(text="正在处理...")
        self.progress['value'] = 0  # 重置进度条
        
        # 在新线程中执行重签名
        thread = threading.Thread(target=processor.perform_resign, 
                                  args=(self.apk_path.get(), keystore_path, storepass, key_alias, self.progress_queue))
        thread.daemon = True
        thread.start()
        
        # 启动进度更新检查
        self.check_progress()
    
    def check_progress(self):
        """检查进度更新"""
        # 检查队列中的消息
        try:
            while True:
                msg = self.progress_queue.get_nowait()
                if msg['type'] == 'progress':
                    self.progress['value'] = msg['value']
                    self.status_label.config(text=msg.get('status', self.status_label.cget('text')))
                elif msg['type'] == 'complete':
                    self.progress['value'] = 100
                    self.status_label.config(text="处理成功完成！")
                    messagebox.showinfo("成功", f"APK重签名成功！\n已保存到: {msg['output_path']}")
                    return
                elif msg['type'] == 'error':
                    self.progress['value'] = 0
                    self.status_label.config(text="处理失败")
                    messagebox.showerror("错误", msg['message'])
                    return
        except queue.Empty:
            pass
        
        # 继续检查
        self.root.after(100, self.check_progress())


def main():
    """运行应用程序的主函数"""
    # 使用 TkinterDnD 创建根窗口（如果可用）
    if TkinterDnD:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = APKResignGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()