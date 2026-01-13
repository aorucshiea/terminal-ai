# 终端 AI 助手

一个在终端中使用的 AI 助手，支持读取上下文、分析错误、解释代码等功能。附带 PyQt 图形界面，用于可视化管理 API 配置。

## 功能特性

### CLI 功能
- 🤖 **交互式对话**: 连续提问，保持上下文
- 📋 **上下文感知**: 自动读取当前目录文件、shell 历史
- 🔍 **错误分析**: 通过管道分析命令输出和错误
- ⚡ **快捷调用**: 支持 `/ai` 快捷命令
- 🔌 **兼容 OpenAI API**: 支持任何兼容 OpenAI API 的服务

### GUI 功能
- 📊 **API 测试**: 可视化测试 API 连接和响应
- ⚙️ **配置管理**: 添加、编辑、删除多个 API 配置
- 📜 **历史记录**: 查看所有 API 调用历史
- 📈 **使用统计**: 统计 API 调用次数和 Token 消耗

## 安装

```bash
# 克隆或下载项目
cd terminal-ai

# 运行安装脚本
chmod +x install.sh
./install.sh
```

## 配置

设置环境变量：

```bash
# API 配置 (兼容 OpenAI API 的服务)
export AI_API_KEY="your-api-key"
export AI_API_ENDPOINT="https://your-api-endpoint"
export AI_MODEL="gpt-4"  # 可选，默认 gpt-4
```

**示例配置 (xiaomimimo API):**
```bash
export AI_API_KEY="sk-xxxxxxxxxxxx"
export AI_API_ENDPOINT="https://api.xiaomimimo.com/v1"
export AI_MODEL="mimo-v2-flash"
```

将配置添加到 `~/.bashrc` 或 `~/.zshrc` 使其永久生效。

## 使用方法

### CLI 使用

#### 交互式模式

```bash
ai
```

进入对话模式，可以连续提问。

#### 单次提问

```bash
ai "解释这个错误"
```

#### 管道分析

```bash
make 2>&1 | ai "分析这些错误"
npm run build 2>&1 | ai "构建失败了，帮我看看"
```

#### 包含 shell 历史

```bash
ai --history "我刚才做了什么？"
```

**重要说明**：AI 读取 shell 历史的功能依赖于您的 shell 历史配置。如果 AI 无法读取刚刚执行的命令，请运行诊断脚本：

```bash
/home/idealer/.claude/agentstream/agents/Projectsource/terminal-ai/diagnose_history.sh
```

诊断脚本会检查：
- Shell 类型（交互式/非交互式）
- 历史功能状态
- 历史环境变量配置

**常见问题和解决方案**：

1. **AI 无法读取刚刚执行的命令**
   - **原因**：`~/.bashrc` 中的 Terminal AI 配置必须在非交互式 shell 检查之前
   - **解决**：运行安装脚本，它会自动将配置添加到正确位置
   - **手动修复**：确保 `~/.bashrc` 前几行包含：
     ```bash
     # Terminal AI 配置 - 必须在非交互式检查之前
     PROMPT_COMMAND="history -a; $PROMPT_COMMAND"
     ai() { ... }
     _ai() { ... }
     case $- in *i*) ;; *) return;; esac  # 这行在配置之后
     ```

2. **必须使用 `ai` 命令**
   - 必须使用 `ai` 命令而不是 `python3 ai_cli.py`，因为 `ai` 命令会先保存历史
   - 这是 Bash 的设计限制，无法通过代码完全解决

#### 快捷命令

安装后会自动设置 `/ai` alias：

```bash
/ai "帮我看看这个问题"
```

### GUI 使用

启动图形界面：

```bash
python3 gui/main.py
```

#### 功能模块

1. **API 测试**: 选择配置，输入消息，查看 AI 响应
2. **配置管理**: 添加、编辑、删除 API 配置，设置默认配置
3. **历史记录**: 查看所有 API 调用历史，支持搜索和筛选
4. **使用统计**: 查看 API 调用次数和 Token 消耗统计

## 项目结构

```
terminal-ai/
├── ai_cli.py          # 主 CLI 入口
├── context.py         # 上下文收集模块
├── ai_client.py       # AI API 客户端
├── config.py          # 配置管理
├── requirements.txt   # 依赖
├── install.sh         # 安装脚本
├── README.md          # 使用说明
└── gui/               # 图形界面
    ├── main.py        # 主窗口
    ├── config_manager.py  # 配置管理
    ├── api_tester.py      # API 测试
    ├── history.py         # 历史记录
    ├── stats.py           # 使用统计
    └── data/              # 数据存储
        ├── configs.json   # 配置数据
        ├── history.json   # 历史记录
        └── stats.json     # 统计数据
```

## 依赖

- Python 3.7+
- openai >= 1.0.0
- PyQt5 >= 5.15.0 (GUI 需要)

## 示例

```bash
# 分析错误
python script.py 2>&1 | ai "这个错误是什么原因？"

# 解释命令
ai "解释一下 grep -r 'TODO' . 的作用"

# 代码审查
git diff | ai "帮我审查这些改动"

# 调试
curl -X POST http://api.example.com 2>&1 | ai "请求失败了，分析原因"
```

## License

MIT
