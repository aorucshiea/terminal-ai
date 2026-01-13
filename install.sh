#!/bin/bash
# Terminal AI 安装脚本

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo "========================================="
echo "  Terminal AI 安装脚本"
echo "========================================="
echo ""

# 检测 shell 类型
SHELL_RC=""
if [ -n "$ZSH_VERSION" ] || [ -n "$ZSH_NAME" ]; then
    SHELL_RC="$HOME/.zshrc"
    echo "检测到 Zsh shell"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
    echo "检测到 Bash shell"
else
    echo "警告: 无法检测到支持的 shell 类型，默认使用 ~/.bashrc"
    SHELL_RC="$HOME/.bashrc"
fi

echo "Shell 配置文件: $SHELL_RC"
echo ""

# 检查 Python 3
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    echo "请先安装 Python 3"
    exit 1
fi

echo "✓ Python 3 已安装: $(python3 --version)"
echo ""

# 安装依赖
echo "安装 Python 依赖..."
pip3 install openai PyQt5 --quiet || {
    echo "错误: 依赖安装失败"
    exit 1
}
echo "✓ 依赖安装完成"
echo ""

# 检查是否已存在 Terminal AI 配置
echo "配置 shell 命令..."

if grep -q "^# Terminal AI 配置" "$SHELL_RC" 2>/dev/null; then
    echo "✓ Terminal AI 配置已存在于 $SHELL_RC"
else
    # 重要说明
    echo ""
    echo "重要说明："
    echo "  Terminal AI 配置必须放在 ~/.bashrc 的最前面，"
    echo "  在非交互式检查之前，否则 AI 无法读取 shell 历史。"
    echo ""
    echo "  当前 ~/.bashrc 的结构："
    echo "    1. Terminal AI 配置 ← 必须在这里"
    echo "    2. 非交互式 shell 检查"
    echo "    3. 其他配置..."
    echo ""
    read -p "是否自动将配置添加到 $SHELL_RC 的最前面？(Y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        # 创建临时文件
        TEMP_RC=$(mktemp)

        # 写入 Terminal AI 配置到开头
        cat > "$TEMP_RC" << 'ENDCONFIG'
# Terminal AI 配置 - 必须在非交互式检查之前，否则 AI 无法读取历史
# 自动保存历史到文件（每次显示提示符时执行）
PROMPT_COMMAND="history -a; $PROMPT_COMMAND"

# AI 命令
ai() {
    # 临时设置历史配置（确保在 snapshot 环境中也能工作）
    local HISTFILE="$HOME/.bash_history"
    local HISTSIZE=1000
    local HISTFILESIZE=2000
    shopt -s histappend

    # 保存当前 shell 的历史
    history -a

    # 调用 AI
    /home/idealer/.claude/agentstream/agents/Projectsource/terminal-ai/ai "$@"
}

# /ai 命令
_ai() {
    # 临时设置历史配置（确保在 snapshot 环境中也能工作）
    local HISTFILE="$HOME/.bash_history"
    local HISTSIZE=1000
    local HISTFILESIZE=2000
    shopt -s histappend

    # 保存当前 shell 的历史
    history -a

    # 调用 AI
    /home/idealer/.claude/agentstream/agents/Projectsource/terminal-ai/_ai "$@"
}

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

ENDCONFIG

        # 追加原有内容（跳过已存在的 Terminal AI 配置）
        grep -v "^# Terminal AI 配置" "$SHELL_RC" | grep -v "^PROMPT_COMMAND" | grep -v "^ai()" | grep -v "^_ai()" | grep -v "^# If not running interactively" | grep -v "^case \$- in" | grep -v "^\s*\*i\*)" | grep -v "^\s*\*) return" | grep -v "^esac" | grep -v "^# AI 命令" | grep -v "^# /ai 命令" >> "$TEMP_RC" 2>/dev/null || true

        # 备份原文件
        cp "$SHELL_RC" "${SHELL_RC}.backup.$(date +%Y%m%d_%H%M%S)"

        # 替换原文件
        mv "$TEMP_RC" "$SHELL_RC"

        echo "✓ 已将 Terminal AI 配置添加到 $SHELL_RC 的最前面"
        echo "  备份文件已保存为 ${SHELL_RC}.backup.*"
    else
        echo "✗ 跳过自动配置"
        echo "  请手动将以下内容添加到 $SHELL_RC 的最前面："
        echo ""
        cat << 'ENDCONFIG'
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
    fi
fi

# 创建可执行脚本
echo ""
echo "创建可执行脚本..."

# 创建 ai 脚本
cat > "$PROJECT_DIR/ai" << 'EOF'
#!/bin/bash
# Terminal AI 命令行工具
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/ai_cli.py" "$@"
EOF
chmod +x "$PROJECT_DIR/ai"
echo "✓ 已创建 ai 脚本"

# 创建 _ai 脚本
cat > "$PROJECT_DIR/_ai" << 'EOF'
#!/bin/bash
# Terminal AI 命令行工具（带历史保存）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
history -a
python3 "$SCRIPT_DIR/ai_cli.py" "$@"
EOF
chmod +x "$PROJECT_DIR/_ai"
echo "✓ 已创建 _ai 脚本"

echo ""
echo "========================================="
echo "  安装完成！"
echo "========================================="
echo ""
echo "使用方法:"
echo "  1. 重新加载 shell 配置:"
echo "     source $SHELL_RC"
echo ""
echo "  2. 或重新打开终端"
echo ""
echo "  3. 使用命令:"
echo "     ai \"你的问题\"          # 单次提问"
echo "     ai                      # 交互模式"
echo "     ai --gui                # 启动 GUI"
echo ""
echo "注意: ai() 函数会在调用前自动保存 shell 历史，"
echo "      这样 AI 就能读取你刚刚执行的命令。"
echo ""
echo "如果 AI 无法读取刚刚执行的命令，请运行诊断脚本:"
echo "  $PROJECT_DIR/diagnose_history.sh"
echo ""
