"""
Terminal AI GUI - 主窗口
Glassmorphism + Dark Mode 设计
"""

import sys
import os

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QStackedWidget, QStatusBar, QFrame,
        QScrollArea, QGraphicsDropShadowEffect, QSizePolicy
    )
    from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint, QSize
    from PyQt5.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush, QMouseEvent, QCursor
except ImportError:
    print("错误: 需要安装 PyQt5")
    print("运行: pip install PyQt5")
    sys.exit(1)

from gui.config_manager import ConfigManager
from gui.api_tester import APITester
from gui.history import HistoryWidget
from gui.stats import StatsWidget
from gui.command_manager import CommandManager


# Glassmorphism Dark Mode 配色方案
COLORS = {
    # 背景色
    'bg_primary': '#0F172A',      # 深蓝灰背景
    'bg_secondary': '#1E293B',    # 次级背景
    'bg_card': 'rgba(30, 41, 59, 0.8)',  # 玻璃卡片背景
    'bg_hover': 'rgba(51, 65, 85, 0.9)', # 悬停背景
    'bg_input': '#1E293B',        # 输入框背景

    # 文字色
    'text_primary': '#F8FAFC',    # 主文字
    'text_secondary': '#94A3B8',  # 次级文字
    'text_muted': '#64748B',      # 弱化文字

    # 主题色
    'primary': '#F59E0B',         # 琥珀色 (主色)
    'primary_hover': '#D97706',   # 琥珀色悬停
    'primary_light': 'rgba(245, 158, 11, 0.15)',  # 琥珀色浅色

    'accent': '#8B5CF6',          # 紫色 (强调色)
    'accent_hover': '#7C3AED',    # 紫色悬停
    'accent_light': 'rgba(139, 92, 246, 0.15)',   # 紫色浅色

    # 状态色
    'success': '#10B981',         # 绿色
    'danger': '#EF4444',          # 红色
    'warning': '#F59E0B',         # 橙色

    # 边框
    'border': 'rgba(51, 65, 85, 0.6)',  # 边框
    'border_light': 'rgba(148, 163, 184, 0.3)',  # 浅边框
    'border_focus': '#F59E0B',    # 焦点边框
}


class ResizableFrame(QFrame):
    """可调整大小的框架"""

    EDGE_SIZE = 8  # 边缘检测区域大小

    def __init__(self, parent=None):
        super().__init__(parent)
        self._edge = None
        self._dragging = False
        self._drag_start_pos = None
        self._drag_start_geometry = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.globalPos()
            self._drag_start_geometry = self.geometry()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging and self._edge:
            delta = event.globalPos() - self._drag_start_pos
            geo = self._drag_start_geometry

            if self._edge & Qt.LeftEdge:
                geo.setLeft(geo.left() + delta.x())
            if self._edge & Qt.RightEdge:
                geo.setRight(geo.right() + delta.x())
            if self._edge & Qt.TopEdge:
                geo.setTop(geo.top() + delta.y())
            if self._edge & Qt.BottomEdge:
                geo.setBottom(geo.bottom() + delta.y())

            self.setGeometry(geo)
            event.accept()
        else:
            # 更新光标
            pos = event.pos()
            edges = 0
            if pos.x() < self.EDGE_SIZE:
                edges |= Qt.LeftEdge
            if pos.x() > self.width() - self.EDGE_SIZE:
                edges |= Qt.RightEdge
            if pos.y() < self.EDGE_SIZE:
                edges |= Qt.TopEdge
            if pos.y() > self.height() - self.EDGE_SIZE:
                edges |= Qt.BottomEdge

            if edges:
                if edges & Qt.LeftEdge and edges & Qt.TopEdge:
                    self.setCursor(Qt.SizeFDiagCursor)
                elif edges & Qt.RightEdge and edges & Qt.BottomEdge:
                    self.setCursor(Qt.SizeFDiagCursor)
                elif edges & Qt.LeftEdge and edges & Qt.BottomEdge:
                    self.setCursor(Qt.SizeBDiagCursor)
                elif edges & Qt.RightEdge and edges & Qt.TopEdge:
                    self.setCursor(Qt.SizeBDiagCursor)
                elif edges & Qt.LeftEdge or edges & Qt.RightEdge:
                    self.setCursor(Qt.SizeHorCursor)
                elif edges & Qt.TopEdge or edges & Qt.BottomEdge:
                    self.setCursor(Qt.SizeVerCursor)
                self._edge = edges
            else:
                self.setCursor(Qt.ArrowCursor)
                self._edge = None

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._dragging = False
        self._edge = None


