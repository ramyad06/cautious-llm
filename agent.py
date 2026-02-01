import os
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from tools import (
    codebase_search, read_file, write_file, list_files, 
    run_terminal_command, get_directory_tree, grep_search, get_file_outline
)

# --- CONFIGURATION ---
def load_env_file():
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key.strip()] = value.strip().strip("'").strip('"')

load_env_file()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def main():
    # 1. Initialize the LLM
    llm = ChatGroq(
        model_name="llama-3.3-70b-versatile",
        groq_api_key=GROQ_API_KEY,
        temperature=0
    )

    # 2. Define the Tools
    tools = [
        codebase_search, read_file, write_file, list_files, 
        run_terminal_command, get_directory_tree, grep_search, get_file_outline
    ]

    # 3. Create the Agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are an expert Software Engineer agent. "
            "You have access to the codebase through various tools. "
            "Your goal is to help the user understand and modify the code.\n\n"
            "STRATEGY:\n"
            "1. EXPLORE: Always start by using `get_directory_tree` to understand the project structure.\n"
            "2. SEARCH: Use `grep_search` to find specific strings (like variable names or imports) "
            "and `codebase_search` for conceptual questions (like 'how is auth handled?').\n"
            "3. UNDERSTAND: Use `get_file_outline` to see symbols in a file before reading the full content with `read_file`.\n"
            "4. PLAN: Explain your findings and your intended changes before executing.\n"
            "5. EXECUTE: Use `write_file` for changes and `run_terminal_command` for testing.\n\n"
            "Always be precise and verify your work."
        )
    )

    # 4. Interactive Loop
    print("\n🤖 Code Intelligence Agent Online! (Type 'exit' to quit)")
    
    while True:
        query = input("\nYour Request: ")
        if query.lower() in ["exit", "quit", "q"]:
            break
            
        print("Thinking...")
        
        try:
            # The new API expects a messages list in the input
            inputs = {"messages": [{"role": "user", "content": query}]}
            
            # Using invoke for simplicity, but stream is also available
            result = agent.invoke(inputs)
            
            # The result contains the message history, the last message is the answer
            answer = result["messages"][-1].content
            print(f"\nResponse:\n{answer}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()