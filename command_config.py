"""
命令配置管理模块
管理用户信任的命令白名单
"""

import os
import json
from typing import Set, List, Dict
from datetime import datetime


class CommandConfig:
    """命令配置管理类"""

    def __init__(self, config_file: str = None):
        if config_file is None:
            config_file = os.path.join(
                os.path.dirname(__file__),
                ".trusted_commands.json"
            )
        self.config_file = config_file
        self.trusted_commands: Set[str] = set()
        self.command_history: List[Dict] = []
        self.load()

    def load(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.trusted_commands = set(data.get("trusted_commands", []))
                    self.command_history = data.get("command_history", [])
            except (json.JSONDecodeError, IOError):
                self.trusted_commands = set()
                self.command_history = []

    def save(self):
        """保存配置"""
        data = {
            "trusted_commands": sorted(list(self.trusted_commands)),
            "command_history": self.command_history,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def is_trusted(self, command: str) -> bool:
        """检查命令是否被信任"""
        # 获取命令的第一个词
        parts = command.strip().split()
        if not parts:
            return False
        cmd = parts[0]
        return cmd in self.trusted_commands

    def add_trusted_command(self, command: str, reason: str = ""):
        """添加信任命令"""
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0]
        if cmd not in self.trusted_commands:
            self.trusted_commands.add(cmd)

            # 添加到历史记录
            self.command_history.append({
                "command": cmd,
                "full_command": command,
                "reason": reason,
                "added_at": datetime.now().isoformat()
            })

            # 限制历史记录数量
            if len(self.command_history) > 100:
                self.command_history = self.command_history[-100:]

            self.save()

    def remove_trusted_command(self, command: str):
        """移除信任命令"""
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0]
        if cmd in self.trusted_commands:
            self.trusted_commands.remove(cmd)
            self.save()

    def get_trusted_commands(self) -> List[str]:
        """获取所有信任的命令"""
        return sorted(list(self.trusted_commands))

    def get_command_history(self) -> List[Dict]:
        """获取命令历史"""
        return self.command_history

    def clear_trusted_commands(self):
        """清空所有信任的命令"""
        self.trusted_commands.clear()
        self.save()


# 全局配置实例
command_config = CommandConfig()
