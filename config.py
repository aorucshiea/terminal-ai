"""
配置管理模块
优先从 GUI 的 configs.json 读取配置，回退到 .env 文件或环境变量
"""

import os
import json
from typing import Optional


def load_env_file(env_path: str = None) -> dict:
    """
    从 .env 文件加载配置

    Args:
        env_path: .env 文件路径，默认为项目根目录下的 .env

    Returns:
        配置字典
    """
    if env_path is None:
        # 获取项目根目录（本文件所在目录）
        env_path = os.path.join(os.path.dirname(__file__), ".env")

    config = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue
                # 解析 KEY=VALUE 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    return config


def load_gui_config() -> Optional[dict]:
    """
    从 GUI 配置文件读取默认配置

    Returns:
        默认配置字典，如果不存在则返回 None
    """
    config_file = os.path.join(os.path.dirname(__file__), "gui/data/configs.json")
    if not os.path.exists(config_file):
        return None

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            default_name = data.get("default_config")
            if not default_name:
                return None
            for config in data.get("configs", []):
                if config.get("name") == default_name:
                    return config
    except (json.JSONDecodeError, IOError):
        pass

    return None


class Config:
    """AI 配置类"""

    def __init__(self, env_path: str = None):
        # 优先级 1: 从 GUI 的 configs.json 读取默认配置
        gui_config = load_gui_config()

        # 优先级 2: 从 .env 文件加载
        env_config = load_env_file(env_path)

        # 优先级 3: 环境变量

        # API Endpoint
        self.api_endpoint: str = (
            os.getenv("AI_API_ENDPOINT")
            or (gui_config.get("endpoint") if gui_config else None)
            or env_config.get("AI_API_ENDPOINT", "https://api.openai.com/v1")
        )

        # API Key
        self.api_key: Optional[str] = (
            os.getenv("AI_API_KEY")
            or (gui_config.get("api_key") if gui_config else None)
            or env_config.get("AI_API_KEY")
        )

        # Model
        self.model: str = (
            os.getenv("AI_MODEL")
            or (gui_config.get("model") if gui_config else None)
            or env_config.get("AI_MODEL", "gpt-4")
        )

        # Max Tokens
        self.max_tokens: int = int(
            os.getenv("AI_MAX_TOKENS")
            or (str(gui_config.get("max_tokens")) if gui_config else None)
            or env_config.get("AI_MAX_TOKENS", "2000")
        )

        # Temperature
        self.temperature: float = float(
            os.getenv("AI_TEMPERATURE")
            or (str(gui_config.get("temperature")) if gui_config else None)
            or env_config.get("AI_TEMPERATURE", "0.7")
        )

        # 配置来源（用于调试）
        self._source = "env" if gui_config else "env_file"

    def validate(self) -> tuple[bool, str]:
        """
        验证配置是否有效

        Returns:
            (是否有效, 错误信息)
        """
        if not self.api_key:
            return False, "未找到 AI_API_KEY，请在 GUI 中配置、.env 文件中配置或设置环境变量"

        if not self.api_endpoint:
            return False, "未找到 AI_API_ENDPOINT，请在 GUI 中配置、.env 文件中配置或设置环境变量"

        return True, ""

    def __repr__(self) -> str:
        return (
            f"Config(api_endpoint={self.api_endpoint}, "
            f"model={self.model}, "
            f"max_tokens={self.max_tokens}, "
            f"temperature={self.temperature}, "
            f"source={self._source})"
        )


# 全局配置实例
config = Config()
