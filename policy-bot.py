import os
import re
import warnings
import tkinter as tk
from tkinter import filedialog

# 1. SILENCE THE NOISE
warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma

# 2. INITIALIZE THE BRAIN
print("⏳ Loading AI models... Please wait.")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

class PolicyBot:
    def __init__(self):
        self.vector_db = None
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100,
            separators=["\nSection", "\nClause", "\n\n", "\n", " "]
        )

    def process_files(self, file_paths):
        all_chunks = []
        for path in file_paths:
            print(f"📖 Processing: {os.path.basename(path)}")
            loader = PyPDFLoader(path)
            docs = loader.load()
            chunks = self.splitter.split_documents(docs)

            for chunk in chunks:
                chunk.metadata["doc_name"] = os.path.basename(path)
                match = re.search(r"(Section|Clause|§)\s?(\d+(\.\d+)?)", chunk.page_content)
                chunk.metadata["section"] = match.group(0) if match else "General Reference"
            
            all_chunks.extend(chunks)

        # We build the DB in memory for this session
        self.vector_db = Chroma.from_documents(
            documents=all_chunks, 
            embedding=embeddings
        )
        print("✅ Analysis Complete!")

    def ask(self, question):
        if not self.vector_db:
            return "Please upload documents first."

        # SEARCH WITH SCORE: This returns (document, score)
        # In Chroma, a LOWER score means it is MORE similar.
        results = self.vector_db.similarity_search_with_score(question, k=3)
        
        # --- GUARDRAIL LOGIC ---
        # If the best match has a score > 1.2, it's likely unrelated.
        # (You can adjust this number: 0.8 is strict, 1.2 is loose)
        THRESHOLD = 1.1 
        
        if not results or results[0][1] > THRESHOLD:
            return {
                "answer": "I cannot find a definitive answer in the provided policy wording.",
                "sources": [],
                "note": "Guardrail triggered: Question appears unrelated to policy content."
            }

        # Format sources and context if it passes the guardrail
        context_parts = []
        sources = []
        for doc, score in results:
            context_parts.append(f"[{doc.metadata['section']}]\n{doc.page_content}")
            sources.append(f"{doc.metadata['doc_name']} ({doc.metadata['section']}), p.{doc.metadata['page']+1}")
        
        return {
            "answer": "\n\n".join(context_parts),
            "sources": list(set(sources))
        }

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    bot = PolicyBot()

    print("\n📂 Select your Policy PDF files in the popup window.")
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True) # Force the window to the front
    selected_files = filedialog.askopenfilenames(title="Select Policy Documents", filetypes=[("PDF files", "*.pdf")])

    if selected_files:
        bot.process_files(selected_files)

        while True:
            query = input("\n💬 Ask a question (or 'exit'): ")
            if query.lower() == 'exit': break
            
            result = bot.ask(query)
            
            if isinstance(result, str):
                print(result)
            else:
                print("\n--- RESPONSE ---")
                print(result['answer'])
                
                if result['sources']:
                    print("\n--- SOURCES ---")
                    for s in result['sources']:
                        print(f"📍 {s}")
                else:
                    print("\n⚠️ No related clauses found for this query.")
    else:
        print("❌ No files selected.")