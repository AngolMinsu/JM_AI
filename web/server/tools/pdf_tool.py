"""Read-only RAG helper for the job-posting PDF."""
from pathlib import Path
from typing import Any, Dict

PDF_PATH = Path(__file__).resolve().parents[1] / "db" / "jaryong_job_posting.pdf"

PDF_TOOL_SPEC: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_job_posting",
        "description": "채용공고 PDF를 RAG로 검색합니다. 연봉, 복리후생, 직무, 자격요건 질문에만 사용합니다. PDF는 읽기 전용입니다.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "채용공고에 대한 질문"}}, "required": ["query"], "additionalProperties": False},
    },
}


def load_pdf_documents():
    """Extract the job PDF, falling back to pypdf for legacy encodings."""
    from langchain_core.documents import Document
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"채용공고 PDF가 없습니다: {PDF_PATH}")
    try:
        from langchain_docling.loader import DoclingLoader
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
        options = PdfPipelineOptions()
        options.allow_external_plugins = True
        converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)})
        docs = DoclingLoader(file_path=str(PDF_PATH), converter=converter).load()
    except Exception:
        from pypdf import PdfReader
        text = "\n".join(page.extract_text() or "" for page in PdfReader(str(PDF_PATH)).pages)
        docs = [Document(page_content=text, metadata={})] if text.strip() else []
    for doc in docs:
        doc.metadata.update({"source": PDF_PATH.name, "kind": "job_posting"})
    return docs


def execute_pdf_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    from tools.rag_tool import execute_rag_search
    return execute_rag_search(str(arguments.get("query", "")), source=PDF_PATH.name)
