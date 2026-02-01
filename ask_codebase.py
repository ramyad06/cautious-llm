import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# --- CONFIGURATION ---
GROQ_API_KEY = "gsk_..." # <--- PASTE YOUR KEY HERE
DB_PATH = "./chroma_db"

def main():
    # 1. Load Memory (Same as before)
    print("Loading memory...")
    embeddings = HuggingFaceEmbeddings(
        model_name="nomic-ai/nomic-embed-text-v1.5",
        model_kwargs={"device": "cpu", "trust_remote_code": True}
    )

    db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    # 2. The Brain (Groq)
    llm = ChatGroq(
        model_name="llama3-8b-8192",
        groq_api_key=GROQ_API_KEY,
        temperature=0
    )

    # 3. The New "LCEL" Architecture 🏗️
    
    # Step A: Define HOW to answer (The Prompt)
    # The new standard uses 'context' and 'input' as keys
    system_prompt = (
        "You are a Senior Software Engineer. "
        "Use the provided code context to answer the user's question. "
        "If you don't know the answer, say so. "
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # Step B: Create the "Answer Chain" (LLM + Prompt)
    # This part just formats documents and sends them to the LLM
    question_answer_chain = create_stuff_documents_chain(llm, prompt)

    # Step C: Create the "Retrieval Chain" (Retriever + Answer Chain)
    # This automatically fetches docs and passes them to Step B
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # 4. The Loop
    print("\n🚀 Modern RAG Agent Ready! (Type 'exit' to quit)")
    
    while True:
        query = input("\nYour Question: ")
        if query.lower() in ["exit", "quit", "q"]:
            break
            
        print("Thinking...")
        
        try:
            # The new invoke syntax expects 'input', not 'query'
            response = rag_chain.invoke({"input": query})
            
            print(f"\nAnswer:\n{response['answer']}")
            
            # Print Sources (New format)
            print("\nSources used:")
            seen_sources = set()
            for doc in response['context']:
                src = doc.metadata.get('source', 'Unknown')
                if src not in seen_sources:
                    print(f"- {src}")
                    seen_sources.add(src)
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()