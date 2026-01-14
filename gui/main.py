"""
Terminal AI GUI - 主窗口
Glassmorphism + Dark Mode (OLED) 设计
"""

import sys
import os

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QStackedWidget, QFrame, QSizePolicy
    )
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QFont, QIcon
except ImportError:
    print("错误: 需要安装 PyQt5")
    print("运行: pip install PyQt5")
    sys.exit(1)

# 导入各功能模块
from config_manager import ConfigManager
from api_tester import APITester
from history import HistoryWidget
from stats import StatsWidget
from command_manager import CommandManager

# Glassmorphism Dark Mode (OLED) 配色方案
COLORS = {
    # 背景色 - OLED 风格深色
    'bg_primary': '#020617',      # 深蓝黑背景 (OLED 风格)
    'bg_secondary': '#0F172A',    # 次级背景
    'bg_card': 'rgba(15, 23, 42, 0.8)',  # 玻璃卡片背景
    'bg_card_hover': 'rgba(30, 41, 59, 0.9)',  # 卡片悬停
    'bg_input': '#1E293B',        # 输入框背景
    'bg_nav': 'rgba(2, 6, 23, 0.95)',  # 导航栏背景

    # 文字色 - 高对比度
    'text_primary': '#F9FAFB',    # 主文字 (高对比)
    'text_secondary': '#CBD5E1',  # 次级文字
    'text_muted': '#64748B',      # 弱化文字

    # 主题色 - 电光蓝系
    'primary': '#0EA5E9',         # 电光蓝 (主强调色)
    'primary_hover': '#0284C7',   # 主色悬停
    'primary_light': 'rgba(14, 165, 233, 0.15)',  # 主色浅色背景

    # 状态色 - 柔和色调
    'success': '#22C55E',         # 柔和绿
    'success_light': 'rgba(34, 197, 94, 0.15)',
    'warning': '#FBBF24',         # 琥珀橙
    'warning_light': 'rgba(251, 191, 36, 0.15)',
    'danger': '#FCA5A5',          # 暖红
    'danger_light': 'rgba(252, 165, 165, 0.15)',

    # 边框
    'border': 'rgba(51, 65, 85, 0.5)',  # 边框
    'border_light': 'rgba(148, 163, 184, 0.2)',
    'border_focus': '#0EA5E9',    # 焦点边框
    'shadow': 'rgba(0, 0, 0, 0.3)',  # 阴影
}


class NavButton(QPushButton):
    """导航按钮 - 现代极简风格"""

    def __init__(self, icon_text: str, label: str, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.label_text = label
        self.is_active = False
        self.setup_ui()

    def setup_ui(self):
        self.setCheckable(True)
        self.setFixedHeight(56)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # 图标
        icon_label = QLabel(self.icon_text)
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 18px;
                font-weight: 500;
            }}
        """)
        self.icon_label = icon_label
        layout.addWidget(icon_label)

        # 标签
        label = QLabel(self.label_text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 14px;
                font-weight: 500;
            }}
        """)
        self.text_label = label
        layout.addWidget(label)

        layout.addStretch()

        self.update_style()

    def update_style(self):
        """更新样式"""
        if self.isChecked():
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['primary_light']};
                    border: 1px solid {COLORS['primary_light']};
                    border-radius: 8px;
                    margin: 4px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['primary_light']};
                }}
            """)
            self.icon_label.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['primary']};
                    font-size: 18px;
                    font-weight: 600;
                }}
            """)
            self.text_label.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['primary']};
                    font-size: 14px;
                    font-weight: 600;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid transparent;
                    border-radius: 8px;
                    margin: 4px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_card_hover']};
                    border: 1px solid {COLORS['border_light']};
                }}
            """)
            self.icon_label.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['text_secondary']};
                    font-size: 18px;
                    font-weight: 500;
                }}
            """)
            self.text_label.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['text_secondary']};
                    font-size: 14px;
                    font-weight: 500;
                }}
            """)

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self.update_style()


class StatusCard(QFrame):
    """状态卡片 - 玻璃拟态风格"""

    def __init__(self, title: str, value: str, color: str = COLORS['primary'], parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.color = color
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        self.setFixedHeight(80)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_muted']};
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)
        layout.addWidget(title_label)

        value_label = QLabel(self.value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-size: 20px;
                font-weight: 600;
            }}
        """)
        layout.addWidget(value_label)


