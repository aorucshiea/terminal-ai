"""
配置管理界面 - Glassmorphism + Dark Mode 设计
"""

import json
import os
from typing import Dict, List, Optional

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
        QLabel, QLineEdit, QFormLayout, QDialog, QMessageBox, QComboBox,
        QSpinBox, QDoubleSpinBox, QGroupBox, QFrame
    )
    from PyQt5.QtCore import Qt, pyqtSignal
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


class ConfigDialog(QDialog):
    """配置编辑对话框"""

    def __init__(self, config: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.config = config or {}
        self.setWindowTitle("编辑配置" if config else "添加配置")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 标题
        title = QLabel("配置详情")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 20px;
                font-weight: 600;
            }}
        """)
        layout.addWidget(title)

        # 表单
        form_layout = QFormLayout()
        form_layout.setSpacing(16)

        self.name_edit = QLineEdit(self.config.get("name", ""))
        self.name_edit.setPlaceholderText("配置名称")
        self.name_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
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

        self.api_key_edit = QLineEdit(self.config.get("api_key", ""))
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("API Key")
        self.api_key_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
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

        self.endpoint_edit = QLineEdit(self.config.get("endpoint", ""))
        self.endpoint_edit.setPlaceholderText("https://api.example.com/v1")
        self.endpoint_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
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

        self.model_edit = QLineEdit(self.config.get("model", "gpt-4"))
        self.model_edit.setPlaceholderText("gpt-4")
        self.model_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
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

        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 100000)
        self.max_tokens_spin.setValue(self.config.get("max_tokens", 2000))
        self.max_tokens_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QSpinBox:focus {{
                border: 2px solid {COLORS['border_focus']};
            }}
        """)

        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0, 2)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(self.config.get("temperature", 0.7))
        self.temperature_spin.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {COLORS['bg_input']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QDoubleSpinBox:focus {{
                border: 2px solid {COLORS['border_focus']};
            }}
        """)

        form_layout.addRow("名称:", self.name_edit)
        form_layout.addRow("API Key:", self.api_key_edit)
        form_layout.addRow("Endpoint:", self.endpoint_edit)
        form_layout.addRow("模型:", self.model_edit)
        form_layout.addRow("最大 Tokens:", self.max_tokens_spin)
        form_layout.addRow("温度:", self.temperature_spin)

        layout.addLayout(form_layout)

        # 按钮
        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
                color: {COLORS['text_primary']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)

        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet(f"""
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
        """)
        ok_btn.clicked.connect(self.accept)

        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def get_config(self) -> Optional[Dict]:
        """获取配置，验证后返回"""
        config = {
            "name": self.name_edit.text().strip(),
            "api_key": self.api_key_edit.text().strip(),
            "endpoint": self.endpoint_edit.text().strip(),
            "model": self.model_edit.text().strip(),
            "max_tokens": self.max_tokens_spin.value(),
            "temperature": self.temperature_spin.value()
        }

        # 验证必填字段
        if not config["name"]:
            QMessageBox.warning(self, "错误", "请输入配置名称")
            return None
        if not config["api_key"]:
            QMessageBox.warning(self, "错误", "请输入 API Key")
            return None
        if not config["endpoint"]:
            QMessageBox.warning(self, "错误", "请输入 API Endpoint")
            return None
        if not config["model"]:
            QMessageBox.warning(self, "错误", "请输入模型名称")
            return None

        # URL 格式验证
        if not config["endpoint"].startswith(("http://", "https://")):
            QMessageBox.warning(self, "错误", "Endpoint 必须以 http:// 或 https:// 开头")
            return None

        return config


class ConfigManager(QWidget):
    """配置管理界面"""

    config_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.configs: List[Dict] = []
        self.default_config: Optional[str] = None
        self.data_file = os.path.join(os.path.dirname(__file__), "data", "configs.json")
        self.load_configs()
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # 左侧配置列表
        left_panel = QVBoxLayout()
        left_panel.setSpacing(16)

        # 标题
        title = QLabel("配置列表")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: 600;
            }}
        """)
        left_panel.addWidget(title)

        self.config_list = QListWidget()
        self.config_list.itemDoubleClicked.connect(self.edit_config)
        self.config_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                font-size: 14px;
                color: {COLORS['text_primary']};
                outline: none;
            }}
            QListWidget::item {{
                padding: 14px 18px;
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
        """)
        left_panel.addWidget(self.config_list)

        # 按钮组
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        add_btn = QPushButton("添加")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
        """)
        add_btn.clicked.connect(self.add_config)

        edit_btn = QPushButton("编辑")
        edit_btn.setStyleSheet(f"""
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
                background-color: {COLORS['bg_hover']};
            }}
        """)
        edit_btn.clicked.connect(self.edit_config)

        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet(f"""
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
        delete_btn.clicked.connect(self.delete_config)

        test_btn = QPushButton("测试连接")
        test_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
        """)
        test_btn.clicked.connect(self.test_connection)

        set_default_btn = QPushButton("设为默认")
        set_default_btn.setStyleSheet(f"""
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
                background-color: {COLORS['bg_hover']};
            }}
        """)
        set_default_btn.clicked.connect(self.set_default)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(test_btn)
        btn_layout.addWidget(set_default_btn)

        left_panel.addLayout(btn_layout)

        # 右侧配置详情
        right_panel = QGroupBox("配置详情")
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
        right_layout = QFormLayout()
        right_layout.setSpacing(16)

        self.detail_name = QLabel("-")
        self.detail_endpoint = QLabel("-")
        self.detail_model = QLabel("-")
        self.detail_max_tokens = QLabel("-")
        self.detail_temperature = QLabel("-")
        self.detail_default = QLabel("-")

        for label in [self.detail_name, self.detail_endpoint, self.detail_model,
                      self.detail_max_tokens, self.detail_temperature, self.detail_default]:
            label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px;")

        right_layout.addRow("名称:", self.detail_name)
        right_layout.addRow("Endpoint:", self.detail_endpoint)
        right_layout.addRow("模型:", self.detail_model)
        right_layout.addRow("最大 Tokens:", self.detail_max_tokens)
        right_layout.addRow("温度:", self.detail_temperature)
        right_layout.addRow("默认:", self.detail_default)

        right_panel.setLayout(right_layout)

        self.config_list.currentRowChanged.connect(self.update_detail)

        layout.addLayout(left_panel, 2)
        layout.addWidget(right_panel, 1)

        self.setLayout(layout)
        self.refresh_list()

    def load_configs(self):
        """加载配置"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.configs = data.get("configs", [])
                self.default_config = data.get("default_config")
        except FileNotFoundError:
            self.configs = []
            self.default_config = None

    def save_configs(self):
        """保存配置"""
        data = {
            "configs": self.configs,
            "default_config": self.default_config
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.config_changed.emit()

    def refresh_list(self):
        """刷新配置列表"""
        self.config_list.clear()
        for config in self.configs:
            item_text = config["name"]
            if config["name"] == self.default_config:
                item_text += " [默认]"
            self.config_list.addItem(item_text)

    def update_detail(self, row: int):
        """更新配置详情"""
        if 0 <= row < len(self.configs):
            config = self.configs[row]
            self.detail_name.setText(config["name"])
            self.detail_endpoint.setText(config["endpoint"])
            self.detail_model.setText(config["model"])
            self.detail_max_tokens.setText(str(config["max_tokens"]))
            self.detail_temperature.setText(str(config["temperature"]))
            is_default = config["name"] == self.default_config
            self.detail_default.setText("是" if is_default else "否")
        else:
            self.detail_name.setText("-")
            self.detail_endpoint.setText("-")
            self.detail_model.setText("-")
            self.detail_max_tokens.setText("-")
            self.detail_temperature.setText("-")
            self.detail_default.setText("-")

    def add_config(self):
        """添加配置"""
        dialog = ConfigDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_config()
            if config is None:
                return  # 验证失败，已在对话框中显示错误
            if any(c["name"] == config["name"] for c in self.configs):
                QMessageBox.warning(self, "错误", "配置名称已存在")
                return
            self.configs.append(config)
            if len(self.configs) == 1:
                self.default_config = config["name"]
            self.save_configs()
            self.refresh_list()

    def edit_config(self):
        """编辑配置"""
        row = self.config_list.currentRow()
        if row < 0:
            return
        dialog = ConfigDialog(self.configs[row], parent=self)
        if dialog.exec_() == QDialog.Accepted:
            new_config = dialog.get_config()
            if new_config is None:
                return  # 验证失败，已在对话框中显示错误
            old_name = self.configs[row]["name"]
            if new_config["name"] != old_name:
                if any(c["name"] == new_config["name"] for c in self.configs):
                    QMessageBox.warning(self, "错误", "配置名称已存在")
                    return
                if self.default_config == old_name:
                    self.default_config = new_config["name"]
            self.configs[row] = new_config
            self.save_configs()
            self.refresh_list()

    def delete_config(self):
        """删除配置"""
        row = self.config_list.currentRow()
        if row < 0:
            return
        config_name = self.configs[row]["name"]
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除配置 '{config_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.default_config == config_name:
                self.default_config = None
            self.configs.pop(row)
            self.save_configs()
            self.refresh_list()

    def set_default(self):
        """设置默认配置"""
        row = self.config_list.currentRow()
        if row < 0:
            return
        self.default_config = self.configs[row]["name"]
        self.save_configs()
        self.refresh_list()

    def test_connection(self):
        """测试连接"""
        row = self.config_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一个配置")
            return

        config = self.configs[row]
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=config["api_key"],
                base_url=config["endpoint"]
            )
            response = client.chat.completions.create(
                model=config["model"],
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            QMessageBox.information(
                self, "测试成功",
                f"连接成功！\n响应: {response.choices[0].message.content}"
            )
        except Exception as e:
            QMessageBox.critical(self, "测试失败", f"连接失败: {str(e)}")

    def get_default_config(self) -> Optional[Dict]:
        """获取默认配置"""
        if not self.default_config:
            return None
        for config in self.configs:
            if config["name"] == self.default_config:
                return config
        return None

    def get_config_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取配置"""
        for config in self.configs:
            if config["name"] == name:
                return config
        return None

    def get_all_configs(self) -> List[Dict]:
        """获取所有配置"""
        return self.configs.copy()
