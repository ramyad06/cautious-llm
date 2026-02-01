#!/usr/bin/env python3
"""
Code Intelligence Agent - Enhanced CLI Tool
"""
import click
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown
from rich.panel import Panel

# Import existing modules
from create_db import main as create_database
from tools import (
    codebase_search, read_file, write_file, list_files,
    run_terminal_command, get_directory_tree, grep_search, get_file_outline
)

console = Console()

def load_env_file():
    """Load environment variables from .env file"""
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key.strip()] = value.strip().strip("'").strip('"')

load_env_file()

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    🤖 Code Intelligence Agent - Your AI-powered coding assistant
    
    Use this tool to analyze, search, and understand your codebase using AI.
    """
    pass

@cli.command()
@click.option('--path', default='./test-project', help='Path to the project directory')
@click.option('--db-path', default='./chroma_db', help='Path to store the vector database')
@click.option('--batch-size', default=50, help='Batch size for processing')
def init(path, db_path, batch_size):
    """
    Initialize vector database for a project
    
    This will scan your codebase and create a searchable vector database.
    """
    console.print(Panel.fit(
        f"🔧 Initializing database for [bold cyan]{path}[/bold cyan]",
        title="Database Initialization"
    ))
    
    # Update environment variables
    os.environ['REPO_PATH'] = path
    os.environ['DB_PATH'] = db_path
    os.environ['BATCH_SIZE'] = str(batch_size)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing files...", total=None)
        try:
            create_database()
            progress.update(task, completed=True)
            console.print("✅ [bold green]Database initialized successfully![/bold green]")
        except Exception as e:
            console.print(f"❌ [bold red]Error:[/bold red] {e}")
            sys.exit(1)

@cli.command()
@click.argument('question')
@click.option('--context', default=5, help='Number of context chunks to retrieve')
@click.option('--show-sources', is_flag=True, help='Show source files')
def ask(question, context, show_sources):
    """
    Ask a question about the codebase
    
    Example: code-agent ask "How does authentication work?"
    """
    console.print(f"\n🔍 [bold]Searching for:[/bold] {question}\n")
    
    try:
        # Use codebase_search tool
        result = codebase_search.invoke({"query": question})
        
        if "Error" in result:
            console.print(f"❌ [bold red]{result}[/bold red]")
            console.print("\n💡 [yellow]Tip:[/yellow] Run 'code-agent init' first to create the database")
            sys.exit(1)
        
        # Parse and display results
        sections = result.split("--- Source:")
        
        for i, section in enumerate(sections[1:], 1):
            if not section.strip():
                continue
                
            lines = section.strip().split("\n", 1)
            source = lines[0].strip().replace("---", "").strip()
            content = lines[1] if len(lines) > 1 else ""
            
            if show_sources:
                console.print(f"\n[bold cyan]📄 Source {i}:[/bold cyan] {source}")
            
            # Display content in a panel
            console.print(Panel(
                content[:500] + ("..." if len(content) > 500 else ""),
                title=f"Match {i}",
                border_style="green"
            ))
            
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.argument('file_path')
@click.option('--type', type=click.Choice(['security', 'performance', 'style', 'all']), default='all')
def review(file_path, type):
    """
    Review a code file for issues
    
    Example: code-agent review ./src/main.py --type security
    """
    console.print(f"\n📝 [bold]Reviewing:[/bold] {file_path}\n")
    
    if not os.path.exists(file_path):
        console.print(f"❌ [bold red]File not found:[/bold red] {file_path}")
        sys.exit(1)
    
    try:
        # Read file content
        content = read_file.invoke({"file_path": file_path})
        
        # Get file outline
        outline = get_file_outline.invoke({"file_path": file_path})
        
        console.print("[bold cyan]File Outline:[/bold cyan]")
        console.print(outline)
        
        console.print(f"\n[bold cyan]Review Type:[/bold cyan] {type}")
        console.print("\n💡 [yellow]Note:[/yellow] Full AI-powered review coming soon!")
        console.print("For now, here's the file structure and content preview.\n")
        
        # Show first 20 lines
        lines = content.split("\n")[:20]
        console.print(Panel(
            "\n".join(lines),
            title="File Preview (first 20 lines)",
            border_style="blue"
        ))
        
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.option('--path', default='.', help='Directory to analyze')
@click.option('--max-depth', default=2, help='Maximum depth to traverse')
def tree(path, max_depth):
    """
    Display project directory tree
    
    Example: code-agent tree --path ./src --max-depth 3
    """
    console.print(f"\n📁 [bold]Project Structure:[/bold] {path}\n")
    
    try:
        result = get_directory_tree.invoke({
            "directory": path,
            "max_depth": max_depth
        })
        console.print(result)
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.argument('query')
@click.option('--path', default='.', help='Path to search in')
@click.option('--regex', is_flag=True, help='Use regex pattern')
def search(query, path, regex):
    """
    Search for exact strings in the codebase
    
    Example: code-agent search "def main" --path ./src
    """
    console.print(f"\n🔎 [bold]Searching for:[/bold] '{query}' in {path}\n")
    
    try:
        result = grep_search.invoke({
            "query": query,
            "path": path,
            "is_regex": regex
        })
        
        if "No matches found" in result:
            console.print("❌ [yellow]No matches found[/yellow]")
        else:
            # Parse grep output
            lines = result.split("\n")
            matches = [line for line in lines if line.strip() and not line.startswith("Matches:")]
            
            console.print(f"✅ Found [bold green]{len(matches)}[/bold green] matches:\n")
            
            for match in matches[:20]:  # Show first 20 matches
                console.print(match)
            
            if len(matches) > 20:
                console.print(f"\n... and {len(matches) - 20} more matches")
                
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.argument('file_path')
def outline(file_path):
    """
    Show outline of classes and functions in a file
    
    Example: code-agent outline ./src/agent.py
    """
    console.print(f"\n📋 [bold]File Outline:[/bold] {file_path}\n")
    
    if not os.path.exists(file_path):
        console.print(f"❌ [bold red]File not found:[/bold red] {file_path}")
        sys.exit(1)
    
    try:
        result = get_file_outline.invoke({"file_path": file_path})
        
        # Create a nice table
        table = Table(title=f"Outline: {os.path.basename(file_path)}")
        table.add_column("Line", style="cyan", no_wrap=True)
        table.add_column("Definition", style="green")
        
        for line in result.split("\n"):
            if line.strip():
                parts = line.split(": ", 1)
                if len(parts) == 2:
                    table.add_row(parts[0], parts[1])
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [bold red]Error:[/bold red] {e}")
        sys.exit(1)

@cli.command()
@click.option('--format', type=click.Choice(['markdown', 'html']), default='markdown')
@click.option('--output', default='./docs', help='Output directory')
def docs(format, output):
    """
    Generate project documentation (Coming Soon)
    
    Example: code-agent docs --format markdown --output ./docs
    """
    console.print(f"\n📚 [bold]Generating {format} documentation...[/bold]\n")
    console.print("🚧 [yellow]This feature is under development![/yellow]")
    console.print(f"Documentation will be saved to: {output}")

@cli.command()
@click.option('--metrics', is_flag=True, help='Show code metrics')
@click.option('--duplicates', is_flag=True, help='Find duplicate code')
@click.option('--complexity', is_flag=True, help='Analyze complexity')
def analyze(metrics, duplicates, complexity):
    """
    Analyze codebase quality (Coming Soon)
    
    Example: code-agent analyze --metrics --complexity
    """
    console.print("\n📊 [bold]Analyzing codebase...[/bold]\n")
    console.print("🚧 [yellow]This feature is under development![/yellow]")
    
    if metrics:
        console.print("  • Code metrics analysis")
    if duplicates:
        console.print("  • Duplicate code detection")
    if complexity:
        console.print("  • Complexity analysis")

@cli.command()
def chat():
    """
    Start interactive chat mode
    
    Chat with the AI about your codebase interactively.
    """
    console.print(Panel.fit(
        "🤖 [bold]Code Intelligence Agent - Interactive Mode[/bold]\n"
        "Type your questions and I'll help you understand your codebase.\n"
        "Type 'exit' or 'quit' to leave.",
        border_style="cyan"
    ))
    
    from langchain_groq import ChatGroq
    from langchain.agents import create_agent
    
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        console.print("❌ [bold red]Error:[/bold red] GROQ_API_KEY not found in environment")
        sys.exit(1)
    
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        groq_api_key=GROQ_API_KEY,
        temperature=0
    )
    
    tools = [
        codebase_search, read_file, write_file, list_files,
        run_terminal_command, get_directory_tree, grep_search, get_file_outline
    ]
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are an expert Software Engineer agent. "
            "You have access to the codebase through various tools. "
            "Your goal is to help the user understand and modify the code.\n\n"
            "STRATEGY:\n"
            "1. EXPLORE: Use get_directory_tree to understand project structure.\n"
            "2. SEARCH: Use grep_search for exact strings and codebase_search for concepts.\n"
            "3. UNDERSTAND: Use get_file_outline before reading full files.\n"
            "4. PLAN: Explain findings and intended changes.\n"
            "5. EXECUTE: Use write_file for changes and run_terminal_command for testing.\n\n"
            "Always be precise and verify your work."
        )
    )
    
    while True:
        try:
            query = console.input("\n[bold cyan]You:[/bold cyan] ")
            
            if query.lower() in ["exit", "quit", "q"]:
                console.print("\n👋 [bold]Goodbye![/bold]")
                break
            
            if not query.strip():
                continue
            
            console.print("\n[bold yellow]Agent:[/bold yellow] Thinking...\n")
            
            inputs = {"messages": [{"role": "user", "content": query}]}
            result = agent.invoke(inputs)
            answer = result["messages"][-1].content
            
            # Display response in a nice format
            console.print(Panel(
                Markdown(answer),
                title="Response",
                border_style="green"
            ))
            
        except KeyboardInterrupt:
            console.print("\n\n👋 [bold]Goodbye![/bold]")
            break
        except Exception as e:
            console.print(f"\n❌ [bold red]Error:[/bold red] {e}")

@cli.command()
def info():
    """
    Show system information and configuration
    """
    table = Table(title="Code Intelligence Agent - System Info")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Version", "1.0.0")
    table.add_row("Database Path", os.getenv("DB_PATH", "./chroma_db"))
    table.add_row("Repo Path", os.getenv("REPO_PATH", "./test-project"))
    table.add_row("Groq API Key", "✅ Set" if os.getenv("GROQ_API_KEY") else "❌ Not Set")
    table.add_row("Embedding Model", "nomic-ai/nomic-embed-text-v1.5")
    table.add_row("LLM Model", "llama-3.3-70b-versatile")
    
    console.print(table)

if __name__ == '__main__':
    cli()