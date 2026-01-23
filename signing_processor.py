"""
签名处理器模块
负责处理APK签名相关的操作
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import queue


class SigningProcessor:
    def __init__(self, sdk_path):
        """
        初始化签名处理器
        :param sdk_path: Android SDK路径
        """
        self.sdk_path = sdk_path
        self.apksigner_cmd = None
        self.zipalign_cmd = None
        self.progress_queue = queue.Queue()
        
    def check_tools(self):
        """检查是否有必要的工具"""
        try:
            # 初始化结果
            apksigner_available = False
            zipalign_available = False
            debug_info = []

            # 检查用户是否指定了SDK路径
            user_sdk_path = self.sdk_path if self.sdk_path else None
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

    def perform_resign(self, apk_path, keystore_path, storepass, key_alias, progress_queue):
        """执行APK重签名"""
        # 发送初始进度
        progress_queue.put({'type': 'progress', 'value': 10, 'status': '准备重签名...'})

        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 复制原始APK到临时位置
            unsigned_apk = os.path.join(temp_dir, "unsigned.apk")
            shutil.copy2(apk_path, unsigned_apk)

            # 发送进度更新
            progress_queue.put({'type': 'progress', 'value': 20, 'status': '准备签名文件...'})

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

                # 发送进度更新
                progress_queue.put({'type': 'progress', 'value': 30, 'status': '开始签名过程...'})

                # 执行签名命令
                result = subprocess.run(cmd, check=False, capture_output=True, text=True, shell=(os.name == 'nt'))

                if result.returncode != 0:
                    progress_queue.put({
                        'type': 'error',
                        'message': f"签名失败: {result.stderr}"
                    })
                    return

                # 检查输出文件是否存在
                if os.path.exists(output_apk):
                    # 发送完成前的进度更新
                    progress_queue.put({'type': 'progress', 'value': 90, 'status': '完成...'})
                    # 稍微延迟以显示完成状态
                    import time
                    time.sleep(0.2)
                    progress_queue.put({
                        'type': 'complete',
                        'output_path': output_apk
                    })
                else:
                    progress_queue.put({
                        'type': 'error',
                        'message': "签名后的APK文件未找到，签名可能失败了"
                    })

            except Exception as e:
                progress_queue.put({
                    'type': 'error',
                    'message': f"签名过程中发生异常: {str(e)}"
                })