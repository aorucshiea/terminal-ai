"""
配置管理界面
"""

import json
import os
from typing import Dict, List, Optional

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
        QLabel, QLineEdit, QFormLayout, QDialog, QMessageBox, QComboBox,
        QSpinBox, QDoubleSpinBox, QGroupBox
    )
    from PyQt5.QtCore import Qt, pyqtSignal
except ImportError:
    print("错误: 需要安装 PyQt5")
    print("运行: pip install PyQt5")
    raise


class ConfigDialog(QDialog):
    """配置编辑对话框"""

    def __init__(self, config: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.config = config or {}
        self.setWindowTitle("编辑配置" if config else "添加配置")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()

        self.name_edit = QLineEdit(self.config.get("name", ""))
        self.api_key_edit = QLineEdit(self.config.get("api_key", ""))
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.endpoint_edit = QLineEdit(self.config.get("endpoint", ""))
        self.model_edit = QLineEdit(self.config.get("model", "gpt-4"))

        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 100000)
        self.max_tokens_spin.setValue(self.config.get("max_tokens", 2000))

        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0, 2)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(self.config.get("temperature", 0.7))

        layout.addRow("名称:", self.name_edit)
        layout.addRow("API Key:", self.api_key_edit)
        layout.addRow("Endpoint:", self.endpoint_edit)
        layout.addRow("模型:", self.model_edit)
        layout.addRow("最大 Tokens:", self.max_tokens_spin)
        layout.addRow("温度:", self.temperature_spin)

        buttons = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(buttons)
        self.setLayout(main_layout)

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

        # 左侧配置列表
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("配置列表:"))

        self.config_list = QListWidget()
        self.config_list.itemDoubleClicked.connect(self.edit_config)
        left_panel.addWidget(self.config_list)

        # 按钮组
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.add_config)
        edit_btn = QPushButton("编辑")
        edit_btn.clicked.connect(self.edit_config)
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_config)
        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self.test_connection)
        set_default_btn = QPushButton("设为默认")
        set_default_btn.clicked.connect(self.set_default)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(test_btn)
        btn_layout.addWidget(set_default_btn)

        left_panel.addLayout(btn_layout)

        # 右侧配置详情
        right_panel = QGroupBox("配置详情")
        right_layout = QFormLayout()

        self.detail_name = QLabel("-")
        self.detail_endpoint = QLabel("-")
        self.detail_model = QLabel("-")
        self.detail_max_tokens = QLabel("-")
        self.detail_temperature = QLabel("-")
        self.detail_default = QLabel("-")

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
