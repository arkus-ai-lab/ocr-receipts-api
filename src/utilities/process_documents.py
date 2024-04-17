import os 
from utilities.document_ai import DocumentAI
import logging

def process_documents():
    project_id = "ocrdocumentai-419906"
    processor_id = "ffec49331ad6da12"
    endpoint= "documentai.googleapis.com"
    location = "us"
    try:
        documents_manager = DocumentAI(project_id, location, processor_id, endpoint, DIRECTORIES)
        documents = documents_manager.get_documents()
        documents_manager.convert_documents_to_jpg(documents)
        images = documents_manager.get_images()
        for image in images:
            document = documents_manager.extract_text(image, project_id, location, processor_id, endpoint)
            print(document.text)
            relevant_info = documents_manager.get_document_info(document)
    except Exception as e:
        logging.error(e)
        return None
    return documents