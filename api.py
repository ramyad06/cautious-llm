"""
FastAPI Web Service for Code Intelligence Agent

This provides a REST API for the code intelligence agent.
Deploy this to make your agent accessible via HTTP.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil
from pathlib import Path
import tempfile

from tools import (
    codebase_search, read_file, get_directory_tree, 
    grep_search, get_file_outline
)
from create_db import main as create_database

app = FastAPI(
    title="Code Intelligence Agent API",
    description="AI-powered code analysis and search API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    context_size: Optional[int] = 5

class SearchRequest(BaseModel):
    query: str
    path: Optional[str] = "."
    is_regex: Optional[bool] = False

class FileRequest(BaseModel):
    file_path: str

class TreeRequest(BaseModel):
    directory: Optional[str] = "."
    max_depth: Optional[int] = 2

class InitRequest(BaseModel):
    repo_path: str
    db_path: Optional[str] = "./chroma_db"

class QueryResponse(BaseModel):
    success: bool
    results: List[dict]
    message: Optional[str] = None

# Health check
@app.get("/")
async def root():
    return {
        "service": "Code Intelligence Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ask": "/api/ask",
            "search": "/api/search",
            "tree": "/api/tree",
            "outline": "/api/outline",
            "read": "/api/read",
            "init": "/api/init"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_exists = os.path.exists("./chroma_db")
    return {
        "status": "healthy",
        "database_initialized": db_exists,
        "groq_api_configured": bool(os.getenv("GROQ_API_KEY"))
    }

@app.post("/api/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Ask a semantic question about the codebase
    
    Example: {"query": "How does authentication work?"}
    """
    try:
        result = codebase_search.invoke({"query": request.query})
        
        if "Error" in result:
            raise HTTPException(status_code=500, detail=result)
        
        # Parse results
        sections = result.split("--- Source:")
        results = []
        
        for section in sections[1:]:
            if not section.strip():
                continue
            
            lines = section.strip().split("\n", 1)
            source = lines[0].strip().replace("---", "").strip()
            content = lines[1] if len(lines) > 1 else ""
            
            results.append({
                "source": source,
                "content": content
            })
        
        return QueryResponse(
            success=True,
            results=results[:request.context_size],
            message=f"Found {len(results)} matches"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search")
async def search_code(request: SearchRequest):
    """
    Search for exact strings in the codebase using grep
    
    Example: {"query": "def main", "path": "./src"}
    """
    try:
        result = grep_search.invoke({
            "query": request.query,
            "path": request.path,
            "is_regex": request.is_regex
        })
        
        if "No matches found" in result:
            return {
                "success": True,
                "matches": [],
                "message": "No matches found"
            }
        
        # Parse grep output
        lines = result.split("\n")
        matches = [line for line in lines if line.strip() and not line.startswith("Matches:")]
        
        return {
            "success": True,
            "matches": matches,
            "count": len(matches)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tree")
async def get_tree(request: TreeRequest):
    """
    Get directory tree structure
    
    Example: {"directory": "./src", "max_depth": 3}
    """
    try:
        result = get_directory_tree.invoke({
            "directory": request.directory,
            "max_depth": request.max_depth
        })
        
        return {
            "success": True,
            "tree": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/outline")
async def get_outline(request: FileRequest):
    """
    Get outline of classes and functions in a file
    
    Example: {"file_path": "./src/main.py"}
    """
    try:
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        result = get_file_outline.invoke({"file_path": request.file_path})
        
        # Parse outline
        items = []
        for line in result.split("\n"):
            if line.strip() and line.startswith("L"):
                parts = line.split(": ", 1)
                if len(parts) == 2:
                    items.append({
                        "line": parts[0],
                        "definition": parts[1]
                    })
        
        return {
            "success": True,
            "file": request.file_path,
            "outline": items
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/read")
async def read_file_content(request: FileRequest):
    """
    Read the content of a file
    
    Example: {"file_path": "./src/main.py"}
    """
    try:
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        result = read_file.invoke({"file_path": request.file_path})
        
        return {
            "success": True,
            "file": request.file_path,
            "content": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/init")
async def initialize_database(request: InitRequest, background_tasks: BackgroundTasks):
    """
    Initialize vector database for a repository
    
    Example: {"repo_path": "/path/to/repo", "db_path": "./chroma_db"}
    """
    try:
        if not os.path.exists(request.repo_path):
            raise HTTPException(status_code=404, detail="Repository path not found")
        
        # Set environment variables
        os.environ['REPO_PATH'] = request.repo_path
        os.environ['DB_PATH'] = request.db_path
        
        # Run database creation in background
        background_tasks.add_task(create_database)
        
        return {
            "success": True,
            "message": "Database initialization started in background",
            "repo_path": request.repo_path,
            "db_path": request.db_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_repository(file: UploadFile = File(...)):
    """
    Upload a repository as a zip file and initialize database
    """
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, file.filename)
        
        # Save uploaded file
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract zip
        extract_dir = os.path.join(temp_dir, "repo")
        shutil.unpack_archive(zip_path, extract_dir)
        
        # Initialize database
        os.environ['REPO_PATH'] = extract_dir
        os.environ['DB_PATH'] = "./chroma_db"
        create_database()
        
        return {
            "success": True,
            "message": "Repository uploaded and indexed successfully",
            "temp_path": extract_dir
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Load environment variables
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key.strip()] = value.strip().strip("'").strip('"')
    
    uvicorn.run(app, host="0.0.0.0", port=8000)