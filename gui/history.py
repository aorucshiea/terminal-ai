"""
历史记录界面
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


class HistoryWidget(QWidget):
    """历史记录界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history: List[Dict] = []
        self.filtered_history: List[Dict] = []
        self.history_file = os.path.join(os.path.dirname(__file__), "data", "history.json")
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        layout = QHBoxLayout()

        # 左侧历史列表
        left_panel = QVBoxLayout()

        # 筛选栏
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("筛选:"))
        self.config_filter = QComboBox()
        self.config_filter.addItem("全部配置")
        self.config_filter.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.config_filter)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索...")
        self.search_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.search_input)

        left_panel.addLayout(filter_layout)

        # 历史列表
        self.history_list = QListWidget()
        self.history_list.currentRowChanged.connect(self.show_detail)
        left_panel.addWidget(self.history_list)

        # 按钮
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_history)
        clear_btn = QPushButton("清空历史")
        clear_btn.clicked.connect(self.clear_history)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(clear_btn)
        left_panel.addLayout(btn_layout)

        # 右侧详情
        right_panel = QGroupBox("记录详情")
        right_layout = QVBoxLayout()

        self.detail_time = QLabel("时间: -")
        self.detail_config = QLabel("配置: -")
        right_layout.addWidget(self.detail_time)
        right_layout.addWidget(self.detail_config)

        right_layout.addWidget(QLabel("消息:"))
        self.detail_message = QTextEdit()
        self.detail_message.setReadOnly(True)
        self.detail_message.setMaximumHeight(150)
        right_layout.addWidget(self.detail_message)

        right_layout.addWidget(QLabel("响应:"))
        self.detail_response = QTextEdit()
        self.detail_response.setReadOnly(True)
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
                json.dump({"history": []}, f, indent=2)
            self.refresh_list()
            self.show_detail(-1)
