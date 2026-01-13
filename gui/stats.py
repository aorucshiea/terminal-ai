"""
使用统计界面 - 基于 Soft UI Evolution 风格
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
    'success': '#10B981',
    'warning': '#F59E0B',
}


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
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 标题
        title = QLabel("使用统计")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 24px;
                font-weight: 700;
            }}
        """)
        layout.addWidget(title)

        # 描述
        desc = QLabel("查看 API 调用次数和 Token 消耗统计")
        desc.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_muted']};
                font-size: 14px;
            }}
        """)
        layout.addWidget(desc)

        # 总体统计
        summary_group = QGroupBox("总体统计")
        summary_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: {COLORS['text']};
                font-size: 14px;
            }}
        """)
        summary_layout = QHBoxLayout()
        summary_layout.setContentsMargins(16, 8, 16, 16)

        self.total_calls_label = QLabel("总调用次数: 0")
        self.total_calls_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 16px;
                font-weight: 600;
            }}
        """)
        self.total_tokens_label = QLabel("总 Token 数: 0")
        self.total_tokens_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 16px;
                font-weight: 600;
            }}
        """)

        summary_layout.addWidget(self.total_calls_label)
        summary_layout.addWidget(self.total_tokens_label)
        summary_layout.addStretch()

        refresh_btn = QPushButton("刷新")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['surface']};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
        """)
        refresh_btn.clicked.connect(self.load_stats)
        summary_layout.addWidget(refresh_btn)

        summary_group.setLayout(summary_layout)

        # 配置统计表格
        config_group = QGroupBox("配置使用统计")
        config_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: {COLORS['text']};
                font-size: 14px;
            }}
        """)
        config_layout = QVBoxLayout()
        config_layout.setContentsMargins(16, 8, 16, 16)

        self.config_table = QTableWidget()
        self.config_table.setColumnCount(3)
        self.config_table.setHorizontalHeaderLabels(["配置名称", "调用次数", "Token 数"])
        self.config_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                gridline-color: {COLORS['border']};
                color: {COLORS['text']};
                font-size: 14px;
                outline: none;
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {COLORS['border']};
                color: {COLORS['text']};
            }}
            QTableWidget::item:hover {{
                background-color: {COLORS['background']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['background']};
                color: {COLORS['text_muted']};
                padding: 12px;
                border: none;
                border-right: 1px solid {COLORS['border']};
                border-bottom: 1px solid {COLORS['border']};
                font-weight: 600;
                font-size: 13px;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 12px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 12px;
            }}
        """)
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
