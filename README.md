# APK重签名GUI工具

这是一个用于在Windows上重新签名APK文件的简单图形用户界面应用程序。此工具允许用户轻松地使用自定义证书对Android APK文件进行重新签名，而无需使用命令行工具。

## 功能特性

- 简单的图形用户界面，便于APK重签名
- 支持自定义密钥库和密码
- 简单的文件选择对话框
- 处理过程中显示进度指示

## 前置要求

- Python 3.7 或更高版本
- Windows 操作系统（专为Windows设计）
- 安装Java开发工具包（JDK）以支持签名功能

## 安装

1. 克隆或下载此仓库
2. 使用pip安装依赖项：
   ```
   pip install -r requirements.txt
   ```

## 构建可执行文件

要构建独立的可执行文件：

1. 运行构建脚本：
   ```
   python build.py
   ```

2. 可执行文件将在 `dist/apk_resign_gui` 文件夹中创建

或者，您也可以运行：
```
pyinstaller apk_resign_gui.spec
```

## 使用方法

1. 运行应用程序：
   ```
   python main.py
   ```
   
   或者直接运行生成的可执行文件。

2. 选择未签名的APK文件
3. 选择您的密钥库文件
4. 输入密钥库密码
5. 输入密钥别名
6. 单击"重签名APK"来处理文件

## 项目结构

- `main.py`: 包含GUI和逻辑的主应用程序代码
- `requirements.txt`: Python依赖项
- `apk_resign_gui.spec`: 用于构建可执行文件的PyInstaller规范文件
- `build.py`: 构建自动化脚本
- `README.md`: 此文件

## 许可证

MIT许可证 - 欢迎自由修改和分发