"""
API 测试界面 - Glassmorphism + Dark Mode 设计
"""

import json
import os
from datetime import datetime
from typing import Optional

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
        QTextEdit, QPushButton, QComboBox, QMessageBox, QGroupBox
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QTextCursor
except ImportError:
    print("错误: 需要安装 PyQt5")
    print("运行: pip install PyQt5")
    raise

# Glassmorphism Dark Mode 配色方案
COLORS = {
    'bg_primary': '#0F172A',
    'bg_secondary': '#1E293B',
    'bg_card': 'rgba(30, 41, 59, 0.8)',
    'bg_hover': 'rgba(51, 65, 85, 0.9)',
    'bg_input': '#1E293B',
    'text_primary': '#F8FAFC',
    'text_secondary': '#94A3B8',
    'text_muted': '#64748B',
    'primary': '#F59E0B',
    'primary_hover': '#D97706',
    'primary_light': 'rgba(245, 158, 11, 0.15)',
    'accent': '#8B5CF6',
    'accent_hover': '#7C3AED',
    'accent_light': 'rgba(139, 92, 246, 0.15)',
    'success': '#10B981',
    'danger': '#EF4444',
    'warning': '#F59E0B',
    'border': 'rgba(51, 65, 85, 0.6)',
    'border_light': 'rgba(148, 163, 184, 0.3)',
    'border_focus': '#F59E0B',
}


