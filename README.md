# AI Research Agent

A multi-phase research agent **built from scratch in Python** with no orchestration frameworks. Implements key agentic design patterns—**planning**, **tool use**, and **reflection**.

**Key Highlights**:
- 🎯 **Planning Pattern** - Decomposes queries into focused research angles
- 🔧 **Tool Use Pattern** - Multi-turn function calling with web search, arXiv, and URL fetching
- 🔄 **Reflection Pattern** - Self-validates completeness and loops back if needed
- 👤 **Human-in-the-Loop** - Interactive clarification when queries are ambiguous
- 💻 **Real-Time UI** - Beautiful Streamlit interface with live progress tracking

## Architecture

### 5-Phase Research Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│  User Query                                                         │
└────────────────────────────┬────────────────────────────────────────┘
                             ↓
                    ┌─────────────────────┐
                    │  Phase 1:           │
                    │  Understanding      │
                    │  Query              │
                    └──────────┬──────────┘
                               ↓
                      ┌────────┴─────────┐
                      │ Needs            │
                      │ Clarification?   │
                      └────┬─────────┬───┘
                       YES │         │ NO
                           ↓         ↓
                  ┌────────────┐    │
                  │  Phase 1.1:│    │
                  │  Human-in- │    │
                  │  the-Loop  │    │
                  │  Clarify   │    │
                  └──────┬─────┘    │
                         ↓          │
                    ┌────┴──────────┘
                    ↓
           ┌─────────────────────┐
           │  Phase 2:           │
           │  Research Planning  │
           │  (3-6 angles)       │
           └──────────┬──────────┘
                      ↓
           ┌─────────────────────┐
           │  Phase 3:           │◄──────────┐
           │  Research Execution │           │
           │  (Tool Calling Loop)│           │
           └──────────┬──────────┘           │
                      ↓                      │
           ┌─────────────────────┐           │
           │  Phase 4:           │           │
           │  Reflection &       │           │
           │  Validation         │           │
           └──────────┬──────────┘           │
                      ↓                      │
              ┌───────┴────────┐             │
              │ Is Research    │             │
              │ Sufficient?    │             │
              └───┬────────┬───┘             │
              YES │        │ NO              │
                  │        └─────────────────┘
                  │          Generate new angles
                  ↓
           ┌─────────────────────┐
           │  Phase 5:           │
           │  Final Report       │
           │  Synthesis          │
           └──────────┬──────────┘
                      ↓
              ┌──────────────┐
              │  Markdown    │
              │  Report      │
              └──────────────┘
```

## Quick Start

### 1. Prerequisites

- Python 3.13+
- API Keys:
  - [Google Gemini API](https://aistudio.google.com/apikey)
  - [Tavily API](https://tavily.com/)

### 2. Installation

```bash
# Clone or download the repository
cd research_agent

# Install dependencies
pip install -r requirements.txt
# or with uv
uv sync
```

### 3. Configuration

**Note**: The `.env` file is **optional**. You can also export API keys as environment variables directly.

**Option 1: Using .env file**

Create a `.env` file in the project root:

```bash
# Copy example file
cp .env.example .env

# Edit .env with your API keys
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

**Option 2: Using environment variables (no .env file needed)**

```bash
export GEMINI_API_KEY=your_gemini_api_key_here
export TAVILY_API_KEY=your_tavily_api_key_here
```

Both approaches work identically. The application will use environment variables if no `.env` file exists.

#### Configuration Options

Edit `.env` or export environment variables to customize behavior:

```bash
# Required
GEMINI_API_KEY=your_key
TAVILY_API_KEY=your_key

# Optional (defaults shown)
GEMINI_MODEL=gemini-3-flash-preview
THINKING_LEVEL=medium
MAX_TOOL_ITERATIONS=20
```

### 4. Run the Application

**Streamlit Web Interface (Recommended):**
```bash
# With .env file:
streamlit run streamlit_app.py

# Or with environment variables:
GEMINI_API_KEY=your_key TAVILY_API_KEY=your_key streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

**CLI Mode:**
```bash
# With .env file:
python main.py

# Or with environment variables:
GEMINI_API_KEY=your_key TAVILY_API_KEY=your_key python main.py
```

## License

MIT License - See LICENSE file for details