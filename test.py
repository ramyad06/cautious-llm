from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# 1. Initialize the Embedding Model (CPU Mode to be safe)
print("Loading model...")
embeddings = HuggingFaceEmbeddings(
    model_name="nomic-ai/nomic-embed-text-v1.5",
    model_kwargs={"device": "cpu", "trust_remote_code": True}
)

# 2. Connect to the Database you just built
db = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# 3. Ask a question about YOUR code
# (Change this string to something specific to your project, like "login" or "api")
query = "whats the function of multiply_recursive?"

print(f"\n🔍 Searching for: '{query}'...")
results = db.similarity_search(query, k=3)

# 4. Show the results
if not results:
    print("❌ No results found. The database might be empty.")
else:
    print(f"✅ Found {len(results)} matches!\n")
    for i, doc in enumerate(results):
        source = doc.metadata.get("source", "Unknown")
        preview = doc.page_content[:200].replace("\n", " ") # Show first 200 chars
        print(f"--- Match {i+1} from: {source} ---")
        print(f"Content: {preview}...\n")