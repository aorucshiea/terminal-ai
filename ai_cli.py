#!/usr/bin/env python3
"""
终端 AI 助手 CLI 入口
"""

import sys
import os
import subprocess
import json
from datetime import datetime
from typing import Optional, List

from config import Config, config
from context import ContextCollector
from ai_client import AIClient
from command_config import command_config


class SessionManager:
    """会话管理器 - 保存和加载对话历史"""

    def __init__(self, session_file: str = None):
        if session_file is None:
            session_file = os.path.join(
                os.path.dirname(__file__),
                ".session_history.json"
            )
        self.session_file = session_file
        self.history: List[dict] = []
        self.load_session()

    def load_session(self):
        """加载会话历史"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get("history", [])
            except (json.JSONDecodeError, IOError):
                self.history = []

    def save_session(self):
        """保存会话历史"""
        data = {
            "history": self.history,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.save_session()

    def get_history(self, max_turns: int = 10) -> List[dict]:
        """获取最近的对话历史"""
        return self.history[-max_turns * 2:] if self.history else []

    def clear_history(self):
        """清空历史"""
        self.history = []
        self.save_session()

    def get_context_messages(self) -> List[dict]:
        """获取用于 API 调用的消息格式"""
        messages = []
        for msg in self.get_history():
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return messages


class TerminalUI:
    """终端 UI 界面"""

    # 颜色代码
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bg_blue': '\033[44m',
        'bg_cyan': '\033[46m',
    }

    @classmethod
    def color(cls, text: str, color_name: str) -> str:
        """给文本添加颜色"""
        return f"{cls.COLORS.get(color_name, '')}{text}{cls.COLORS['reset']}"

    @classmethod
    def print_header(cls, title: str):
        """打印标题"""
        width = 60
        print()
        print(cls.color('═' * width, 'cyan'))
        print(cls.color(f'  {title}', 'bold'))
        print(cls.color('═' * width, 'cyan'))
        print()

    @classmethod
    def print_menu(cls, options: list, title: str = "请选择"):
        """打印菜单"""
        cls.print_header(title)
        for i, option in enumerate(options, 1):
            print(f"  {cls.color(str(i), 'cyan')}. {option}")
        print()
        print(f"  {cls.color('0', 'cyan')}. 退出")
        print()

    @classmethod
    def print_ai_response(cls, text: str):
        """打印 AI 响应，格式化输出"""
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                # 代码块
                if line.strip().startswith('```'):
                    print(cls.color(line, 'dim'))
                # 标题
                elif line.strip().startswith('#'):
                    print(cls.color(line, 'bold'))
                # 列表项
                elif line.strip().startswith('-') or line.strip().startswith('*'):
                    print(f"  {cls.color(line, 'green')}")
                # 普通文本
                else:
                    print(f"  {line}")
            else:
                print()

    @classmethod
    def print_user_input(cls, text: str):
        """打印用户输入"""
        print()
        print(cls.color('你:', 'yellow'), end=' ')
        print(text)

    @classmethod
    def print_ai_label(cls):
        """打印 AI 标签"""
        print()
        print(cls.color('AI:', 'cyan'), end=' ')
        sys.stdout.flush()

    @classmethod
    def print_error(cls, text: str):
        """打印错误信息"""
        print(cls.color(f'错误: {text}', 'red'))

    @classmethod
    def print_success(cls, text: str):
        """打印成功信息"""
        print(cls.color(f'✓ {text}', 'green'))

    @classmethod
    def print_info(cls, text: str):
        """打印信息"""
        print(cls.color(f'ℹ {text}', 'blue'))

    @classmethod
    def print_divider(cls):
        """打印分隔线"""
        print(cls.color('─' * 60, 'dim'))


class AICLI:
    """AI 命令行界面"""

    # 安全命令白名单
    SAFE_COMMANDS = {
        'ls', 'pwd', 'cd', 'cat', 'head', 'tail', 'grep', 'find',
        'which', 'where', 'uname', 'df', 'du', 'ps', 'top', 'free',
        'echo', 'date', 'whoami', 'hostname', 'file', 'wc', 'sort',
        'uniq', 'cut', 'awk', 'sed', 'tr', 'base64', 'md5sum', 'sha1sum',
        'sha256sum', 'stat', 'id', 'env', 'printenv', 'history', 'jobs',
        'bg', 'fg', 'kill', 'killall', 'pkill', 'pgrep', 'pidof'
    }

    def __init__(self):
        self.client: Optional[AIClient] = None
        self.collector: Optional[ContextCollector] = None
        self.session: Optional[SessionManager] = None
        self.ui = TerminalUI()

    def _is_safe_command(self, command: str) -> bool:
        """检查命令是否安全可执行"""
        # 获取命令的第一个词
        parts = command.strip().split()
        if not parts:
            return False

        cmd = parts[0]

        # 检查是否在白名单中（内置安全命令）
        if cmd in self.SAFE_COMMANDS:
            return True

        # 检查是否在用户信任的命令中
        if command_config.is_trusted(command):
            return True

        return False

    def _ask_trust_command(self, command: str) -> bool:
        """询问用户是否信任该命令"""
        parts = command.strip().split()
        if not parts:
            return False

        cmd = parts[0]

        print()
        print(self.ui.color(f'⚠ 命令 "{cmd}" 不在安全白名单中', 'yellow'))
        print(self.ui.color(f'完整命令: {command}', 'dim'))
        print()
        print('选项:')
        print(f'  {self.ui.color("y", "green")}. 信任此命令并执行')
        print(f'  {self.ui.color("n", "red")}. 不信任，作为问题发送给 AI')
        print(f'  {self.ui.color("a", "cyan")}. 永久信任此命令')
        print()

        choice = input(self.ui.color('请选择 [y/n/a]: ', 'yellow')).strip().lower()

        if choice == 'a':
            # 永久信任
            command_config.add_trusted_command(command, "用户手动添加")
            self.ui.print_success(f'已将 "{cmd}" 添加到信任命令列表')
            return True
        elif choice == 'y':
            # 临时信任
            return True
        else:
            # 不信任
            return False

    def _execute_command(self, command: str) -> tuple[bool, str]:
        """执行命令并返回结果"""
        try:
            result = subprocess.run(
                ['bash', '-c', command],
                capture_output=True,
                text=True,
                timeout=10
            )
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, output
        except subprocess.TimeoutExpired:
            return False, "命令执行超时"
        except Exception as e:
            return False, f"命令执行错误: {e}"

    def _format_command_context(self, command: str, success: bool, output: str) -> str:
        """格式化命令上下文"""
        status = "成功" if success else "失败"
        return f"""## 用户执行的命令
{command}

