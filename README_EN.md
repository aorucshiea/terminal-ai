# Terminal AI Assistant

An AI assistant for terminal usage with context awareness, error analysis, and code explanation capabilities. Includes a PyQt GUI for visual API configuration management.

## Features

### CLI Features
- 🤖 **Interactive Chat**: Continuous questioning with context retention
- 📋 **Context Awareness**: Automatically reads current directory files and shell history
- 🔍 **Error Analysis**: Analyze command output and errors via pipes
- ⚡ **Quick Access**: Supports `/ai` shortcut command
- 🔌 **OpenAI API Compatible**: Works with any OpenAI API compatible service
- 🛡️ **Command Trust Management**: Dynamically add trusted commands with CLI and GUI support

### GUI Features
- 📊 **API Testing**: Visual API connection and response testing
- ⚙️ **Configuration Management**: Add, edit, and delete multiple API configurations
- 🛡️ **Command Management**: Manage trusted command whitelist
- 📜 **History**: View all API call history
- 📈 **Statistics**: Track API call counts and token usage

## Installation

```bash
# Clone or download the project
cd terminal-ai

# Run the installation script
chmod +x install.sh
./install.sh
```

## Configuration

Set environment variables:

```bash
# API Configuration (OpenAI API compatible services)
export AI_API_KEY="your-api-key"
export AI_API_ENDPOINT="https://your-api-endpoint"
export AI_MODEL="gpt-4"  # Optional, default is gpt-4
```

**Example Configuration (xiaomimimo API):**
```bash
export AI_API_KEY="sk-xxxxxxxxxxxx"
export AI_API_ENDPOINT="https://api.xiaomimimo.com/v1"
export AI_MODEL="mimo-v2-flash"
```

Add the configuration to `~/.bashrc` or `~/.zshrc` to make it permanent.

## Usage

### CLI Usage

#### Interactive Mode

```bash
ai
```

Enter conversation mode for continuous questioning.

#### Single Question

```bash
ai "Explain this error"
```

#### Pipe Analysis

```bash
make 2>&1 | ai "Analyze these errors"
npm run build 2>&1 | ai "Build failed, help me check"
```

#### Smart Command Execution

When using the `ai` command, if the input is a shell command, the system will automatically execute it and pass the output to AI:

```bash
ai ls                    # Execute ls command, AI answers based on output
ai which claude          # Execute which claude, AI answers based on output
ai cd /                 # Execute cd /, AI answers based on output
ai "Hello, who are you"  # Not a command, sent directly as a question to AI
```

For commands not in the safe whitelist, the system will ask if you trust them:
- `y` - Temporarily trust and execute
- `a` - Permanently trust and execute
- `n` - Don't trust, send as a question to AI

#### Include Shell History

```bash
ai --history "What did I just do?"
```

**Important Note**: The shell history reading feature depends on your shell history configuration. If AI cannot read recently executed commands, run the diagnostic script:

```bash
/home/idealer/.claude/agentstream/agents/Projectsource/terminal-ai/diagnose_history.sh
```

The diagnostic script checks:
- Shell type (interactive/non-interactive)
- History function status
- History environment variable configuration

**Common Issues and Solutions**:

1. **AI cannot read recently executed commands**
   - **Cause**: Terminal AI configuration in `~/.bashrc` must be before the non-interactive shell check
   - **Solution**: Run the installation script, it will automatically add the configuration to the correct location
   - **Manual Fix**: Ensure the first few lines of `~/.bashrc` contain:
     ```bash
     # Terminal AI configuration - must be before non-interactive check
     PROMPT_COMMAND="history -a; $PROMPT_COMMAND"
     ai() { ... }
     _ai() { ... }
     case $- in *i*) ;; *) return;; esac  # This line comes after the configuration
     ```

2. **Must use the `ai` command**
   - You must use the `ai` command instead of `python3 ai_cli.py`, because the `ai` command saves history first
   - This is a Bash design limitation that cannot be fully solved by code

#### Quick Command

After installation, the `/ai` alias is automatically set up:

```bash
/ai "Help me with this problem"
```

### GUI Usage

Launch the graphical interface:

```bash
ai --gui
```

Or

```bash
python3 gui/main.py
```

#### Feature Modules

1. **API Testing**: Select configuration, input message, view AI response
2. **Configuration Management**: Add, edit, delete API configurations, set default configuration
3. **Command Management**: Manage trusted command whitelist, add/remove/clear commands
4. **History**: View all API call history with search and filtering
5. **Statistics**: View API call counts and token usage statistics

## Project Structure

```
terminal-ai/
├── ai_cli.py              # Main CLI entry point
├── context.py             # Context collection module
├── ai_client.py           # AI API client
├── config.py              # Configuration management
├── command_config.py      # Command configuration management
├── requirements.txt       # Dependencies
├── install.sh             # Installation script
├── README.md              # Usage documentation (Chinese)
├── README_EN.md           # Usage documentation (English)
├── ai, _ai                # Executable scripts
├── run.py                 # GUI launch script
└── gui/                   # Graphical interface
    ├── main.py            # Main window
    ├── config_manager.py  # Configuration management
    ├── api_tester.py      # API testing
    ├── command_manager.py # Command management
    ├── history.py         # History
    ├── stats.py           # Statistics
    └── data/              # Data storage
        ├── configs.json   # Configuration data
        ├── history.json   # History records
        └── stats.json     # Statistics data
```

## Dependencies

- Python 3.7+
- openai >= 1.0.0
- PyQt5 >= 5.15.0 (for GUI)

## Examples

```bash
# Analyze errors
python script.py 2>&1 | ai "What's the cause of this error?"

# Explain commands
ai "Explain what grep -r 'TODO' . does"

# Code review
git diff | ai "Help me review these changes"

# Debugging
curl -X POST http://api.example.com 2>&1 | ai "Request failed, analyze the cause"

# Execute commands and let AI analyze
ai ls -la
ai git status
```

## License

MIT
