# Cautious-LLM 🤖

An AI-powered code intelligence agent that helps you understand, search, and analyze codebases using natural language. Built with LangChain, ChromaDB, and Groq's LLM APIs.

## 🌟 Features

- **Semantic Code Search**: Ask questions about your codebase in natural language
- **Vector Database**: Powered by ChromaDB with HuggingFace embeddings for intelligent code retrieval
- **Multiple Interfaces**:
  - Interactive CLI tool with rich formatting
  - Python agent with conversational interface
  - REST API for integration with other tools
- **Advanced Search Tools**:
  - Semantic search for conceptual questions
  - Exact string/regex search (grep)
  - Directory tree visualization
  - File outline generation
  - Direct file operations (read/write)
- **Multi-Language Support**: Python, JavaScript, TypeScript, HTML, CSS, Markdown, JSON, YAML

## 📋 Prerequisites

- Python 3.9 or higher
- Virtual environment (venv)
- Groq API key ([Get one here](https://console.groq.com/))

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd cautious-llm

# Run the installation script
chmod +x install.sh
./install.sh
```

Or install manually:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your API key:

```bash
GROQ_API_KEY=your_groq_api_key_here
REPO_PATH=./test-project
DB_PATH=./chroma_db
BATCH_SIZE=50
```

### 3. Initialize Database

Index your codebase to create the vector database:

```bash
# Using CLI
python3 cli.py init --path ./your-project

# Or directly
python3 create_db.py
```

### 4. Start Using

**Interactive Agent:**
```bash
./run_agent.sh
# or
python3 agent.py
```

**CLI Tool:**
```bash
# Ask questions
python3 cli.py ask "How does authentication work?"

# Search for strings
python3 cli.py search "def main" --path ./src

# View project structure
python3 cli.py tree --max-depth 3

# Review code files
python3 cli.py review ./src/main.py
```

**API Server:**
```bash
python3 api.py
# Navigate to http://localhost:8000 for API documentation
```

## 📚 Usage Examples

### Semantic Search
```bash
python3 cli.py ask "Where is the database initialized?"
```

### Exact String Search
```bash
python3 cli.py search "BATCH_SIZE" --regex
```

### Interactive Agent
```bash
python3 agent.py
> Your Request: Show me all the API endpoints
> Your Request: Explain how the vector database works
```

### API Usage
```bash
# Ask a question
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "How does the agent work?"}'

# Search code
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "def main", "path": "."}'
```

## 🛠️ Architecture

### Core Components

1. **create_db.py**: Indexes codebase and creates vector database
   - Scans multiple file types (.py, .js, .ts, .html, .md, etc.)
   - Splits code into chunks with overlap
   - Generates embeddings using nomic-ai model
   - Stores in ChromaDB with batch processing

2. **agent.py**: Interactive conversational agent
   - Uses LangChain's agent framework
   - Equipped with 8 tools for code exploration
   - Powered by Groq's llama-3.3-70b-versatile model

3. **cli.py**: Rich command-line interface
   - Beautiful output formatting with Rich library
   - Subcommands: init, ask, search, tree, review
   - Progress indicators and error handling

4. **api.py**: FastAPI REST service
   - RESTful endpoints for all functionality
   - CORS enabled for web integration
   - Pydantic models for validation
   - Health check and status endpoints

5. **tools.py**: Core functionality as LangChain tools
   - `codebase_search`: Semantic search using embeddings
   - `grep_search`: Exact string/regex search
   - `get_directory_tree`: Visual tree structure
   - `get_file_outline`: Class/function extraction
   - `read_file`, `write_file`: File operations
   - `run_terminal_command`: Execute shell commands

6. **ask_codebase.py**: Simple RAG (Retrieval-Augmented Generation) example
   - Demonstrates basic Q&A over codebase
   - Uses retrieval chain pattern

### Technology Stack

- **LangChain**: Agent framework and tool orchestration
- **ChromaDB**: Vector database for embeddings
- **HuggingFace**: Embeddings (nomic-embed-text-v1.5)
- **Groq**: Fast LLM inference
- **FastAPI**: REST API framework
- **Rich**: Terminal UI library
- **Click**: CLI framework

## 📁 Project Structure

```
cautious-llm/
├── agent.py              # Interactive agent with tools
├── api.py               # FastAPI REST service
├── ask_codebase.py      # Simple RAG example
├── cli.py               # Rich CLI interface
├── create_db.py         # Database initialization
├── tools.py             # LangChain tool definitions
├── test.py              # Database testing script
├── requirements.txt     # Python dependencies
├── setup.py             # Package setup
├── install.sh           # Installation script
├── run_agent.sh         # Agent launcher
└── chroma_db/           # Vector database storage
```

## 🔧 Configuration Options

### Environment Variables

- `GROQ_API_KEY`: Your Groq API key (required)
- `REPO_PATH`: Path to codebase for indexing (default: ./test-project)
- `DB_PATH`: Vector database location (default: ./chroma_db)
- `BATCH_SIZE`: Batch size for embedding (default: 50)

### Customization

Edit the tool configurations in `tools.py` or adjust the agent's system prompt in `agent.py` to customize behavior.

## 🧪 Testing

Test the vector database:
```bash
python3 test.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Powered by [Groq](https://groq.com/)
- Embeddings by [Nomic AI](https://www.nomic.ai/)

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

**Made with ❤️ by Ayush**