## 命令输出
{output}

## 执行状态
{status}
"""

    def run(self, args):
        """运行 CLI"""
        # 验证配置
        valid, error = config.validate()
        if not valid:
            self.ui.print_error(error)
            print("\n请在 .env 文件中配置以下内容:")
            print("  AI_API_KEY=your-api-key")
            print("  AI_API_ENDPOINT=https://your-api-endpoint")
            sys.exit(1)

        # 初始化客户端
        self.client = AIClient(config)
        self.collector = ContextCollector(include_history=True)
        self.session = SessionManager()

        # 检查是否为交互式终端
        is_interactive = sys.stdin.isatty()

        # 检查管道输入
        piped_input = self._read_piped_input()
        if piped_input and len(piped_input.strip()) > 10:
            self.collector.set_piped_input(piped_input)
            # 有管道输入时直接处理（不保存到会话历史）
            self._single_mode(piped_input, save_to_session=False)
            return

        # 根据参数选择模式
        if args.gui:
            self._launch_gui()
        elif args.message:
            # 将 message 列表转换为字符串
            message = " ".join(args.message) if isinstance(args.message, list) else args.message
            self._single_mode(message, save_to_session=True)
        elif is_interactive:
            # 交互式终端，显示主菜单
            self._main_menu()
        else:
            # 非交互式，显示帮助
            print("请提供消息或使用交互模式")
            print("使用示例:")
            print("  ai \"你好\"")
            print("  ai --gui")

    def _main_menu(self):
        """主菜单"""
        while True:
            self.ui.print_menu([
                "命令行模式 - 直接与 AI 对话",
                "UI 模式 - 启动图形界面",
                "清空会话历史",
            ], "Terminal AI - 主菜单")

            choice = input(self.ui.color("请选择 [0-3]: ", 'yellow')).strip()

            if choice == '0':
                self.ui.print_info("再见！")
                break
            elif choice == '1':
                self._interactive_mode()
            elif choice == '2':
                self._launch_gui()
            elif choice == '3':
                self.session.clear_history()
                self.ui.print_success("会话历史已清空")
            else:
                self.ui.print_error("无效选择，请重新输入")

    def _interactive_mode(self):
        """交互式对话模式"""
        self.ui.print_header("命令行模式")
        self.ui.print_info("输入 'quit' 或 'exit' 退出，输入 'menu' 返回主菜单，输入 'clear' 清空历史")

        while True:
            try:
                user_input = input(self.ui.color("\n你: ", 'yellow')).strip()

                if not user_input:
                    continue

                if user_input.lower() in ("quit", "exit", "q"):
                    self.ui.print_info("退出命令行模式")
                    break
                elif user_input.lower() == "menu":
                    return
                elif user_input.lower() == "clear":
                    self.session.clear_history()
                    self.ui.print_success("会话历史已清空")
                    continue

                self.ui.print_ai_label()
                self._send_and_display(user_input, save_to_session=True)

            except KeyboardInterrupt:
                print()
                self.ui.print_info("退出命令行模式")
                break
            except EOFError:
                print()
                self.ui.print_info("退出命令行模式")
                break

    def _single_mode(self, message: str, save_to_session: bool = True):
        """单次命令模式"""
        # 检查用户输入是否为安全命令
        if self._is_safe_command(message):
            # 执行命令并获取结果
            success, output = self._execute_command(message)
            command_context = self._format_command_context(message, success, output)

            # 保存用户消息到会话历史
            if save_to_session:
                self.session.add_message("user", message)

            # 构建消息列表：历史对话 + 当前消息
            messages = self.session.get_context_messages()
            if not messages or messages[-1]["role"] != "user":
                messages.append({"role": "user", "content": message})

            # 添加命令上下文作为系统消息
            messages.insert(0, {
                "role": "system",
                "content": f"以下是用户执行的命令及其输出结果：\n{command_context}\n\n请基于这些信息回答用户的问题。"
            })

            # 添加常规上下文信息（当前目录、文件列表、shell 历史）
            context = self.collector.collect() if self.collector else ""
            if context:
                messages.insert(1, {
                    "role": "system",
                    "content": f"以下是当前的上下文信息：\n{context}\n"
                })

            # 发送给 AI
            self.ui.print_ai_label()
            response = ""
            for chunk in self.client.chat_with_messages(messages):
                response += chunk
                print(chunk, end="", flush=True)
            print()  # 换行

            # 保存 AI 响应到会话历史
            if save_to_session and response:
                self.session.add_message("assistant", response)
        else:
            # 检查是否可能是命令（即使不在白名单中）
            parts = message.strip().split()
            if parts and self._is_potential_command(parts[0]):
                # 询问用户是否信任此命令
                if self._ask_trust_command(message):
                    # 用户选择信任，执行命令
                    success, output = self._execute_command(message)
                    command_context = self._format_command_context(message, success, output)

                    # 保存用户消息到会话历史
                    if save_to_session:
                        self.session.add_message("user", message)

                    # 构建消息列表：历史对话 + 当前消息
                    messages = self.session.get_context_messages()
                    if not messages or messages[-1]["role"] != "user":
                        messages.append({"role": "user", "content": message})

                    # 添加命令上下文作为系统消息
                    messages.insert(0, {
                        "role": "system",
                        "content": f"以下是用户执行的命令及其输出结果：\n{command_context}\n\n请基于这些信息回答用户的问题。"
                    })

                    # 添加常规上下文信息（当前目录、文件列表、shell 历史）
                    context = self.collector.collect() if self.collector else ""
                    if context:
                        messages.insert(1, {
                            "role": "system",
                            "content": f"以下是当前的上下文信息：\n{context}\n"
                        })

                    # 发送给 AI
                    self.ui.print_ai_label()
                    response = ""
                    for chunk in self.client.chat_with_messages(messages):
                        response += chunk
                        print(chunk, end="", flush=True)
                    print()  # 换行

                    # 保存 AI 响应到会话历史
                    if save_to_session and response:
                        self.session.add_message("assistant", response)
                else:
                    # 用户选择不信任，作为问题处理
                    self.ui.print_ai_label()
                    self._send_and_display(message, save_to_session=save_to_session)
            else:
                # 不是命令，直接作为问题处理
                self.ui.print_ai_label()
                self._send_and_display(message, save_to_session=save_to_session)

    def _is_potential_command(self, cmd: str) -> bool:
        """检查是否可能是命令（检查命令是否存在）"""
        try:
            result = subprocess.run(
                ['bash', '-c', f'type {cmd}'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def _launch_gui(self):
        """启动 GUI"""
        self.ui.print_info("正在启动 GUI...")
        try:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.abspath(__file__))
            gui_script = os.path.join(project_root, "run.py")

            if os.path.exists(gui_script):
                # 在后台启动 GUI
                subprocess.Popen([sys.executable, gui_script],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                self.ui.print_success("GUI 已启动")
            else:
                self.ui.print_error("找不到 GUI 启动脚本")
        except Exception as e:
            self.ui.print_error(f"启动 GUI 失败: {e}")

    def _send_and_display(self, message: str, save_to_session: bool = True):
        """发送消息并显示响应"""
        # 保存用户消息到会话历史
        if save_to_session:
            self.session.add_message("user", message)

        # 构建消息列表：历史对话 + 当前消息
        messages = self.session.get_context_messages()
        if not messages or messages[-1]["role"] != "user":
            messages.append({"role": "user", "content": message})

        # 添加上下文信息（当前目录、文件列表、shell 历史）
        context = self.collector.collect() if self.collector else ""
        if context:
            # 将上下文作为系统消息添加
            messages.insert(0, {
                "role": "system",
                "content": f"以下是当前的上下文信息：\n{context}\n请基于这些信息回答用户的问题。"
            })

        response = ""
        for chunk in self.client.chat_with_messages(messages):
            response += chunk
            print(chunk, end="", flush=True)
        print()  # 换行

        # 保存 AI 响应到会话历史
        if save_to_session and response:
            self.session.add_message("assistant", response)

    def _read_piped_input(self) -> Optional[str]:
        """读取管道输入"""
        if not sys.stdin.isatty():
            return sys.stdin.read()
        return None


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="终端 AI 助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  ai                    # 显示主菜单
  ai "解释这个错误"      # 单次提问（保存到会话历史）
  make 2>&1 | ai        # 管道输入分析（不保存到会话历史）
  ai --gui              # 直接启动 GUI

会话记忆:
  - 交互式模式会自动保存对话历史
  - 单次提问也会保存到会话历史
  - 输入 'clear' 清空会话历史
  - 主菜单中选择 '清空会话历史' 清空所有历史
        """
    )

    parser.add_argument(
        "message",
        nargs="*",
        help="要发送给 AI 的消息"
    )

    parser.add_argument(
        "-g", "--gui",
        action="store_true",
        help="直接启动 GUI 模式"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="terminal-ai 2.1.0"
    )

    args = parser.parse_args()

    cli = AICLI()
    cli.run(args)


if __name__ == "__main__":
    main()
