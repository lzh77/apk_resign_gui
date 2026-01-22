"""
APK重签名GUI应用程序
应用程序的主入口点
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tempfile
import zipfile
import subprocess
import shutil
from pathlib import Path
import json


class APKResignGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("APK重签名工具")
        self.root.geometry("600x400")  # 调整大小适应新布局
        
        # 配置文件路径 - 使用用户目录，不会被打包到exe中
        self.config_file = os.path.join(os.path.expanduser("~"), ".apk_resign_gui_config.json")
        
        # 从配置文件加载数据
        self.config_data = self.load_config()
        
        # 初始化变量
        self.sdk_path = tk.StringVar(value=self.config_data.get("sdk_path", ""))
        self.apk_path = tk.StringVar()
        
        # 当前选中的签名配置
        self.current_profile = tk.StringVar(value="default")
        
        # 创建控件
        self.create_widgets()
        
        # 更新签名配置下拉菜单
        self.update_profiles_list()
    
    def load_config(self):
        """从配置文件加载数据"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"profiles": {"default": {}}, "sdk_path": ""}

    def save_config(self):
        """保存配置到文件"""
        try:
            self.config_data["sdk_path"] = self.sdk_path.get()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def create_widgets(self):
        """创建并布局GUI控件"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="APK重签名工具", font=("Arial", 16, "bold"))
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
        ttk.Button(main_frame, text="浏览", command=self.browse_apk).grid(row=3, column=2, padx=(10, 0), pady=(0, 5))
        
        # 处理按钮
        ttk.Button(main_frame, text="重签名APK", command=self.resign_apk).grid(row=8, column=0, columnspan=4, pady=(20, 0))
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=9, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪", foreground="blue")
        self.status_label.grid(row=10, column=0, columnspan=4, pady=(10, 0))

    def update_profiles_list(self):
        """更新签名配置列表"""
        profiles = list(self.config_data.get("profiles", {}).keys())
        self.profiles_combo['values'] = profiles
        if self.current_profile.get() in profiles:
            self.profiles_combo.set(self.current_profile.get())
        elif profiles:
            self.current_profile.set(profiles[0])
            self.load_profile_data(profiles[0])

    def on_profile_selected(self, event=None):
        """当选择签名配置时触发"""
        pass  # 现在在执行重签名时才加载配置信息

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

    def browse_keystore(self):
        """打开文件对话框选择密钥库文件"""
        filename = filedialog.askopenfilename(
            title="选择密钥库文件",
            filetypes=[("密钥库文件", "*.jks *.keystore"), ("所有文件", "*.*")]
        )
        if filename:
            self.keystore_path.set(filename)

    def resign_apk(self):
        """处理APK重签名过程"""
        if not self.apk_path.get():
            messagebox.showerror("错误", "请选择一个APK文件")
            return
            
        # 获取当前配置
        profile_name = self.current_profile.get()
        profiles = self.config_data.get("profiles", {})
        profile = profiles.get(profile_name, {})
        
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
        tool_check_result = self.check_tools()
        if not tool_check_result[0]:
            messagebox.showerror("错误", f"缺少必要的工具: {tool_check_result[1]}，请确保已安装Android SDK并在PATH中\n\n调试信息：{tool_check_result[2]}")
            return
        
        # 开始处理
        self.status_label.config(text="正在处理...")
        self.progress.start()
        
        # 执行APK重签名
        try:
            self.perform_resign(keystore_path, storepass, key_alias)
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="处理失败")
            messagebox.showerror("错误", f"重签名过程中发生错误: {str(e)}")

    def check_tools(self):
        """检查是否有必要的工具"""
        try:
            # 初始化结果
            apksigner_available = False
            zipalign_available = False
            debug_info = []
            
            # 检查用户是否指定了SDK路径
            user_sdk_path = self.sdk_path.get() if self.sdk_path.get() else None
            if user_sdk_path:
                debug_info.append(f"用户指定SDK路径: {user_sdk_path}")
                
                # 在用户指定的路径下查找工具
                build_tools_path = Path(user_sdk_path) / 'build-tools'
                
                if build_tools_path.exists():
                    versions = [d for d in build_tools_path.iterdir() if d.is_dir()]
                    if versions:
                        # 按名称排序，获取最新版本
                        try:
                            sorted_versions = sorted(versions, key=lambda x: [
                                int(part) if part.isdigit() else part.lower() 
                                for part in x.name.replace('-rc', '.rc.').replace(' ', '.').split('.')
                            ])
                            latest_version = sorted_versions[-1]
                            
                            # 对于Windows，工具通常是.exe文件
                            zipalign_path = latest_version / 'zipalign.exe'
                            apksigner_path = latest_version / 'apksigner.exe'
                            
                            debug_info.append(f"最新版本: {latest_version.name}")
                            debug_info.append(f"Zipalign路径: {zipalign_path}, 存在: {zipalign_path.exists()}")
                            debug_info.append(f"Apsigner路径: {apksigner_path}, 存在: {apksigner_path.exists()}")
                            
                            if apksigner_path.exists():
                                self.apksigner_cmd = str(apksigner_path)
                                apksigner_available = True
                                
                            if zipalign_path.exists():
                                self.zipalign_cmd = str(zipalign_path)
                                zipalign_available = True
                        except Exception as sort_error:
                            debug_info.append(f"版本排序错误: {str(sort_error)}")
                else:
                    debug_info.append(f"用户指定路径中未找到build-tools: {build_tools_path}")
            
            # 如果用户未指定或工具未找到，尝试从环境变量获取
            if not apksigner_available or not zipalign_available:
                android_home = os.environ.get('ANDROID_HOME')
                android_sdk_root = os.environ.get('ANDROID_SDK_ROOT')
                
                debug_info.append(f"ANDROID_HOME: {android_home}")
                debug_info.append(f"ANDROID_SDK_ROOT: {android_sdk_root}")
                
                # 检查 ANDROID_HOME 或 ANDROID_SDK_ROOT
                sdk_path = android_home or android_sdk_root or user_sdk_path
                
                if sdk_path:
                    build_tools_path = Path(sdk_path) / 'build-tools'
                    
                    debug_info.append(f"Build tools路径: {build_tools_path}")
                    
                    # 查找最新的build-tools版本
                    if build_tools_path.exists():
                        versions = [d for d in build_tools_path.iterdir() if d.is_dir()]
                        if versions:
                            # 按名称排序，获取最新版本
                            try:
                                sorted_versions = sorted(versions, key=lambda x: [
                                    int(part) if part.isdigit() else part.lower() 
                                    for part in x.name.replace('-rc', '.rc.').replace(' ', '.').split('.')
                                ])
                                latest_version = sorted_versions[-1]
                                
                                zipalign_path = latest_version / 'zipalign.exe'
                                apksigner_path = latest_version / 'apksigner.exe'
                                
                                debug_info.append(f"环境变量下的最新版本: {latest_version.name}")
                                debug_info.append(f"Zipalign路径: {zipalign_path}, 存在: {zipalign_path.exists()}")
                                debug_info.append(f"Apsigner路径: {apksigner_path}, 存在: {apksigner_path.exists()}")
                                
                                if not apksigner_available and apksigner_path.exists():
                                    self.apksigner_cmd = str(apksigner_path)
                                    apksigner_available = True
                                    
                                if not zipalign_available and zipalign_path.exists():
                                    self.zipalign_cmd = str(zipalign_path)
                                    zipalign_available = True
                            except Exception as sort_error:
                                debug_info.append(f"版本排序错误: {str(sort_error)}")
                        else:
                            debug_info.append("未找到build-tools版本")
                    else:
                        debug_info.append("Build-tools路径不存在")
            
            # 如果上述方法都没找到，尝试从PATH中查找
            if not apksigner_available:
                try:
                    result_apksigner = subprocess.run(
                        ['apksigner', '--version'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,
                        check=False,
                        shell=True  # 使用shell来确保PATH被正确解析
                    )
                    apksigner_available = result_apksigner.returncode == 0
                    debug_info.append(f"PATH中apksigner: {'找到' if apksigner_available else '未找到'}")
                    if apksigner_available:
                        self.apksigner_cmd = 'apksigner'
                except Exception as e:
                    debug_info.append(f"PATH中apksigner检查异常: {str(e)}")
            
            if not zipalign_available:
                try:
                    result_zipalign = subprocess.run(
                        ['zipalign', '-h'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,
                        check=False,
                        shell=True  # 使用shell来确保PATH被正确解析
                    )
                    zipalign_available = result_zipalign.returncode == 0
                    debug_info.append(f"PATH中zipalign: {'找到' if zipalign_available else '未找到'}")
                    if zipalign_available:
                        self.zipalign_cmd = 'zipalign'
                except Exception as e:
                    debug_info.append(f"PATH中zipalign检查异常: {str(e)}")
            
            # 检查是否安装了adb，这可以表明SDK是否完整安装
            try:
                result_adb = subprocess.run(['adb', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, shell=True)
                has_adb = result_adb.returncode == 0
                debug_info.append(f"PATH中adb: {'找到' if has_adb else '未找到'}")
            except:
                debug_info.append("PATH中adb: 未找到")
            
            # 最终检查
            tools_missing = []
            if not apksigner_available:
                tools_missing.append("apksigner")
            if not zipalign_available:
                # 注意：zipalign不是绝对必需的，但我们仍会在调试信息中提及
                debug_info.append("zipalign未找到，某些情况下可能影响性能，但不是必需的")
            
            if tools_missing:
                return False, "和".join(tools_missing), "; ".join(debug_info)
            else:
                return True, "", "; ".join(debug_info)

        except Exception as e:
            return False, "未知错误", f"检查工具时出错: {str(e)}"

    def perform_resign(self, keystore_path, storepass, key_alias):
        """执行APK重签名"""
        apk_path = self.apk_path.get()
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 解压原始APK
            unsigned_apk = os.path.join(temp_dir, "unsigned.apk")
            
            # 复制原始APK到临时位置
            shutil.copy2(apk_path, unsigned_apk)
            
            # 输出路径 - 在原APK同目录下生成新的签名APK
            original_dir = os.path.dirname(apk_path)
            apk_name = os.path.splitext(os.path.basename(apk_path))[0]
            output_apk = os.path.join(original_dir, f"{apk_name}_resigned.apk")
            
            # 使用apksigner进行签名
            try:
                # 准备命令参数
                cmd = [
                    self.apksigner_cmd, 'sign',
                    '--ks', keystore_path,
                    '--ks-key-alias', key_alias,
                    '--ks-pass', f'pass:{storepass}',
                    '--out', output_apk,
                    unsigned_apk
                ]
                
                # 执行签名命令
                result = subprocess.run(cmd, check=False, capture_output=True, text=True, shell=(os.name == 'nt'))
                
                if result.returncode != 0:
                    print(f"签名错误: {result.stderr}")
                    self.progress.stop()
                    self.status_label.config(text="签名失败")
                    messagebox.showerror("错误", f"签名失败: {result.stderr}")
                    return
                
                # 检查输出文件是否存在
                if os.path.exists(output_apk):
                    self.progress.stop()
                    self.status_label.config(text="处理成功完成！")
                    messagebox.showinfo("成功", f"APK重签名成功！\n已保存到: {output_apk}")
                else:
                    self.progress.stop()
                    self.status_label.config(text="签名失败")
                    messagebox.showerror("错误", "签名后的APK文件未找到，签名可能失败了")
                    
            except Exception as e:
                self.progress.stop()
                self.status_label.config(text="签名失败")
                messagebox.showerror("错误", f"签名过程中发生异常: {str(e)}")

    def process_complete(self):
        """处理完成时调用（保留此方法以防其他用途）"""
        pass


class ManageProfilesDialog:
    def __init__(self, parent, app):
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("管理签名配置")
        self.dialog.geometry("600x450")  # 增加高度以完整显示所有控件
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示对话框
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_reqwidth() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_reqheight() // 2)
        self.dialog.geometry("+{}+{}".format(x, y))
        
        self.selected_profile = None
        self.create_widgets()
        self.load_profiles_list()
        self.highlight_current_profile()
        # 自动选择当前配置并加载其详情
        self.select_and_load_current_profile()
    
    def select_and_load_current_profile(self):
        """自动选择当前配置并加载详情"""
        current = self.app.current_profile.get()
        for i in range(self.listbox.size()):
            if self.listbox.get(i) == current:
                self.listbox.selection_set(i)
                self.listbox.activate(i)  # 激活该项
                self.selected_profile = current
                self.on_select_profile(None)  # 触发加载详情
                self.listbox.see(i)  # 确保该项可见
                break
    
    def create_widgets(self):
        """创建管理对话框的控件"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置列表
        ttk.Label(main_frame, text="签名配置列表:").pack(anchor=tk.W)
        listbox_frame = ttk.Frame(main_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        self.listbox = tk.Listbox(listbox_frame, height=8)  # 设置固定高度
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.listbox.bind('<<ListboxSelect>>', self.on_select_profile)
        
        # 编辑区域
        edit_frame = ttk.LabelFrame(main_frame, text="编辑配置", padding="10")
        edit_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 配置名称
        ttk.Label(edit_frame, text="配置名称:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(edit_frame, textvariable=self.name_var, width=50)
        name_entry.grid(row=0, column=1, padx=(10, 0), pady=(0, 5))
        
        # 密钥库路径
        ttk.Label(edit_frame, text="密钥库路径:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.keystore_var = tk.StringVar()
        keystore_entry = ttk.Entry(edit_frame, textvariable=self.keystore_var, width=50)
        keystore_entry.grid(row=1, column=1, padx=(10, 0), pady=(0, 5))
        ttk.Button(edit_frame, text="浏览", command=self.browse_keystore).grid(row=1, column=2, padx=(10, 0), pady=(0, 5))
        
        # 密钥别名
        ttk.Label(edit_frame, text="密钥别名:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.alias_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.alias_var, width=50).grid(row=2, column=1, padx=(10, 0), pady=(0, 5))
        
        # 密码
        ttk.Label(edit_frame, text="密码:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.password_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.password_var, width=50, show="*").grid(row=3, column=1, padx=(10, 0), pady=(0, 5))
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="新建", command=self.new_profile).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="删除", command=self.delete_profile).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="重命名", command=self.rename_profile).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="保存", command=self.save_profile).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="设为当前", command=self.set_current).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="关闭", command=self.close_dialog).pack(side=tk.RIGHT)
    
    def load_profiles_list(self):
        """加载配置列表"""
        self.listbox.delete(0, tk.END)
        profiles = list(self.app.config_data.get("profiles", {}).keys())
        for profile in profiles:
            self.listbox.insert(tk.END, profile)
    
    def highlight_current_profile(self):
        """高亮显示当前选中的配置"""
        current = self.app.current_profile.get()
        for i in range(self.listbox.size()):
            if self.listbox.get(i) == current:
                self.listbox.selection_set(i)
                self.listbox.see(i)  # 确保该项可见
                break
    
    def on_select_profile(self, event):
        """选择配置时加载详情"""
        # 如果是通过事件触发，更新selected_profile
        if event:
            selection = self.listbox.curselection()
            if not selection:
                return
            profile_name = self.listbox.get(selection[0])
            self.selected_profile = profile_name
        elif self.selected_profile:  # 如果是通过程序调用，直接使用selected_profile
            profile_name = self.selected_profile
        else:
            return
        
        # 更新名称字段
        self.name_var.set(profile_name)
        
        profiles = self.app.config_data.get("profiles", {})
        profile = profiles.get(profile_name, {})
        
        self.keystore_var.set(profile.get("keystore_path", ""))
        self.alias_var.set(profile.get("key_alias", ""))
        self.password_var.set(profile.get("storepass", ""))
    
    def browse_keystore(self):
        """浏览密钥库文件"""
        if not self.selected_profile:
            messagebox.showwarning("警告", "请先选择一个配置")
            return
            
        filename = filedialog.askopenfilename(
            title="选择密钥库文件",
            filetypes=[("密钥库文件", "*.jks *.keystore"), ("所有文件", "*.*")]
        )
        if filename:
            self.keystore_var.set(filename)
    
    def new_profile(self):
        """新建配置"""
        name = simpledialog.askstring("新建配置", "请输入配置名称:", parent=self.dialog)
        if name and name.strip():
            profiles = self.app.config_data.get("profiles", {})
            if name in profiles:
                messagebox.showerror("错误", f"配置 '{name}' 已存在")
                return
            
            profiles[name] = {"keystore_path": "", "storepass": "", "key_alias": ""}
            self.app.config_data["profiles"] = profiles
            self.app.save_config()
            self.load_profiles_list()
    
    def rename_profile(self):
        """重命名选中的配置"""
        if not self.selected_profile:
            messagebox.showwarning("警告", "请先选择一个配置")
            return
        
        if self.selected_profile == "default":
            messagebox.showerror("错误", "不能重命名默认配置")
            return
        
        new_name = simpledialog.askstring(
            "重命名配置", 
            f"请输入新的配置名称:", 
            initialvalue=self.selected_profile,
            parent=self.dialog
        )
        
        if new_name and new_name.strip():
            if new_name in self.app.config_data.get("profiles", {}):
                messagebox.showerror("错误", f"配置 '{new_name}' 已存在")
                return
            
            # 重命名配置
            profiles = self.app.config_data.get("profiles", {})
            profile_data = profiles.pop(self.selected_profile)
            profiles[new_name] = profile_data
            self.app.config_data["profiles"] = profiles
            
            # 如果重命名的是当前配置，更新当前配置名称
            if self.app.current_profile.get() == self.selected_profile:
                self.app.current_profile.set(new_name)
            
            self.app.save_config()
            self.selected_profile = new_name
            self.name_var.set(new_name)
            self.load_profiles_list()
            self.highlight_current_profile()
    
    def delete_profile(self):
        """删除选中的配置"""
        if not self.selected_profile:
            messagebox.showwarning("警告", "请选择要删除的配置")
            return
        
        if self.selected_profile == "default":
            messagebox.showerror("错误", "不能删除默认配置")
            return
        
        if messagebox.askyesno("确认", f"确定要删除配置 '{self.selected_profile}' 吗？"):
            profiles = self.app.config_data.get("profiles", {})
            del profiles[self.selected_profile]
            self.app.config_data["profiles"] = profiles
            self.app.save_config()
            self.selected_profile = None
            self.name_var.set("")
            self.keystore_var.set("")
            self.alias_var.set("")
            self.password_var.set("")
            self.load_profiles_list()
            
            # 如果删除的是当前配置，切换到第一个配置
            if self.selected_profile == self.app.current_profile.get() and profiles:
                first_profile = next(iter(profiles))
                self.app.current_profile.set(first_profile)
                self.app.update_profiles_list()
    
    def save_profile(self):
        """保存当前编辑的配置"""
        if not self.selected_profile:
            messagebox.showwarning("警告", "请先选择一个配置")
            return
        
        # 如果配置名称被修改了，需要重命名配置
        if self.name_var.get() != self.selected_profile:
            self.rename_profile_by_value()
            return
        
        profiles = self.app.config_data.get("profiles", {})
        profile = profiles.get(self.selected_profile, {})
        
        profile["keystore_path"] = self.keystore_var.get()
        profile["key_alias"] = self.alias_var.get()
        profile["storepass"] = self.password_var.get()
        
        profiles[self.selected_profile] = profile
        self.app.config_data["profiles"] = profiles
        self.app.save_config()
        self.load_profiles_list()  # 刷新列表
        self.highlight_current_profile()  # 重新高亮当前配置
        messagebox.showinfo("提示", f"配置 '{self.selected_profile}' 已保存")
    
    def rename_profile_by_value(self):
        """通过值重命名配置（内部使用）"""
        old_name = self.selected_profile
        new_name = self.name_var.get()
        
        if not new_name or new_name.strip() == "":
            messagebox.showerror("错误", "配置名称不能为空")
            return
        
        if new_name in self.app.config_data.get("profiles", {}):
            messagebox.showerror("错误", f"配置 '{new_name}' 已存在")
            return
        
        # 重命名配置
        profiles = self.app.config_data.get("profiles", {})
        profile_data = profiles.pop(old_name)
        profiles[new_name] = profile_data
        self.app.config_data["profiles"] = profiles
        
        # 如果重命名的是当前配置，更新当前配置名称
        if self.app.current_profile.get() == old_name:
            self.app.current_profile.set(new_name)
        
        self.app.save_config()
        self.selected_profile = new_name
        self.load_profiles_list()
        self.highlight_current_profile()
    
    def set_current(self):
        """将选中的配置设为当前配置"""
        if not self.selected_profile:
            messagebox.showwarning("警告", "请选择一个配置")
            return
        
        self.app.current_profile.set(self.selected_profile)
        self.app.update_profiles_list()
        self.highlight_current_profile()
    
    def close_dialog(self):
        """关闭对话框"""
        self.dialog.destroy()


def main():
    """运行应用程序的主函数"""
    root = tk.Tk()
    app = APKResignGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()