class MainWindow(QMainWindow):
    """主窗口 - 现代极简设计"""

    def __init__(self):
        super().__init__()
        self.config_manager = None
        self.setup_ui()
        self.setup_modules()

    def setup_ui(self):
        """设置 UI"""
        self.setWindowTitle("Terminal AI - 配置面板")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # 主窗口样式
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg_primary']};
            }}
        """)

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧导航栏
        nav_frame = QFrame()
        nav_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_nav']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)
        nav_frame.setFixedWidth(260)

        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        # Logo 区域
        logo_frame = QFrame()
        logo_frame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        logo_frame.setFixedHeight(72)

        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 0, 20, 0)

        logo_icon = QLabel("⚡")
        logo_icon.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['primary']};
                font-size: 24px;
                font-weight: 600;
            }}
        """)
        logo_layout.addWidget(logo_icon)

        logo_text = QLabel("Terminal AI")
        logo_text.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: 600;
                letter-spacing: -0.5px;
            }}
        """)
        logo_layout.addWidget(logo_text)

        logo_layout.addStretch()

        nav_layout.addWidget(logo_frame)

        # 导航按钮
        nav_buttons_layout = QVBoxLayout()
        nav_buttons_layout.setContentsMargins(12, 16, 12, 16)
        nav_buttons_layout.setSpacing(4)

        self.nav_buttons = []
        nav_items = [
            ("⚙️", "配置管理"),
            ("🧪", "API 测试"),
            ("📜", "历史记录"),
            ("📊", "使用统计"),
            ("🛡️", "命令管理"),
        ]

        for icon, label in nav_items:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda checked, b=btn: self.on_nav_clicked(b))
            nav_buttons_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        # 默认选中第一个
        self.nav_buttons[0].setChecked(True)

        nav_buttons_layout.addStretch()
        nav_layout.addLayout(nav_buttons_layout)

        # 底部版本信息
        version_frame = QFrame()
        version_frame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-top: 1px solid {COLORS['border']};
            }}
        """)
        version_frame.setFixedHeight(48)

        version_layout = QHBoxLayout(version_frame)
        version_layout.setContentsMargins(20, 0, 20, 0)

        version_label = QLabel("v2.1.0")
        version_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_muted']};
                font-size: 12px;
            }}
        """)
        version_layout.addWidget(version_label)

        version_layout.addStretch()

        nav_layout.addWidget(version_frame)

        # 右侧内容区
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_primary']};
            }}
        """)

        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 顶部标题栏
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        header_frame.setFixedHeight(64)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 0, 24, 0)

        self.page_title = QLabel("配置管理")
        self.page_title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 20px;
                font-weight: 600;
            }}
        """)
        header_layout.addWidget(self.page_title)

        header_layout.addStretch()

        # 状态指示器
        status_indicator = QLabel("● 已连接")
        status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['success']};
                font-size: 13px;
                font-weight: 500;
            }}
        """)
        header_layout.addWidget(status_indicator)

        content_layout.addWidget(header_frame)

        # 内容堆栈
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {COLORS['bg_primary']};
            }}
        """)
        content_layout.addWidget(self.content_stack)

        # 添加到主布局
        main_layout.addWidget(nav_frame)
        main_layout.addWidget(content_frame, 1)

    def setup_modules(self):
        """设置各功能模块"""
        # 配置管理
        self.config_manager = ConfigManager()
        self.content_stack.addWidget(self.config_manager)

        # API 测试
        self.api_tester = APITester(self.config_manager)
        self.content_stack.addWidget(self.api_tester)

        # 历史记录
        self.history_widget = HistoryWidget()
        self.content_stack.addWidget(self.history_widget)

        # 使用统计
        self.stats_widget = StatsWidget()
        self.content_stack.addWidget(self.stats_widget)

        # 命令管理
        self.command_manager = CommandManager()
        self.content_stack.addWidget(self.command_manager)

        # 配置变更时刷新其他模块
        self.config_manager.config_changed.connect(self.on_config_changed)

    def on_nav_clicked(self, button: NavButton):
        """导航点击"""
        # 更新按钮状态
        for btn in self.nav_buttons:
            btn.setChecked(btn == button)

        # 切换页面
        index = self.nav_buttons.index(button)
        self.content_stack.setCurrentIndex(index)

        # 更新标题
        titles = ["配置管理", "API 测试", "历史记录", "使用统计", "命令管理"]
        self.page_title.setText(titles[index])

    def on_config_changed(self):
        """配置变更"""
        self.api_tester.refresh_configs()


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置应用字体 - Inter 风格
    font = QFont("Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", 10)
    app.setFont(font)

    # 全局样式
    app.setStyleSheet(f"""
        /* 全局背景 */
        QWidget {{
            background-color: {COLORS['bg_primary']};
            color: {COLORS['text_primary']};
        }}

        /* 按钮 */
        QPushButton {{
            padding: 10px 20px;
            background-color: {COLORS['primary']};
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 8px;
            font-weight: 500;
            font-size: 14px;
        }}

        QPushButton:hover {{
            background-color: {COLORS['primary_hover']};
        }}

        QPushButton:pressed {{
            background-color: {COLORS['primary']};
        }}

        QPushButton:disabled {{
            background-color: {COLORS['border']};
            color: {COLORS['text_muted']};
        }}

        /* 输入框 */
        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            padding: 12px 16px;
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            background-color: {COLORS['bg_input']};
            color: {COLORS['text_primary']};
            font-size: 14px;
            selection-background-color: {COLORS['primary_light']};
            selection-color: {COLORS['primary']};
        }}

        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 2px solid {COLORS['border_focus']};
            background-color: {COLORS['bg_input']};
        }}

        QLineEdit:hover, QTextEdit:hover, QComboBox:hover {{
            border-color: {COLORS['border_light']};
        }}

        /* 下拉框 */
        QComboBox {{
            padding: 12px 32px 12px 16px;
        }}

        QComboBox::drop-down {{
            border: none;
            width: 24px;
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

        /* 列表 */
        QListWidget {{
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            background-color: {COLORS['bg_card']};
            color: {COLORS['text_primary']};
            font-size: 14px;
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

        /* 表格 */
        QTableWidget {{
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            background-color: {COLORS['bg_card']};
            gridline-color: {COLORS['border']};
            color: {COLORS['text_primary']};
            font-size: 14px;
            outline: none;
        }}

        QTableWidget::item {{
            padding: 12px;
            border-bottom: 1px solid {COLORS['border']};
            color: {COLORS['text_primary']};
        }}

        QTableWidget::item:hover {{
            background-color: {COLORS['bg_card_hover']};
        }}

        QTableWidget::item:selected {{
            background-color: {COLORS['primary_light']};
            color: {COLORS['primary']};
        }}

        QHeaderView::section {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_secondary']};
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

        /* 分组框 */
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

        /* 标签 */
        QLabel {{
            color: {COLORS['text_primary']};
            font-size: 14px;
        }}

        /* 复选框 */
        QCheckBox {{
            color: {COLORS['text_primary']};
            font-size: 14px;
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {COLORS['border']};
            border-radius: 4px;
            background-color: {COLORS['bg_input']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {COLORS['primary']};
            border-color: {COLORS['primary']};
        }}

        QCheckBox::indicator:hover {{
            border-color: {COLORS['border_light']};
        }}

        /* 进度条 */
        QProgressBar {{
            border: none;
            border-radius: 8px;
            background-color: {COLORS['border']};
            text-align: center;
            font-size: 13px;
            color: {COLORS['text_primary']};
            height: 24px;
        }}

        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['primary']}, stop:1 {COLORS['primary_hover']});
            border-radius: 8px;
        }}

        /* 滚动条 */
        QScrollBar:vertical {{
            border: none;
            background-color: transparent;
            width: 12px;
            border-radius: 6px;
            margin: 4px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {COLORS['border']};
            border-radius: 6px;
            min-height: 30px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {COLORS['border_light']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            border: none;
            background-color: transparent;
            height: 12px;
            border-radius: 6px;
            margin: 4px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {COLORS['border']};
            border-radius: 6px;
            min-width: 30px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {COLORS['border_light']};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* 表单布局 */
        QFormLayout {{
            spacing: 12px;
        }}

        QFormLayout QLabel {{
            color: {COLORS['text_primary']};
            font-size: 13px;
            font-weight: 500;
        }}

        /* 消息框 */
        QMessageBox {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_primary']};
        }}

        QMessageBox QPushButton {{
            min-width: 80px;
            padding: 8px 16px;
            background-color: {COLORS['primary']};
            color: {COLORS['text_primary']};
        }}

        QMessageBox QPushButton:hover {{
            background-color: {COLORS['primary_hover']};
        }}

        /* 对话框 */
        QDialog {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_primary']};
        }}
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
