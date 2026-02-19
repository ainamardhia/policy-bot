# Policy Q&A Assistant with Grounded Citations

An AI-powered Retrieval-Augmented Generation (RAG) tool is designed to answer specific questions from insurance or legal policy documents with high precision and clause-level citations.

## Features

- **Automated Document Ingestion**: Supports multiple PDF uploads via a native file picker.
- **Clause-Level Citations**: Automatically extracts section numbers and page references using Regex and PDF metadata.
- **Semantic Guardrails**: Implements a similarity threshold to prevent hallucinations on unrelated or out-of-scope queries.
- **Section-Aware Chunking**: Uses hierarchical splitting to preserve the context of legal clauses

## Installation

1. **Clone or Download** this repository to your local machine

   ```
   git clone https://github.com/ainamardhia/policy-bot.git
   cd policy-bot
   ```

2. **Create virtual environment**
   Ensure the Python version is 3.9+, then create virtual environment:

   ```
   py -m venv penv
   ```

   _Note that **penv** is the name of the virtual environment._

3. **Activate the virtual environment**

   ```
   # On Windows
   penv\scripts\activate

   # On Mac/Linux
   source penv/bin/activate
   ```

4. **Install dependencies**
   Install these libraries in the terminal:
   ```
   pip install -U langchain-huggingface langchain-text-splitters langchain-community chromadb pypdf sentence-transformers
   ```
   _Note that **-U** means to install the latest version of Python libraries_

## How to Use

1. **Run the script on the terminal:**

   ```
   python policy-bot.py
   ```

2. **Upload Policies (In PDF file)**: A file selection window will appear. Select 2-3 PDF policy documents.

3. **Ask Questions:** Use the terminal prompt to ask questions like:
   - "Is accidental damage covered?"
   - "What are the exclusions for water damage?"

4. **View Citations:** The bot will provide the relevant text and the exact source (Document name, Section/Clause, and Page number).

## System Design

- The system uses the **all-MiniLM-L6-v2** embeddings model for local, high-speed vectorisation.
- It utilises **ChromaDB** as an in-process vector store to manage document embeddings and metadata efficiently.

**Note:** For a deep dive into the chunking strategy and robustness logic, see [Design-Notes.md](./Design-Notes.md).
