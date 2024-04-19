import os 
from utilities.document_ai import DocumentAI
import logging
from utilities.config import PROJECT_SETUP


def process_documents():    
    project_id = PROJECT_SETUP["project_id"]
    location = PROJECT_SETUP["location"]
    processor_id = PROJECT_SETUP["processor_id"]
    endpoint = PROJECT_SETUP["endpoint"]     
    try:
        documents_manager = DocumentAI(project_id, location, processor_id, endpoint)
        documents = documents_manager.get_documents()
        document_text = ''
        for document in documents:
            document_text = documents_manager.extract_text(document)
            relevant_info = documents_manager.get_document_info(document_text)
        
        print(document_text)
        print(relevant_info)
    except Exception as e:
        logging.error(e)
        return None
    return relevant_info