class APIStreamThread(QThread):
    """API 流式输出线程"""

    chunk_received = pyqtSignal(str)
    usage_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, config: dict, message: str):
        super().__init__()
        self.config = config
        self.message = message
        self._full_response = ""

    def run(self):
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.config["api_key"],
                base_url=self.config["endpoint"]
            )
            response = client.chat.completions.create(
                model=self.config["model"],
                messages=[{"role": "user", "content": self.message}],
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
                stream=True  # 启用流式输出
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    self._full_response += content
                    self.chunk_received.emit(content)
                # 检查是否有 usage 信息（通常在最后一个 chunk 中）
                if hasattr(chunk, 'usage') and chunk.usage:
                    self.usage_received.emit({
                        "prompt_tokens": chunk.usage.prompt_tokens,
                        "completion_tokens": chunk.usage.completion_tokens,
                        "total_tokens": chunk.usage.total_tokens
                    })
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()


class APITester(QWidget):
    """API 测试界面"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.current_thread: Optional[APIStreamThread] = None
        self.history_file = os.path.join(os.path.dirname(__file__), "data", "history.json")
        self.stats_file = os.path.join(os.path.dirname(__file__), "data", "stats.json")
        self.current_usage: Optional[dict] = None
        self._full_response = ""
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 配置选择
        config_group = QGroupBox("选择配置")
        config_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
        """)
        config_layout = QHBoxLayout()
        config_layout.setContentsMargins(16, 8, 16, 16)

        config_label = QLabel("配置:")
        config_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 500;")
        config_layout.addWidget(config_label)

        self.config_combo = QComboBox()
        self.config_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 30px 10px 14px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QComboBox:focus {{
                border: 2px solid {COLORS['border_focus']};
            }}
            QComboBox:hover {{
                border-color: {COLORS['border_light']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
                padding-right: 8px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['text_secondary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                selection-background-color: {COLORS['primary_light']};
                selection-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                padding: 4px;
            }}
        """)
        self.config_combo.currentIndexChanged.connect(self.on_config_changed)
        config_layout.addWidget(self.config_combo)
        config_layout.addStretch()
        config_group.setLayout(config_layout)

        # 输入区域
        input_group = QGroupBox("输入消息")
        input_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
        """)
        input_layout = QVBoxLayout()
        input_layout.setContentsMargins(16, 8, 16, 16)
        input_layout.setSpacing(12)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("输入要发送给 AI 的消息...")
        self.message_input.setMaximumHeight(120)
        self.message_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 14px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QTextEdit:focus {{
                border: 2px solid {COLORS['border_focus']};
            }}
            QTextEdit:hover {{
                border-color: {COLORS['border_light']};
            }}
        """)
        input_layout.addWidget(self.message_input)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.send_btn = QPushButton("发送")
        self.send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['text_muted']};
            }}
        """)
        self.send_btn.clicked.connect(self.send_message)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        self.clear_btn.clicked.connect(self.clear_all)

        btn_layout.addStretch()
        btn_layout.addWidget(self.send_btn)
        btn_layout.addWidget(self.clear_btn)
        input_layout.addLayout(btn_layout)

        input_group.setLayout(input_layout)

        # 输出区域
        output_group = QGroupBox("AI 响应")
        output_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: {COLORS['text_primary']};
                font-size: 14px;
            }}
        """)
        output_layout = QVBoxLayout()
        output_layout.setContentsMargins(16, 8, 16, 16)

        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)
        self.response_output.setPlaceholderText("AI 响应将显示在这里...")
        self.response_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 14px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
        """)
        output_layout.addWidget(self.response_output)
        output_group.setLayout(output_layout)

        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")

        layout.addWidget(config_group)
        layout.addWidget(input_group)
        layout.addWidget(output_group)
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.refresh_configs()

    def refresh_configs(self):
        """刷新配置列表"""
        self.config_combo.clear()
        configs = self.config_manager.get_all_configs()
        for config in configs:
            self.config_combo.addItem(config["name"], config)

        # 选择默认配置
        default_config = self.config_manager.get_default_config()
        if default_config:
            for i in range(self.config_combo.count()):
                if self.config_combo.itemText(i) == default_config["name"]:
                    self.config_combo.setCurrentIndex(i)
                    break

    def on_config_changed(self, index: int):
        """配置改变时更新"""
        pass

    def send_message(self):
        """发送消息"""
        if self.current_thread and self.current_thread.isRunning():
            QMessageBox.warning(self, "提示", "请等待当前请求完成")
            return

        message = self.message_input.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "提示", "请输入消息")
            return

        config_data = self.config_combo.currentData()
        if not config_data:
            QMessageBox.warning(self, "提示", "请先添加配置")
            return

        self.send_btn.setEnabled(False)
        self.status_label.setText("发送中...")
        self.response_output.clear()
        self._full_response = ""
        self.current_usage = None

        self.current_thread = APIStreamThread(config_data, message)
        self.current_thread.chunk_received.connect(self.on_chunk)
        self.current_thread.usage_received.connect(self.on_usage)
        self.current_thread.error_occurred.connect(self.on_error)
        self.current_thread.finished.connect(self.on_finished)
        self.current_thread.start()

    def on_chunk(self, chunk: str):
        """收到流式数据块"""
        self.response_output.insertPlainText(chunk)
        # 自动滚动到底部
        cursor = self.response_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.response_output.setTextCursor(cursor)

    def on_usage(self, usage: dict):
        """收到 usage 信息"""
        self.current_usage = usage
        # 显示 token 使用情况
        self.status_label.setText(
            f"完成 - Tokens: {usage['prompt_tokens']} + {usage['completion_tokens']} = {usage['total_tokens']}"
        )

    def on_error(self, error: str):
        """发生错误"""
        self.response_output.append(f"\n[错误] {error}")

    def on_finished(self):
        """请求完成"""
        self.send_btn.setEnabled(True)
        if not self.current_usage:
            self.status_label.setText("完成")
        # 保存到历史记录
        if self._full_response:
            self.save_to_history(self._full_response)
            # 更新统计（如果收到 usage 信息则使用实际值，否则使用估算值）
            if self.current_usage:
                self.update_stats(self.current_usage)
            else:
                # 简单估算：大约每 4 个字符 = 1 个 token
                estimated_tokens = len(self._full_response) // 4
                self.update_stats({
                    "prompt_tokens": len(self.message_input.toPlainText()) // 4,
                    "completion_tokens": estimated_tokens,
                    "total_tokens": len(self.message_input.toPlainText()) // 4 + estimated_tokens
                })

    def clear_all(self):
        """清空所有内容"""
        self.message_input.clear()
        self.response_output.clear()
        self.status_label.setText("就绪")
        self._full_response = ""
        self.current_usage = None

    def save_to_history(self, response: str):
        """保存到历史记录"""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"history": []}

        config_name = self.config_combo.currentText()
        message = self.message_input.toPlainText()

        record = {
            "timestamp": datetime.now().isoformat(),
            "config_name": config_name,
            "message": message,
            "response": response
        }

        data["history"].insert(0, record)
        # 只保留最近 100 条
        if len(data["history"]) > 100:
            data["history"] = data["history"][:100]

        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def update_stats(self, usage: dict):
        """更新统计"""
        try:
            with open(self.stats_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"total_calls": 0, "total_tokens": 0, "config_stats": {}}

        config_name = self.config_combo.currentText()

        data["total_calls"] += 1
        data["total_tokens"] += usage["total_tokens"]

        if config_name not in data["config_stats"]:
            data["config_stats"][config_name] = {"calls": 0, "tokens": 0}
        data["config_stats"][config_name]["calls"] += 1
        data["config_stats"][config_name]["tokens"] += usage["total_tokens"]

        with open(self.stats_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
