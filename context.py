"""
上下文收集模块
收集终端相关的上下文信息
"""

import os
import sys
import subprocess
from typing import Optional


class ContextCollector:
    """上下文收集器"""

    def __init__(self, include_history: bool = False):
        self.include_history = include_history
        self.piped_input: Optional[str] = None

    def collect(self) -> str:
        """
        收集所有上下文信息

        Returns:
            格式化的上下文字符串
        """
        context_parts = []

        # 当前工作目录
        context_parts.append(f"## 当前工作目录\n{os.getcwd()}\n")

        # 当前目录文件列表
        context_parts.append(self._get_file_list())

        # Shell 历史命令（可选）
        if self.include_history:
            context_parts.append(self._get_shell_history())

        # 管道输入
        if self.piped_input:
            context_parts.append(f"## 管道输入\n```\n{self.piped_input}\n```\n")

        return "\n".join(context_parts)

    def _get_file_list(self) -> str:
        """获取当前目录文件列表"""
        try:
            files = sorted(os.listdir("."))
            return f"## 当前目录文件\n{', '.join(files)}\n"
        except Exception:
            return "## 当前目录文件\n(无法读取)\n"

    def _get_shell_history(self) -> str:
        """获取最近的 shell 历史命令"""
        # 优先直接读取历史文件，避免 subprocess 启动新 bash 实例的缓冲问题
        return self._get_history_from_file()

    def _get_history_from_file(self) -> str:
        """从历史文件读取命令"""
        history_file = None
        shell = os.getenv("SHELL", "")

        if "zsh" in shell:
            history_file = os.path.expanduser("~/.zsh_history")
        elif "bash" in shell:
            history_file = os.path.expanduser("~/.bash_history")

        if not history_file or not os.path.exists(history_file):
            return "## Shell 历史\n(无历史记录)\n"

        try:
            with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                # 过滤掉时间戳行（以 # 开头的行）和空行
                commands = []
                for line in reversed(lines):
                    stripped = line.strip()
                    # 跳过空行和时间戳行
                    if not stripped or stripped.startswith('#'):
                        continue
                    # 跳过 ai 命令本身（避免循环）
                    if stripped.startswith('ai ') or stripped == 'ai':
                        continue
                    commands.append(stripped)
                    # 只获取最近 10 条命令
                    if len(commands) >= 10:
                        break

                if commands:
                    # 反转回正确顺序
                    commands.reverse()
                    return "## 最近 Shell 命令\n" + "\n".join(commands) + "\n\n注意：如果命令不存在或拼写错误，shell 会显示 '未找到命令' 错误。\n"
                else:
                    return "## Shell 历史\n(无有效命令)\n"
        except Exception:
            return "## Shell 历史\n(无法读取)\n"

    def set_piped_input(self, input_data: str):
        """设置管道输入数据"""
        self.piped_input = input_data

    def has_piped_input(self) -> bool:
        """检查是否有管道输入"""
        return self.piped_input is not None
