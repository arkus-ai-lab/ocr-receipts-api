import os
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from openai import OpenAI
import pdf2image

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"


class DocumentAI:
    def __init__(self, project_id, location, processor_id, endpoint, directories):

        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        self.endpoint = endpoint
        self.documents_path = directories[0]
        self.converted_path = directories[1]

    def get_documents(self):
        documents = []
        for document in os.listdir(self.documents_path):
            if document.endswith(".pdf"):
                document_path = os.path.join(self.documents_path, document)
                document = self.process_document(document_path, self.project_id, self.location, self.processor_id, self.endpoint)
                documents.append(document)
        return documents
    
    def convert_documents_to_jpg(self, documents):
        for document in documents:
            complete_path = os.path.join(self.documents_path, document)
            jpg_save_path = os.path.join(self.converted_path, document[:-4])
            pages = pdf2image.convert_from_path(complete_path, 500)
            for i, page in enumerate(pages):
                page.save(f'{jpg_save_path}_{i}.jpg', 'JPEG')

    def get_images(self):
        images = []
        for image in os.listdir(self.converted_path):
            if image.endswith(".jpg"):
                image_path = os.path.join(self.converted_path, image)
                images.append(image_path)
        return images

    def extract_text(self, complete_path, project_id, location, processor_id, endpoint):
        mime_type = "image/jpeg"
        client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(api_endpoint=f"{location}-{endpoint}"))
        name =  client.processor_path(project_id, location, processor_id)
        with open(complete_path, "rb") as image:
            image_content = image.read()

        raw_document = documentai.RawDocument(
            content=image_content, mime_type=mime_type)
        
        request = documentai.ProcessRequest(
            name=name,
            raw_document=raw_document)
        response = client.process_document(request=request)
        document = response.document
        return document
    
    def get_document_info(self, document):
        try:
            completion = self.openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": "You are a helpful assistant that helps people with their documents. "
                    +"Essentially with the information extracted from the document, you can help the user with their queries,"
                    +" be carefully with the information, the user only need a array of jsons with the next fields 'Name', 'Date' and 'Ammount', 'document type'"
                    +" without explanations, just that info. Also, if you detect that the document have 2 tickets or more please add the info of all of them."
                    +"If the document is not visible or is not a ticket, please let the user know returning this message 'Please check the information of the ticket' ."},
                    {"role": "user", "content": "Please provide a json with the next fields:"
                    +"Name of the person who issued the ticket,"
                    +"Date of the ticket,"
                    +"Amount of the ticket,"
                    +"This is the text extracted from the document:"
                    +f"{document.text}"},
                    ],
                )
            result = completion.choices[0].message.content
            print(result)
            return result
        except Exception as e:
            print(e)