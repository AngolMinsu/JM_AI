"""Build the local Chroma index: run `python -m tools.ingest_documents` from web/server."""
import csv
import shutil
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from tools.rag_tool import COLLECTION_NAME, QwenLocalEmbeddings, VECTOR_DB_PATH

SERVER_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = SERVER_DIR / "db"

def load_documents() -> list[Document]:
    documents: list[Document] = []
    pdf_path = SOURCE_DIR / "jaryong_job_posting.pdf"
    if pdf_path.exists():
        try:
            # docling is already part of this project's dependency set and
            # preserves PDF structure better than plain text extraction.
            from langchain_docling.loader import DoclingLoader
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.document_converter import DocumentConverter, PdfFormatOption
            options = PdfPipelineOptions()
            options.allow_external_plugins = True
            converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)})
            pdf_docs = DoclingLoader(file_path=str(pdf_path), converter=converter).load()
            for doc in pdf_docs:
                doc.metadata.update({"source": pdf_path.name, "kind": "job_posting"})
            documents.extend(pdf_docs)
        except Exception as docling_exc:
            # Some legacy Korean PDFs fail Docling's OCR preprocessing.  Keep
            # a lightweight text-extraction fallback for those files.
            try:
                from pypdf import PdfReader
                text = "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf_path)).pages)
                if text.strip():
                    documents.append(Document(page_content=text, metadata={"source": pdf_path.name, "kind": "job_posting"}))
            except Exception as fallback_exc:
                print(f"PDF 건너뜀 (Docling: {docling_exc}; fallback: {fallback_exc})")
    csv_path = SOURCE_DIR / "bms_cell_logs_2026.csv"
    if csv_path.exists():
        with csv_path.open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        for index in range(0, len(rows), 100):
            batch = rows[index:index + 100]
            documents.append(Document(page_content="\n".join(" | ".join(f"{key}={value}" for key, value in row.items()) for row in batch), metadata={"source": csv_path.name, "kind": "bms_log", "row_start": index + 1}))
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
