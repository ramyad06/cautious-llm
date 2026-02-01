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


### Technology Stack

- **LangChain**: Agent framework and tool orchestration
- **ChromaDB**: Vector database for embeddings
- **HuggingFace**: Embeddings (nomic-embed-text-v1.5)
- **Groq**: Fast LLM inference
- **FastAPI**: REST API framework
- **Rich**: Terminal UI library
- **Click**: CLI framework