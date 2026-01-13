"""
使用统计界面
"""

import json
import os
from typing import Dict

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
    )
    from PyQt5.QtCore import Qt
except ImportError:
    print("错误: 需要安装 PyQt5")
    print("运行: pip install PyQt5")
    raise


class StatsWidget(QWidget):
    """使用统计界面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats: Dict = {}
        self.stats_file = os.path.join(os.path.dirname(__file__), "data", "stats.json")
        self.setup_ui()
        self.load_stats()

    def setup_ui(self):
        layout = QVBoxLayout()

        # 总体统计
        summary_group = QGroupBox("总体统计")
        summary_layout = QHBoxLayout()

        self.total_calls_label = QLabel("总调用次数: 0")
        self.total_calls_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.total_tokens_label = QLabel("总 Token 数: 0")
        self.total_tokens_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        summary_layout.addWidget(self.total_calls_label)
        summary_layout.addWidget(self.total_tokens_label)
        summary_layout.addStretch()

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_stats)
        summary_layout.addWidget(refresh_btn)

        summary_group.setLayout(summary_layout)

        # 配置统计表格
        config_group = QGroupBox("配置使用统计")
        config_layout = QVBoxLayout()

        self.config_table = QTableWidget()
        self.config_table.setColumnCount(3)
        self.config_table.setHorizontalHeaderLabels(["配置名称", "调用次数", "Token 数"])
        self.config_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.config_table.verticalHeader().setVisible(False)
        config_layout.addWidget(self.config_table)

        config_group.setLayout(config_layout)

        layout.addWidget(summary_group)
        layout.addWidget(config_group)

        self.setLayout(layout)

    def load_stats(self):
        """加载统计数据"""
        try:
            with open(self.stats_file, "r", encoding="utf-8") as f:
                self.stats = json.load(f)
        except FileNotFoundError:
            self.stats = {"total_calls": 0, "total_tokens": 0, "config_stats": {}}

        self.update_display()

    def update_display(self):
        """更新显示"""
        # 更新总体统计
        total_calls = self.stats.get("total_calls", 0)
        total_tokens = self.stats.get("total_tokens", 0)
        self.total_calls_label.setText(f"总调用次数: {total_calls}")
        self.total_tokens_label.setText(f"总 Token 数: {total_tokens}")

        # 更新配置统计表格
        config_stats = self.stats.get("config_stats", {})
        self.config_table.setRowCount(len(config_stats))

        for row, (config_name, stats) in enumerate(config_stats.items()):
            calls = stats.get("calls", 0)
            tokens = stats.get("tokens", 0)

            self.config_table.setItem(row, 0, QTableWidgetItem(config_name))
            self.config_table.setItem(row, 1, QTableWidgetItem(str(calls)))
            self.config_table.setItem(row, 2, QTableWidgetItem(str(tokens)))
