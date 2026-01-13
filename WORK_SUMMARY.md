# Terminal AI 项目 - 工作总结

> 本文档总结了 Terminal AI 项目的开发过程、问题解决和最终成果
>
> 项目完成时间: 2026-01-13

---

## 一、项目概述

### 1.1 项目目标

开发一个在终端中使用的 AI 助手，支持：
- 交互式对话和单次提问
- 自动读取 shell 历史命令
- 通过管道分析命令输出和错误
- 兼容 OpenAI API 的服务
- 提供 PyQt 图形界面管理 API 配置

### 1.2 项目状态

✅ **项目已完成** - 所有功能正常工作，Shell 历史读取问题已解决

---

## 二、核心问题与解决方案

### 2.1 Shell 历史读取问题

#### 问题描述

用户执行命令后，AI 无法读取刚刚执行的命令：

```bash
$ sadaosd
bash: sadaosd: command not found
$ ai 我刚刚说了什么
AI: 你刚刚说的是：
```
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --break-system-packages
```
```

#### 根本原因分析

1. **当前 shell 是非交互式**
   ```bash
   $ echo $-
   hmtBc    # 缺少 'i' 标志 = 非交互式 shell
   ```

2. **~/.bashrc 的执行流程**
   ```bash
   # ~/.bashrc 第 5-9 行：
   # If not running interactively, don't do anything
   case $- in
       *i*) ;;
         *) return;;  # 非交互式 shell 在这里就返回了
   esac

   # Terminal AI 配置在第 140 行之后，永远不会被执行
   ```

3. **历史功能被禁用**
   - HISTFILE 和 HISTSIZE 都是空的
   - history 功能被禁用 (history off)
   - 命令根本没有被保存到 ~/.bash_history 文件

#### 解决方案

**将 Terminal AI 配置移到 ~/.bashrc 的最前面，在非交互式检查之前**

```bash
# ~/.bashrc 第 1-43 行：
# Terminal AI 配置 - 必须在非交互式检查之前
PROMPT_COMMAND="history -a; $PROMPT_COMMAND"

ai() {
    local HISTFILE="$HOME/.bash_history"
    local HISTSIZE=1000
    local HISTFILESIZE=2000
    shopt -s histappend
    history -a
    /home/idealer/.claude/agentstream/agents/Projectsource/terminal-ai/ai "$@"
}

_ai() {
    local HISTFILE="$HOME/.bash_history"
    local HISTSIZE=1000
    local HISTFILESIZE=2000
    shopt -s histappend
    history -a
    /home/idealer/.claude/agentstream/agents/Projectsource/terminal-ai/_ai "$@"
}

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# ... 其他配置 ...
```

### 2.2 会话历史干扰问题

#### 问题描述

AI 基于旧的对话记录回答，而不是基于当前 shell 历史上下文。

#### 解决方案

清空会话历史文件 `.session_history.json`，让 AI 基于当前 shell 历史上下文回答。

---

## 三、完成的修改

### 3.1 文件修改列表

| 文件 | 修改内容 | 状态 |
|------|---------|------|
| `~/.bashrc` | 将 Terminal AI 配置移到最前面（第 5-43 行） | ✅ 已完成 |
| `install.sh` | 更新为自动将配置添加到最前面 | ✅ 已完成 |
| `README.md` | 添加根本原因说明和故障排除指南 | ✅ 已完成 |
| `fix_summary.md` | 创建完整的修复文档 | ✅ 已完成 |
| `.session_history.json` | 清空旧的对话记录 | ✅ 已完成 |

### 3.2 关键代码修改

#### install.sh 关键部分

```bash
# 检查是否已存在 Terminal AI 配置
if ! grep -q "^# Terminal AI 配置" "$SHELL_RC" 2>/dev/null; then
    echo ""
    echo "重要说明："
    echo "  Terminal AI 配置必须放在 ~/.bashrc 的最前面，"
    echo "  在非交互式检查之前，否则 AI 无法读取 shell 历史。"
    echo ""
    read -p "是否自动将配置添加到 $SHELL_RC 的最前面？(Y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        # 创建临时文件
        TEMP_RC=$(mktemp)

        # 写入 Terminal AI 配置到开头
        cat > "$TEMP_RC" << 'ENDCONFIG'
# Terminal AI 配置 - 必须在非交互式检查之前
PROMPT_COMMAND="history -a; $PROMPT_COMMAND"

ai() {
    local HISTFILE="$HOME/.bash_history"
    local HISTSIZE=1000
    local HISTFILESIZE=2000
    shopt -s histappend
    history -a
    /home/idealer/.claude/agentstream/agents/Projectsource/terminal-ai/ai "$@"
}

_ai() {
    local HISTFILE="$HOME/.bash_history"
    local HISTSIZE=1000
    local HISTFILESIZE=2000
    shopt -s histappend
    history -a
    /home/idealer/.claude/agentstream/agents/Projectsource/terminal-ai/_ai "$@"
}

case $- in *i*) ;; *) return;; esac

ENDCONFIG

        # 追加原有内容（跳过已存在的 Terminal AI 配置）
        grep -v "^# Terminal AI 配置" "$SHELL_RC" | \
        grep -v "^PROMPT_COMMAND" | \
        grep -v "^ai()" | \
        grep -v "^_ai()" | \
        grep -v "^# If not running interactively" | \
        grep -v "^case \$- in" | \
        grep -v "^\s*\*i\*)" | \
        grep -v "^\s*\*) return" | \
        grep -v "^esac" >> "$TEMP_RC" 2>/dev/null || true

        # 备份原文件
        cp "$SHELL_RC" "${SHELL_RC}.backup.$(date +%Y%m%d_%H%M%S)"

        # 替换原文件
        mv "$TEMP_RC" "$SHELL_RC"

        echo "✓ 已将 Terminal AI 配置添加到 $SHELL_RC 的最前面"
    fi
fi
```

