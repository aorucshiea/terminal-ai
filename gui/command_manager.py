"""
命令管理界面 - 管理用户信任的命令
基于 Soft UI Evolution 风格
"""

import sys
import os

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
        QListWidget, QListWidgetItem, QLineEdit, QMessageBox,
        QFrame, QScrollArea, QInputDialog
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont, QColor
except ImportError:
    print("错误: 需要安装 PyQt5")
    print("运行: pip install PyQt5")
    sys.exit(1)

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from command_config import command_config

# SaaS 配色方案
COLORS = {
    'primary': '#2563EB',
    'primary_hover': '#1D4ED8',
    'primary_light': '#DBEAFE',
    'secondary': '#3B82F6',
    'background': '#F8FAFC',
    'surface': '#FFFFFF',
    'text': '#1E293B',
    'text_muted': '#64748B',
    'border': '#E2E8F0',
    'border_hover': '#CBD5E1',
    'danger': '#EF4444',
    'danger_hover': '#DC2626',
    'danger_light': '#FEE2E2',
}


class CommandManager(QWidget):
    """命令管理界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_commands()

    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # 标题
        title_label = QLabel("命令管理")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 24px;
                font-weight: 700;
            }}
        """)
        layout.addWidget(title_label)

        # 描述
        desc_label = QLabel("管理您信任的命令白名单。只有信任的命令才会被执行并传递给 AI。")
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_muted']};
                font-size: 14px;
            }}
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # 添加命令区域
        add_frame = QFrame()
        add_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        add_layout = QHBoxLayout(add_frame)
        add_layout.setContentsMargins(20, 16, 20, 16)

        add_label = QLabel("添加命令:")
        add_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 14px;
                font-weight: 500;
            }}
        """)
        add_layout.addWidget(add_label)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("输入命令名称（如: git, npm, docker）")
        self.command_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: {COLORS['text']};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QLineEdit:hover {{
                border-color: {COLORS['border_hover']};
            }}
        """)
        self.command_input.returnPressed.connect(self.add_command)
        add_layout.addWidget(self.command_input)

        add_btn = QPushButton("添加")
        add_btn.setFixedSize(80, 40)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['surface']};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
        """)
        add_btn.clicked.connect(self.add_command)
        add_layout.addWidget(add_btn)

        layout.addWidget(add_frame)

        # 命令列表
        list_frame = QFrame()
        list_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)

        # 列表标题
        list_header = QLabel("信任的命令列表")
        list_header.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 16px;
                font-weight: 600;
                padding: 20px 24px 12px 24px;
            }}
        """)
        list_layout.addWidget(list_header)

        # 命令列表
        self.command_list = QListWidget()
        self.command_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['surface']};
                border: none;
                font-size: 14px;
                color: {COLORS['text']};
            }}
            QListWidget::item {{
                padding: 12px 24px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['background']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
            }}
        """)
        list_layout.addWidget(self.command_list)

        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 16, 20, 20)

        remove_btn = QPushButton("移除选中")
        remove_btn.setFixedSize(120, 40)
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: {COLORS['surface']};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger_hover']};
            }}
        """)
        remove_btn.clicked.connect(self.remove_command)
        button_layout.addWidget(remove_btn)

        button_layout.addStretch()

        clear_btn = QPushButton("清空所有")
        clear_btn.setFixedSize(120, 40)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['background']};
                color: {COLORS['text_muted']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
                color: {COLORS['text']};
            }}
        """)
        clear_btn.clicked.connect(self.clear_commands)
        button_layout.addWidget(clear_btn)

        list_layout.addLayout(button_layout)
        layout.addWidget(list_frame)

        # 历史记录
        history_frame = QFrame()
        history_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        history_layout = QVBoxLayout(history_frame)
        history_layout.setContentsMargins(0, 0, 0, 0)

        history_header = QLabel("添加历史")
        history_header.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 16px;
                font-weight: 600;
                padding: 20px 24px 12px 24px;
            }}
        """)
        history_layout.addWidget(history_header)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['surface']};
                border: none;
                font-size: 13px;
                color: {COLORS['text_muted']};
            }}
            QListWidget::item {{
                padding: 10px 24px;
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        history_layout.addWidget(self.history_list)

        layout.addWidget(history_frame)

        layout.addStretch()

    def load_commands(self):
        """加载命令列表"""
        self.command_list.clear()
        commands = command_config.get_trusted_commands()
        for cmd in commands:
            item = QListWidgetItem(cmd)
            self.command_list.addItem(item)

        # 加载历史记录
        self.history_list.clear()
        history = command_config.get_command_history()
        for entry in reversed(history[-20:]):  # 只显示最近 20 条
            cmd = entry.get("command", "")
            reason = entry.get("reason", "")
            added_at = entry.get("added_at", "")
            text = f"{cmd} - {reason} ({added_at[:10]})"
            item = QListWidgetItem(text)
            self.history_list.addItem(item)

    def add_command(self):
        """添加命令"""
        command = self.command_input.text().strip()
        if not command:
            QMessageBox.warning(self, "警告", "请输入命令名称")
            return

        # 检查命令是否已存在
        if command in command_config.get_trusted_commands():
            QMessageBox.information(self, "提示", "该命令已在信任列表中")
            return

        # 添加命令
        command_config.add_trusted_command(command, "GUI 手动添加")
        self.command_input.clear()
        self.load_commands()
        QMessageBox.information(self, "成功", f"已添加命令: {command}")

    def remove_command(self):
        """移除选中的命令"""
        current_item = self.command_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要移除的命令")
            return

        command = current_item.text()
        reply = QMessageBox.question(
            self,
            "确认",
            f"确定要移除命令 '{command}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            command_config.remove_trusted_command(command)
            self.load_commands()
            QMessageBox.information(self, "成功", f"已移除命令: {command}")

    def clear_commands(self):
        """清空所有命令"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空所有信任的命令吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            command_config.clear_trusted_commands()
            self.load_commands()
            QMessageBox.information(self, "成功", "已清空所有信任的命令")
