#!/usr/bin/env python3
"""
Terminal AI GUI 启动脚本
"""
import sys
import os

# 确保项目根目录在 sys.path 中
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入并运行主程序
from gui.main import main

if __name__ == "__main__":
    main()
