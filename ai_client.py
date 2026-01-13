"""
AI 客户端模块
封装 OpenAI 兼容 API 调用
"""

import sys
from typing import Generator, Optional, List

try:
    from openai import OpenAI
except ImportError:
    print("错误: 需要安装 openai 库")
    print("运行: pip install openai")
    sys.exit(1)

from config import Config


class AIClient:
    """AI API 客户端"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.api_endpoint
        )

    def chat(
        self,
        message: str,
        context: str = "",
        stream: bool = True
    ) -> Generator[str, None, None]:
        """
        发送聊天请求（单条消息模式）

        Args:
            message: 用户消息
            context: 上下文信息
            stream: 是否流式输出

        Yields:
            AI 响应内容
        """
        system_prompt = self._build_system_prompt(context)

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stream=stream
            )

            if stream:
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content

        except Exception as e:
            yield f"\n[错误] API 调用失败: {e}"

    def chat_with_messages(
        self,
        messages: List[dict],
        stream: bool = True
    ) -> Generator[str, None, None]:
        """
        发送聊天请求（多消息模式，支持会话历史）

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}, ...]
            stream: 是否流式输出

        Yields:
            AI 响应内容
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                stream=stream
            )

            if stream:
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content

        except Exception as e:
            yield f"\n[错误] API 调用失败: {e}"

    def _build_system_prompt(self, context: str) -> str:
        """构建系统提示词"""
        base_prompt = """你是一个终端 AI 助手，帮助用户解决编程和命令行问题。

你的职责：
- 分析错误信息并提供解决方案
- 解释命令和代码的含义
- 提供实用的建议和最佳实践
- 回答要简洁明了，重点突出

回答风格：
- 使用 Markdown 格式
- 代码块使用 ```language 标记
- 重要信息用 **加粗** 标记
- 保持回答简洁，避免冗长
"""

        if context:
            return f"{base_prompt}\n\n---\n\n当前上下文信息：\n{context}\n---\n\n"

        return base_prompt
