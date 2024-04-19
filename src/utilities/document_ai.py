import logging
import os
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from openai import OpenAI
from utilities.config import OPENAI_API_KEY

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
CLIENT = OpenAI(api_key= OPENAI_API_KEY)

class DocumentAI:
    def __init__(self, project_id, location, processor_id, endpoint):
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        self.endpoint = endpoint        

    def get_documents(self):
        docs_path = []
        for document in os.listdir('utilities/documents/'):
            if document.endswith(".pdf"):
                complete_path = os.path.join('utilities/documents/', document)
                docs_path.append(complete_path) 
        print(docs_path)        
        return docs_path    
   

    def extract_text(self, docs_path):
        try:
            mime_type = 'application/pdf'
            client = documentai.DocumentProcessorServiceClient(
                client_options=ClientOptions(api_endpoint=self.endpoint))
            name =  client.processor_path(self.project_id, self.location, self.processor_id)
            with open(docs_path, "rb") as image:
                image_content = image.read()

            raw_document = documentai.RawDocument(
                content=image_content, mime_type=mime_type)
            
            request = documentai.ProcessRequest(
                name=name,
                raw_document=raw_document)
            response = client.process_document(request=request)
            document = response.document
            
            return document.text
        except Exception as e:
            logging.error(e)
            return None
    
    def get_document_info(self, text):
        try:
            completion = CLIENT.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": "You are a helpful assistant that helps people with their documents. "
                    +"Essentially with the information extracted from the document, you can help the user with their queries,"
                    +" be carefully with the information, the user only need a array of jsons with the next fields 'Name', 'Date' and 'Ammount', 'RFC'"
                    +" without explanations, just that info. Also, if you detect that the document have 2 tickets or more please add the info of all of them."
                    +"If the document is not visible or is not a ticket, please let the user know returning this message 'Please check the information of the ticket' ."},
                    {"role": "user", "content": "Please provide a json with the next fields:"
                    +"Name of the person who issued the ticket,"
                    +"Date of the ticket,"
                    +"Amount of the ticket,"
                    +"This is the text extracted from the document:"
                    +f"{text}"},
                    ],
                )
            result = completion.choices[0].message.content
            print(result)
            return result
        except Exception as e:
            print(e)