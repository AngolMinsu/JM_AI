from langchain_docling.loader import DoclingLoader
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.allow_external_plugins = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

file_path = "../db/jaryong_job_posting.pdf"

loader = DoclingLoader(file_path=file_path, converter=converter)
docs = loader.load()

print(len(docs))
print(docs[0].page_content)
print(docs[0].metadata)