class GlassCard(QFrame):
    """玻璃效果卡片"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()

    def setup_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
            }}
        """)


class SidebarButton(QPushButton):
    """侧边栏按钮"""

    def __init__(self, icon, text, parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.button_text = text
        self.setText(f"{icon}  {text}")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(48)
        self.setup_style()

    def setup_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                padding: 0 20px;
                text-align: left;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
                font-weight: 600;
            }}
        """)


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Terminal AI")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        # 窗口拖拽相关
        self._drag_position = None

        self.setup_ui()

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            # 只在标题栏区域允许拖动
            if event.y() < 60:
                self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件 - 用于拖动窗口"""
        if event.buttons() == Qt.LeftButton and self._drag_position:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        self._drag_position = None

    def toggle_maximize(self):
        """切换最大化状态"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key_F11:
            self.toggle_maximize()
        super().keyPressEvent(event)

    def setup_ui(self):
        # 设置应用字体
        font = QFont("Segoe UI, -apple-system, BlinkMacSystemFont, Roboto, sans-serif", 11)
        QApplication.setFont(font)

        # 主容器
        main_container = ResizableFrame()
        main_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_primary']};
                border-radius: 0px;
                border: 1px solid {COLORS['border']};
            }}
        """)

        # 中心部件
        self.setCentralWidget(main_container)

        # 主布局
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 标题栏
        title_bar = QFrame()
        title_bar.setFixedHeight(60)
        title_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(20, 0, 12, 0)

        # 窗口标题
        title_label = QLabel("Terminal AI")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 16px;
                font-weight: 600;
            }}
        """)
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()

        # 窗口控制按钮
        minimize_btn = QPushButton("─")
        minimize_btn.setFixedSize(36, 36)
        minimize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                color: {COLORS['text_primary']};
            }}
        """)
        minimize_btn.clicked.connect(self.showMinimized)

        maximize_btn = QPushButton("□")
        maximize_btn.setFixedSize(36, 36)
        maximize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                color: {COLORS['text_primary']};
            }}
        """)
        maximize_btn.clicked.connect(self.toggle_maximize)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
                color: {COLORS['text_primary']};
            }}
        """)
        close_btn.clicked.connect(self.close)

        title_bar_layout.addWidget(minimize_btn)
        title_bar_layout.addWidget(maximize_btn)
        title_bar_layout.addWidget(close_btn)

        main_layout.addWidget(title_bar)

        # 内容区域容器
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 侧边栏
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo 区域
        logo_widget = QWidget()
        logo_widget.setStyleSheet(f"background-color: {COLORS['bg_secondary']};")
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(24, 24, 24, 20)

        logo_label = QLabel("Terminal AI")
        logo_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['primary']};
                font-size: 22px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }}
        """)
        logo_layout.addWidget(logo_label)

        subtitle_label = QLabel("API 配置管理")
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_muted']};
                font-size: 12px;
                font-weight: 500;
            }}
        """)
        logo_layout.addWidget(subtitle_label)

        sidebar_layout.addWidget(logo_widget)

        # 导航菜单
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(12, 8, 12, 20)
        nav_layout.setSpacing(4)

        self.nav_buttons = []
        nav_items = [
            ("🚀", "API 测试"),
            ("⚙️", "配置管理"),
            ("🛡️", "命令管理"),
            ("📜", "历史记录"),
            ("📊", "使用统计"),
        ]

        for icon, title in nav_items:
            btn = SidebarButton(icon, title)
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        nav_layout.addStretch()

        # 退出按钮
        exit_btn = QPushButton("退出应用")
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['danger']};
                border: 1px solid {COLORS['border']};
                padding: 12px 20px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
                color: {COLORS['text_primary']};
                border-color: {COLORS['danger']};
            }}
        """)
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.clicked.connect(self.close)
        nav_layout.addWidget(exit_btn)

        sidebar_layout.addWidget(nav_container)

        # 右侧内容区域
        right_content = QWidget()
        right_content.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_primary']};
            }}
        """)
        right_layout = QVBoxLayout(right_content)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # 顶部标题栏
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_primary']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        header.setFixedHeight(64)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(32, 0, 32, 0)

        self.page_title = QLabel("API 测试")
        self.page_title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 20px;
                font-weight: 600;
            }}
        """)
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()

        # 内容堆栈
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: transparent;")

        # 创建各个页面
        self.config_manager = ConfigManager()
        self.api_tester = APITester(self.config_manager)
        self.command_manager = CommandManager()
        self.history = HistoryWidget()
        self.stats = StatsWidget()

        self.content_stack.addWidget(self.api_tester)
        self.content_stack.addWidget(self.config_manager)
        self.content_stack.addWidget(self.command_manager)
        self.content_stack.addWidget(self.history)
        self.content_stack.addWidget(self.stats)

        # 连接导航按钮
        for i, btn in enumerate(self.nav_buttons):
            btn.clicked.connect(lambda checked, idx=i: self.switch_page(idx))

        # 默认选中第一个
        self.nav_buttons[0].setChecked(True)

        right_layout.addWidget(header)
        right_layout.addWidget(self.content_stack)

        # 布局：侧边栏 + 右侧内容
        content_layout.addWidget(sidebar)
        content_layout.addWidget(right_content, 1)

        main_layout.addWidget(content_container)

        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_muted']};
                border-top: 1px solid {COLORS['border']};
                font-size: 12px;
                padding: 4px;
            }}
        """)
        right_layout.addWidget(self.status_bar)
        self.update_status_bar()

        # 配置变化时更新状态栏
        self.config_manager.config_changed.connect(self.update_status_bar)

    def switch_page(self, index: int):
        """切换页面"""
        # 更新按钮状态
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        # 切换页面
        self.content_stack.setCurrentIndex(index)

        # 更新标题
        titles = ["API 测试", "配置管理", "命令管理", "历史记录", "使用统计"]
        self.page_title.setText(titles[index])

        # 加载数据
        if index == 2:  # 命令管理
            self.command_manager.load_commands()
        elif index == 3:  # 历史记录
            self.history.load_history()
        elif index == 4:  # 统计
            self.stats.load_stats()

    def update_status_bar(self):
        """更新状态栏"""
        default_config = self.config_manager.get_default_config()
        if default_config:
            self.status_bar.showMessage(f"  默认配置: {default_config['name']}  |  模型: {default_config.get('model', 'N/A')}")
        else:
            self.status_bar.showMessage("  未设置默认配置")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Glassmorphism Dark Mode 全局样式
    app.setStyleSheet(f"""
        QMainWindow {{
            background-color: {COLORS['bg_primary']};
        }}

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

        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            padding: 10px 14px;
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

        QComboBox {{
            padding: 10px 30px 10px 14px;
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
            background-color: {COLORS['bg_hover']};
        }}

        QListWidget::item:selected {{
            background-color: {COLORS['primary_light']};
            color: {COLORS['primary']};
        }}

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
            background-color: {COLORS['bg_hover']};
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

        QTabWidget::pane {{
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            background-color: {COLORS['bg_card']};
        }}

        QTabBar::tab {{
            background-color: {COLORS['bg_secondary']};
            color: {COLORS['text_muted']};
            padding: 10px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 4px;
            font-size: 14px;
            font-weight: 500;
        }}

        QTabBar::tab:selected {{
            background-color: {COLORS['bg_card']};
            color: {COLORS['primary']};
            border-bottom: 2px solid {COLORS['primary']};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {COLORS['bg_hover']};
        }}

        QScrollArea {{
            border: none;
            background-color: transparent;
        }}

        QLabel {{
            color: {COLORS['text_primary']};
            font-size: 14px;
        }}

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
                stop:0 {COLORS['primary']}, stop:1 {COLORS['accent']});
            border-radius: 8px;
        }}

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

        QFormLayout {{
            spacing: 12px;
        }}

        QFormLayout QLabel {{
            color: {COLORS['text_primary']};
            font-size: 13px;
            font-weight: 500;
        }}

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