#### context.py 关键部分

```python
def _get_shell_history(self) -> str:
    """获取最近的 shell 历史命令"""
    # 优先直接读取历史文件，避免 subprocess 启动新 bash 实例的缓冲问题
    return self._get_history_from_file()

def _get_history_from_file(self) -> str:
    """从历史文件读取命令"""
    history_file = None
    shell = os.getenv("SHELL", "")

    if "zsh" in shell:
        history_file = os.path.expanduser("~/.zsh_history")
    elif "bash" in shell:
        history_file = os.path.expanduser("~/.bash_history")

    if not history_file or not os.path.exists(history_file):
        return "## Shell 历史\n(无历史记录)\n"

    try:
        with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            # 过滤掉时间戳行（以 # 开头的行）和空行
            commands = []
            for line in reversed(lines):
                stripped = line.strip()
                # 跳过空行和时间戳行
                if not stripped or stripped.startswith('#'):
                    continue
                # 跳过 ai 命令本身（避免循环）
                if stripped.startswith('ai ') or stripped == 'ai':
                    continue
                commands.append(stripped)
                # 只获取最近 10 条命令
                if len(commands) >= 10:
                    break

            if commands:
                # 反转回正确顺序
                commands.reverse()
                return "## 最近 Shell 命令\n" + "\n".join(commands) + "\n\n注意：如果命令不存在或拼写错误，shell 会显示 '未找到命令' 错误。\n"
            else:
                return "## Shell 历史\n(无有效命令)\n"
    except Exception:
        return "## Shell 历史\n(无法读取)\n"
```

---

## 四、测试结果

### 4.1 最终测试

```bash
$ where claude
/home/idealer/.local/bin/claude
$ which claude
/home/idealer/.local/bin/claude
$ ai 我刚刚执行了什么
AI: 根据您的 Shell 命令历史，您刚刚执行了：
1. **`where claude`** - 查找 claude 命令的安装位置
2. **`which claude`** - 显示 claude 命令的完整路径
```

✅ **测试通过** - AI 正确返回了刚刚执行的命令

---

## 五、项目文件结构

```
terminal-ai/
├── ai_cli.py              # 主 CLI 入口
├── context.py             # 上下文收集模块
├── ai_client.py           # AI API 客户端
├── config.py              # 配置管理
├── requirements.txt       # 依赖
├── install.sh             # 安装脚本
├── README.md              # 使用说明
├── WORK_SUMMARY.md        # 工作总结（本文件）
├── fix_summary.md         # 修复文档
├── diagnose_history.sh    # 诊断脚本
├── ai                     # 可执行脚本
├── _ai                    # 可执行脚本
├── run.py                 # GUI 启动脚本
├── test_gui.py            # GUI 测试脚本
└── gui/                   # 图形界面
    ├── main.py            # 主窗口
    ├── config_manager.py  # 配置管理
    ├── api_tester.py      # API 测试
    ├── history.py         # 历史记录
    ├── stats.py           # 使用统计
    └── data/              # 数据存储
        ├── configs.json   # 配置数据
        ├── history.json   # 历史记录
        └── stats.json     # 统计数据
```

---

## 六、依赖

- Python 3.7+
- openai >= 1.0.0
- PyQt5 >= 5.15.0 (GUI 需要)

---

## 七、使用说明

### 7.1 安装

```bash
cd terminal-ai
chmod +x install.sh
./install.sh
```

### 7.2 配置

```bash
# API 配置 (兼容 OpenAI API 的服务)
export AI_API_KEY="your-api-key"
export AI_API_ENDPOINT="https://your-api-endpoint"
export AI_MODEL="gpt-4"  # 可选，默认 gpt-4
```

### 7.3 使用

```bash
# 交互式模式
ai

# 单次提问
ai "解释这个错误"

# 管道分析
make 2>&1 | ai "分析这些错误"

# GUI 模式
ai --gui
```

---

## 八、常见问题

### 8.1 AI 无法读取刚刚执行的命令

**原因**：`~/.bashrc` 中的 Terminal AI 配置必须在非交互式 shell 检查之前

**解决**：运行安装脚本，它会自动将配置添加到正确位置

### 8.2 必须使用 `ai` 命令

必须使用 `ai` 命令而不是 `python3 ai_cli.py`，因为 `ai` 命令会先保存历史

---

## 九、License

MIT

---

*文档版本: v1.0.0*
*最后更新: 2026-01-13*
*作者: CoderAgent*
