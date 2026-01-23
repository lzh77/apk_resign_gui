"""
配置管理器模块
负责处理应用程序的配置文件读写和管理
"""

import os
import json


class ConfigManager:
    def __init__(self, config_file_path):
        """
        初始化配置管理器
        :param config_file_path: 配置文件路径
        """
        self.config_file = os.path.join(os.path.expanduser(config_file_path))
        self.config_data = self.load_config()

    def load_config(self):
        """从配置文件加载数据"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"profiles": {"default": {}}, "sdk_path": ""}

    def save_config(self, sdk_path=""):
        """保存配置到文件"""
        try:
            self.config_data["sdk_path"] = sdk_path
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get_all_profiles(self):
        """获取所有配置"""
        return self.config_data.get("profiles", {})

    def add_profile(self, name, profile_data):
        """添加配置"""
        profiles = self.config_data.get("profiles", {})
        profiles[name] = profile_data
        self.config_data["profiles"] = profiles

    def update_profile(self, name, profile_data):
        """更新配置"""
        profiles = self.config_data.get("profiles", {})
        profiles[name] = profile_data
        self.config_data["profiles"] = profiles

    def delete_profile(self, name):
        """删除配置"""
        profiles = self.config_data.get("profiles", {})
        if name in profiles:
            del profiles[name]
            self.config_data["profiles"] = profiles

    def get_profile(self, name):
        """获取指定配置"""
        profiles = self.config_data.get("profiles", {})
        return profiles.get(name, {})

    def get_sdk_path(self):
        """获取SDK路径"""
        return self.config_data.get("sdk_path", "")