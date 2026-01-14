"""
历史记录界面 - Glassmorphism + Dark Mode (OLED) 设计
"""

import json
import os
from datetime import datetime
from typing import List, Dict

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
        QTextEdit, QPushButton, QComboBox, QMessageBox, QGroupBox,
        QLineEdit, QListWidgetItem
    )
    from PyQt5.QtCore import Qt
except ImportError:
    print("错误: 需要安装 PyQt5")
    print("运行: pip install PyQt5")
    raise

# Glassmorphism Dark Mode (OLED) 配色方案
COLORS = {
    'bg_primary': '#020617',
    'bg_secondary': '#0F172A',
    'bg_card': 'rgba(15, 23, 42, 0.8)',
    'bg_card_hover': 'rgba(30, 41, 59, 0.9)',
    'bg_input': '#1E293B',
    'bg_nav': 'rgba(2, 6, 23, 0.95)',
    'text_primary': '#F9FAFB',
    'text_secondary': '#CBD5E1',
    'text_muted': '#64748B',
    'primary': '#0EA5E9',
    'primary_hover': '#0284C7',
    'primary_light': 'rgba(14, 165, 233, 0.15)',
    'success': '#22C55E',
    'success_light': 'rgba(34, 197, 94, 0.15)',
    'warning': '#FBBF24',
    'warning_light': 'rgba(251, 191, 36, 0.15)',
    'danger': '#FCA5A5',
    'danger_light': 'rgba(252, 165, 165, 0.15)',
    'border': 'rgba(51, 65, 85, 0.5)',
    'border_light': 'rgba(148, 163, 184, 0.2)',
    'border_focus': '#0EA5E9',
    'shadow': 'rgba(0, 0, 0, 0.3)',
}


class HistoryWidget(QWidget):
    """历史记录界面 - 现代极简设计"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history: List[Dict] = []
        self.filtered_history: List[Dict] = []
        self.history_file = os.path.join(os.path.dirname(__file__), "data", "history.json")
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # 左侧历史列表
        left_panel = QVBoxLayout()
        left_panel.setSpacing(16)

        # 标题
        title = QLabel("历史记录")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: 600;
            }}
        """)
        left_panel.addWidget(title)

        # 筛选栏
        filter_group = QGroupBox("筛选")
        filter_group.setStyleSheet(f"""
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
        filter_layout = QVBoxLayout()
        filter_layout.setContentsMargins(16, 8, 16, 16)
        filter_layout.setSpacing(12)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        filter_label = QLabel("配置:")
        filter_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 500;")
        row1.addWidget(filter_label)

        self.config_filter = QComboBox()
        self.config_filter.setStyleSheet(f"""
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
        self.config_filter.addItem("全部配置")
        self.config_filter.currentIndexChanged.connect(self.apply_filter)
        row1.addWidget(self.config_filter)
        filter_layout.addLayout(row1)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索消息或响应...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['border_focus']};
            }}
            QLineEdit:hover {{
                border-color: {COLORS['border_light']};
            }}
        """)
        self.search_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.search_input)

        filter_group.setLayout(filter_layout)
        left_panel.addWidget(filter_group)

        # 历史列表
        self.history_list = QListWidget()
        self.history_list.currentRowChanged.connect(self.show_detail)
        self.history_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                font-size: 14px;
                color: {COLORS['text_primary']};
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px 16px;
                border-bottom: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['bg_card_hover']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
            }}
        """)
        left_panel.addWidget(self.history_list)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        refresh_btn = QPushButton("刷新")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_card_hover']};
            }}
        """)
        refresh_btn.clicked.connect(self.load_history)

        clear_btn = QPushButton("清空历史")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['danger']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
                color: {COLORS['text_primary']};
                border-color: {COLORS['danger']};
            }}
        """)
        clear_btn.clicked.connect(self.clear_history)

        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(clear_btn)
        left_panel.addLayout(btn_layout)

        # 右侧详情
        right_panel = QGroupBox("记录详情")
        right_panel.setStyleSheet(f"""
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
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(16, 8, 16, 16)
        right_layout.setSpacing(16)

        self.detail_time = QLabel("时间: -")
        self.detail_time.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px;")
        self.detail_config = QLabel("配置: -")
        self.detail_config.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px;")
        right_layout.addWidget(self.detail_time)
        right_layout.addWidget(self.detail_config)

        msg_label = QLabel("消息:")
        msg_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 500;")
        right_layout.addWidget(msg_label)

        self.detail_message = QTextEdit()
        self.detail_message.setReadOnly(True)
        self.detail_message.setMaximumHeight(150)
        self.detail_message.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 14px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
        """)
        right_layout.addWidget(self.detail_message)

        resp_label = QLabel("响应:")
        resp_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 500;")
        right_layout.addWidget(resp_label)

        self.detail_response = QTextEdit()
        self.detail_response.setReadOnly(True)
        self.detail_response.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 14px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
        """)
        right_layout.addWidget(self.detail_response)

        right_panel.setLayout(right_layout)

        layout.addLayout(left_panel, 1)
        layout.addWidget(right_panel, 2)

        self.setLayout(layout)

    def load_history(self):
        """加载历史记录"""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.history = data.get("history", [])
        except FileNotFoundError:
            self.history = []

        # 更新配置筛选器
        configs = set()
        for record in self.history:
            configs.add(record.get("config_name", "未知"))

        current_filter = self.config_filter.currentText()
        self.config_filter.clear()
        self.config_filter.addItem("全部配置")
        for config in sorted(configs):
            self.config_filter.addItem(config)

        # 恢复之前的筛选
        index = self.config_filter.findText(current_filter)
        if index >= 0:
            self.config_filter.setCurrentIndex(index)

        self.apply_filter()

    def apply_filter(self):
        """应用筛选"""
        config_filter = self.config_filter.currentText()
        search_text = self.search_input.text().lower()

        self.filtered_history = []
        for record in self.history:
            # 配置筛选
            if config_filter != "全部配置" and record.get("config_name") != config_filter:
                continue

            # 搜索筛选
            if search_text:
                message = record.get("message", "").lower()
                response = record.get("response", "").lower()
                if search_text not in message and search_text not in response:
                    continue

            self.filtered_history.append(record)

        self.refresh_list()

    def refresh_list(self):
        """刷新列表"""
        self.history_list.clear()
        for record in self.filtered_history:
            timestamp = record.get("timestamp", "")
            config_name = record.get("config_name", "未知")
            message = record.get("message", "")[:50]

            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = timestamp

            item_text = f"[{time_str}] {config_name}: {message}..."
            self.history_list.addItem(item_text)

    def show_detail(self, row: int):
        """显示详情"""
        if 0 <= row < len(self.filtered_history):
            record = self.filtered_history[row]
            timestamp = record.get("timestamp", "")
            config_name = record.get("config_name", "未知")
            message = record.get("message", "")
            response = record.get("response", "")

            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = timestamp

            self.detail_time.setText(f"时间: {time_str}")
            self.detail_config.setText(f"配置: {config_name}")
            self.detail_message.setPlainText(message)
            self.detail_response.setPlainText(response)
        else:
            self.detail_time.setText("时间: -")
            self.detail_config.setText("配置: -")
            self.detail_message.clear()
            self.detail_response.clear()

    def clear_history(self):
        """清空历史"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空所有历史记录吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.history = []
            self.filtered_history = []
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump({"history": []}, f)
            self.refresh_list()
            self.show_detail(-1)
