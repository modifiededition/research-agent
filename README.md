# AI Research Agent

An intelligent multi-phase research agent that conducts comprehensive research using web search, academic papers, and document analysis. Built with Google Gemini AI and featuring a beautiful Streamlit interface.

## Features

- **5-Phase Research Workflow:**
  1. **Query Understanding** - Analyzes and clarifies your research question
  2. **Clarification** - Interactive questions for ambiguous queries (human-in-the-loop)
  3. **Research Planning** - Creates multiple research angles
  4. **Execution** - Investigates each angle using AI tools
  5. **Reflection** - Validates research completeness
  6. **Report Synthesis** - Generates comprehensive markdown reports

- **Multi-Source Research** - Web search (Tavily), arXiv papers, URL fetching with JS rendering support
- **Real-Time UI** - See each phase running, tool calls being made, and progress updates
- **Production-Ready** - Proper configuration, error handling, and safety limits

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

Create a `.env` file in the project root:

```bash
# Copy example file
cp .env.example .env

# Edit .env with your API keys (use your favorite editor)
# .env should contain:
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```
## Configuration Options

Edit `.env` to customize behavior:

```bash
# Required
GEMINI_API_KEY=your_key
TAVILY_API_KEY=your_key

# Optional (defaults shown)
GEMINI_MODEL=gemini-3-flash-preview
THINKING_LEVEL=medium
MAX_TOOL_ITERATIONS=20

### 4. Run the Application

**Streamlit Web Interface (Recommended):**
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

**CLI Mode:**
```bash
python main.py
```

## Deployment

### Streamlit Cloud (Recommended)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Production-ready research agent"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Set main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Configure Secrets**
   - In Streamlit Cloud dashboard, go to App Settings → Secrets
   - Add:
   ```toml
   GEMINI_API_KEY = "your_actual_key_here"
   TAVILY_API_KEY = "your_actual_key_here"
   ```
   - Save and restart the app

4. **Share Your App**
   - Your app will be available at: `https://your-app-name.streamlit.app`

## License

MIT License - See LICENSE file for details