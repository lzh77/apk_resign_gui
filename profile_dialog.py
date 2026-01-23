"""
签名配置管理对话框模块
负责处理签名配置的管理界面
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog


class ManageProfilesDialog:
    def __init__(self, parent, app):
        self.app = app
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("管理签名配置")
        self.dialog.geometry("600x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 设置对话框图标
        self.set_dialog_icon()
        
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
    
    def set_dialog_icon(self):
        """设置对话框图标"""
        icon_path = "icon.ico"  # 默认图标文件名
        if os.path.exists(icon_path):
            try:
                self.dialog.iconbitmap(icon_path)
            except Exception as e:
                print(f"加载对话框图标失败: {e}")
        else:
            print(f"图标文件不存在: {icon_path}")
    
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
        # 启用密钥库文件拖拽功能
        if hasattr(self.dialog, 'dnd_bind'):
            keystore_entry.drop_target_register('DND_FILES')
            keystore_entry.dnd_bind('<<Drop>>', self.on_keystore_drop)
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
        profiles = list(self.app.config_manager.get_all_profiles().keys())
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
        
        profile = self.app.config_manager.get_profile(profile_name)
        
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

    def on_keystore_drop(self, event):
        """处理密钥库文件拖拽事件"""
        # 获取拖拽的文件路径
        dropped_file = self.dialog.tk.splitlist(event.data)[0]  # 只取第一个文件
        # 检查文件扩展名
        if dropped_file.lower().endswith(('.jks', '.keystore')):
            self.keystore_var.set(dropped_file)
        else:
            messagebox.showerror("错误", "请选择有效的密钥库文件(.jks 或 .keystore)")
    
    def new_profile(self):
        """新建配置"""
        name = simpledialog.askstring("新建配置", "请输入配置名称:", parent=self.dialog)
        if name and name.strip():
            profiles = self.app.config_manager.get_all_profiles()
            if name in profiles:
                messagebox.showerror("错误", f"配置 '{name}' 已存在")
                return
            
            self.app.config_manager.add_profile(name, {"keystore_path": "", "storepass": "", "key_alias": ""})
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
            profiles = self.app.config_manager.get_all_profiles()
            if new_name in profiles:
                messagebox.showerror("错误", f"配置 '{new_name}' 已存在")
                return
            
            # 重命名配置
            profile_data = profiles.pop(self.selected_profile)
            profiles[new_name] = profile_data
            self.app.config_manager.update_profile(new_name, profile_data)
            
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
            self.app.config_manager.delete_profile(self.selected_profile)
            self.app.save_config()
            self.selected_profile = None
            self.name_var.set("")
            self.keystore_var.set("")
            self.alias_var.set("")
            self.password_var.set("")
            self.load_profiles_list()
            
            # 如果删除的是当前配置，切换到第一个配置
            profiles = self.app.config_manager.get_all_profiles()
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
        
        profile_data = {
            "keystore_path": self.keystore_var.get(),
            "key_alias": self.alias_var.get(),
            "storepass": self.password_var.get()
        }
        
        self.app.config_manager.update_profile(self.selected_profile, profile_data)
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
        
        profiles = self.app.config_manager.get_all_profiles()
        if new_name in profiles:
            messagebox.showerror("错误", f"配置 '{new_name}' 已存在")
            return
        
        # 重命名配置
        profile_data = profiles.pop(old_name)
        profiles[new_name] = profile_data
        self.app.config_manager.update_profile(new_name, profile_data)
        
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