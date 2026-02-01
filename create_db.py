import os
import shutil
import glob
import gc # Garbage Collection
import torch # To clear GPU cache

from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# --- CONFIGURATION ---
REPO_PATH = "/Users/ayush/Projects/Github/Langchain-issues/test-project" 
DB_PATH = "./chroma_db"

# EMERGENCY SETTING: Drastically reduced batch size
BATCH_SIZE = 50

def load_files_manually(extension):
    search_pattern = f"{REPO_PATH}/**/*{extension}"
    file_paths = glob.glob(search_pattern, recursive=True)
    docs = []
    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            if text.strip():
                docs.append(Document(page_content=text, metadata={"source": path}))
        except:
            pass
    return docs

def main():
    # 1. Clear old database
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    all_chunks = []
    
    # 2. Load Files
    file_types = {
        ".py": Language.PYTHON,
        ".js": Language.JS,
        ".ts": Language.TS,
        ".html": Language.HTML,
        ".md": Language.MARKDOWN,
        ".css": None, 
        ".json": None,
        ".yaml": None,
        ".txt": None
    }

    print(f"Scanning {REPO_PATH}...")

    for ext, lang_type in file_types.items():
        docs = load_files_manually(ext)
        if docs:
            if lang_type:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=lang_type, chunk_size=4000, chunk_overlap=400
                )
            else:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=4000, chunk_overlap=400
                )
            chunks = splitter.split_documents(docs)
            all_chunks.extend(chunks)

    if not all_chunks:
        print("No files found.")
        return

    print(f"Embedding {len(all_chunks)} chunks in TINY batches of {BATCH_SIZE}...")

    # 3. Initialize Model
    embeddings = HuggingFaceEmbeddings(
        model_name="nomic-ai/nomic-embed-text-v1.5",
        model_kwargs={"device": "cpu", "trust_remote_code": True}
    )

    db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

    # 4. The Safety Loop
    total_batches = (len(all_chunks) // BATCH_SIZE) + 1
    
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = all_chunks[i : i + BATCH_SIZE]
        if not batch: continue
        
        try:
            db.add_documents(batch)
            print(f" Saved batch {i//BATCH_SIZE + 1}/{total_batches}")
            
            # --- MEMORY CLEANUP ---
            # Force Python to delete unused variables
            gc.collect()
            # Force Mac MPS to release GPU memory
            torch.mps.empty_cache()
            
        except Exception as e:
            print(f"Error saving batch: {e}")

    print(f"Success! Database built at {DB_PATH}")

if __name__ == "__main__":
    main()