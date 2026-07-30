from langchain_docling.loader import DoclingLoader
from docling.document_converter import DocumentConverter, CsvFormatOption
from docling.datamodel.pipeline_options import ConvertPipelineOptions
from docling.datamodel.base_models import InputFormat

pipeline_options = ConvertPipelineOptions()
pipeline_options.allow_external_plugins = True

converter = DocumentConverter(
    format_options={
        InputFormat.CSV: CsvFormatOption(pipeline_options=pipeline_options)
    }
)

file_path = '../db/bms_cell_logs_2026.csv'

loader = DoclingLoader(file_path=file_path, converter=converter)
docs = loader.load()

print(len(docs))
print(docs[0].page_content)
print(docs[0].metadata)