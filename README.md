# Claude Agent SDK Course

Hands-on exercises for the Claude Agent SDK live course for O'Reilly.

## Prerequisites

- Python 3.10+
- Anthropic API key
- Git

## Setup Instructions

### 1. Install uv (Python Package Manager)

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (using pip):**
```bash
pip install uv
```

> **Note:** For detailed installation instructions and troubleshooting, visit the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### 2. Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/sajal2692/claude_agent_sdk_course_code.git
cd claude_agent_sdk_course_code

# Install dependencies
uv sync

# Create environment file
cp .env.example .env
```

### 3. Configure Environment Variables

Edit the `.env` file and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 4. Run Jupyter Notebooks

```bash
# Start Jupyter
uv run jupyter notebook
```

Navigate to the `notebooks/` directory and open the exercise notebooks.

## Project Structure

```
claude_agent_sdk_course_code/
├── notebooks/                         # Jupyter exercise notebooks
│   ├── 01_module1_handson.ipynb      # Module 1: Getting Started
│   ├── 02_module2_handson.ipynb      # Module 2: Deep Dive (coming)
│   └── 03_module3_handson.ipynb      # Module 3: Multi-Agent (coming)
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore file
├── .python-version                    # Python version specification
├── pyproject.toml                     # Project configuration
├── README.md                          # This file
└── uv.lock                            # Dependency lock file
```

## Course Modules

| Module | Duration | Topics |
|--------|----------|--------|
| **Module 1** | 75 min | Introduction to Claude Agent SDK, core concepts, response modes |
| **Module 2** | 90 min | Agent loop, debugging, context management, built-in tools, skills |
| **Module 3** | 75 min | Custom tools, MCP integration, multi-agent systems, production deployment |

## Notebooks Overview

### Module 1: Getting Started
- Create a simple agent with minimal configuration
- Single query vs streaming modes
- Basic tool configuration

### Module 2: Deep Dive (Coming Soon)
- Complete agent loop demonstration
- Context compaction observation
- Built-in tools for practical tasks
- Create your own custom skill

### Module 3: Multi-Agent Systems (Coming Soon)
- Build and integrate custom tools
- MCP server integration
- Multi-agent system with specialized subagents

## Troubleshooting

### Common Issues

1. **uv command not found**
   - Restart your terminal after installing uv
   - On Windows, try using PowerShell instead of Command Prompt
   - Or use `python -m uv` instead of `uv`

2. **Anthropic API errors**
   - Verify your API key is correct in `.env`
   - Check you have sufficient API credits

3. **Import errors**
   - Run `uv sync` to ensure all dependencies are installed
   - Activate the virtual environment: `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)

4. **Jupyter kernel issues**
   - Make sure to run Jupyter via `uv run jupyter notebook`
   - Or install the kernel: `uv run python -m ipykernel install --user --name claude-sdk`

### Getting Help

If you encounter issues:
1. Check the error message carefully
2. Verify all setup steps were completed
3. Ask for help in the course discussion forum

## Resources

- [Claude Agent SDK Documentation](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
