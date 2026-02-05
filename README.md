# Claude Agent SDK Course

Hands-on code examples and exercises for the Claude Agent SDK live course for O'Reilly.

This repository contains:
- **Examples**: Step-by-step Jupyter notebooks demonstrating SDK concepts
- **Exercises**: Complete projects that build progressively more complex agent systems

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

## Repository Structure

```
claude_agent_sdk_course_code/
├── code/
│   ├── examples/                      # Demonstration notebooks
│   │   ├── module_1/
│   │   │   └── 01_getting_started.ipynb
│   │   ├── module_2/
│   │   │   ├── 01_session_management.ipynb
│   │   │   ├── 02_hooks.ipynb
│   │   │   └── 03_skills.ipynb
│   │   └── module_3/
│   │       ├── 01_custom_tools.ipynb
│   │       └── 02_multi_agent_systems.ipynb
│   └── exercises/                     # Hands-on projects
│       ├── module_1/
│       │   └── stock_analyzer/        # Notebook-based stock analysis
│       ├── module_2/
│       │   └── stock_analyzer_with_skills/  # CLI with agent skills
│       └── module_3/
│           └── investment_research_system/  # Multi-agent system
├── .env.example
├── pyproject.toml
└── README.md
```

## How to Use This Repository

### Running Examples

Examples are Jupyter notebooks that demonstrate specific SDK concepts:

```bash
# Start Jupyter from the root directory
uv run jupyter notebook

# Navigate to code/examples/module_X/ and open the notebooks
```

**Examples cover:**
- Module 1: Getting started with the SDK
- Module 2: Session management, hooks, and skills
- Module 3: Custom tools and multi-agent systems

### Running Exercises

Exercises are complete, standalone projects. Each exercise has its own README with setup and running instructions:

1. Navigate to the exercise directory:
```bash
cd code/exercises/module_1/stock_analyzer
# or
cd code/exercises/module_2/stock_analyzer_with_skills
# or
cd code/exercises/module_3/investment_research_system
```

2. Follow the README in each exercise directory for:
   - Specific setup instructions
   - How to run the exercise
   - Expected outputs

**Exercises include:**
- **Module 1**: Stock analyzer using Jupyter notebooks (agents write Python code)
- **Module 2**: Stock analyzer CLI with reusable agent skills
- **Module 3**: Multi-agent investment research system with HTML dashboards

## Course Modules

| Module | Duration | Topics | Examples | Exercises |
|--------|----------|--------|----------|-----------|
| **Module 1** | 75 min | Introduction to Claude Agent SDK, core concepts, response modes | Getting started | Stock analyzer (notebook) |
| **Module 2** | 90 min | Agent loop, debugging, context management, built-in tools, skills | Session management, hooks, skills | Stock analyzer with skills (CLI) |
| **Module 3** | 75 min | Custom tools, MCP integration, multi-agent systems | Custom tools, multi-agent systems | Investment research system |

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
