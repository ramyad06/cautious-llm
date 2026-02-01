import os
import subprocess
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# --- CONFIGURATION ---
DB_PATH = "./chroma_db"

# Initialize embeddings once to share across searches
embeddings = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={"device": "cpu", "trust_remote_code": True}
)

@tool
def get_directory_tree(directory: str = ".", max_depth: int = 2) -> str:
    """Get a visual tree representation of the directory structure.
    Use this first to understand the layout before searching or reading files.
    """
    try:
        output = []
        def _build_tree(path, depth):
            if depth > max_depth:
                return
            indent = "  " * depth
            try:
                items = sorted(os.listdir(path))
            except PermissionError:
                return
            for item in items:
                if item.startswith(".") or item == "__pycache__":
                    continue
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    output.append(f"{indent}📁 {item}/")
                    _build_tree(full_path, depth + 1)
                else:
                    output.append(f"{indent}📄 {item}")
        
        output.append(f"Project Root: {directory}")
        _build_tree(directory, 0)
        return "\n".join(output)
    except Exception as e:
        return f"Error building tree: {e}"

@tool
def grep_search(query: str, path: str = ".", is_regex: bool = False) -> str:
    """Exact string or regex search in files using 'grep'.
    More reliable than codebase_search for finding specific variable names or function calls.
    """
    try:
        flag = "-rnE" if is_regex else "-rn"
        # Avoid searching .git and .venv
        command = f"grep {flag} --exclude-dir={{.git,.venv,chroma_db}} '{query}' {path}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if not result.stdout and not result.stderr:
            return "No matches found."
        return f"Matches:\n{result.stdout}\n{result.stderr}"
    except Exception as e:
        return f"Error running grep: {e}"

@tool
def get_file_outline(file_path: str) -> str:
    """Return an outline of classes and functions in a Python file.
    Use this to quickly see what's inside a file without reading the whole thing.
    """
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
        
        outline = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("def ") or stripped.startswith("class "):
                outline.append(f"L{i+1}: {stripped}")
        
        if not outline:
            return "No classes or functions found."
        return "\n".join(outline)
    except Exception as e:
        return f"Error getting outline: {e}"

@tool
def codebase_search(query: str) -> str:
    """Semantic search on the codebase using embeddings.
    Best for conceptual questions like 'How is database initialization handled?'.
    Use grep_search for finding specific strings like 'BATCH_SIZE'.
    """
    if not os.path.exists(DB_PATH):
        return "Error: Database not found. Please run create_db.py first."
    
    db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    results = db.similarity_search(query, k=5)
    
    output = []
    for doc in results:
        source = doc.metadata.get("source", "Unknown")
        output.append(f"--- Source: {source} ---\n{doc.page_content}\n")
    
    return "\n".join(output)

@tool
def read_file(file_path: str) -> str:
    """Read the content of a file from the local filesystem."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

@tool
def write_file(file_path: str, content: str) -> str:
    """Write content to a file on the local filesystem."""
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"

@tool
def list_files(directory: str = ".") -> str:
    """List files in a directory. Use get_directory_tree for a better overview."""
    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {e}"

@tool
def run_terminal_command(command: str) -> str:
    """Run a terminal command and return the output."""
    try:
        # For security, we might want to restrict commands, but for this agent we'll allow it.
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Error running command: {e}"