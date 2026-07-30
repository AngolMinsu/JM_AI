"""Build the local Chroma index: run `python -m tools.ingest_documents` from web/server."""
import shutil
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from tools.rag_tool import COLLECTION_NAME, QwenLocalEmbeddings, VECTOR_DB_PATH
from tools.csv_tool import load_csv_documents
from tools.pdf_tool import load_pdf_documents

SERVER_DIR = Path(__file__).resolve().parents[1]
def load_documents() -> list[Document]:
    documents = load_csv_documents()
    try:
        documents.extend(load_pdf_documents())
    except Exception as exc:
        print(f"PDF 건너뜀 ({exc})")
    return documents

def main() -> None:
    documents = load_documents()
    if not documents: raise SystemExit("색인할 PDF/CSV 문서가 없습니다.")
    chunks = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150).split_documents(documents)
    for index, doc in enumerate(chunks): doc.metadata["chunk"] = index
    if VECTOR_DB_PATH.exists(): shutil.rmtree(VECTOR_DB_PATH)
    Chroma.from_documents(chunks, QwenLocalEmbeddings(), collection_name=COLLECTION_NAME, persist_directory=str(VECTOR_DB_PATH))
    print(f"RAG 인덱스 생성 완료: {len(documents)}개 문서, {len(chunks)}개 청크 -> {VECTOR_DB_PATH}")

if __name__ == "__main__": main()
