import logging
import os
import unicodedata
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from openai import OpenAI
from utilities.config import OPENAI_API_KEY
import json 

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
        
    def choose_ticket(self,text):
        try:
          text = self.remove_accents(text)
          if "SPEIR" in text:
            return self.get_spei_info(text)
          elif "Enviaste una transferencia" in text:
            return self.get_etransaction_info(text)
        except Exception as e:
            logging.error(e)
            return None
    
    def remove_accents(self,input_str):        
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    def get_spei_info(self, text):
        try:
            completion = CLIENT.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that extracts and structures data from Spanish documents into JSON format. for both the ordering and beneficiary parties. be carefully with all fields."
                    },
                    {
                        "role": "user",
                        "content": f"Organize the extracted information into the specified JSON structure from the document text: "
                                f"'type' set to 'spei', "
                                f"'date' (change format from d month yyyy to YYYY-MM-DD), "
                                f"'amount'(Just number), "
                                f"'ammount_letter', "
                                f"'reference', "
                                f"'currency', "
                                f"'ordering_party' with fields 'name', 'rfc', 'account', and 'issuer' (bank name), "
                                f"'beneficiary_party' with fields 'name', 'rfc', 'account', and 'receiver' (bank name). "
                                f"This is the text extracted from the document: {text}"
                    },
                ]
            )
            result = completion.choices[0].message.content
            print(result)
            return result
        except Exception as e:
            print(e)

    def get_etransaction_info(self, result):
        try:
            completion = CLIENT.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", 
                     "content": f"You are a helpful assistant that helps people with their eTransactions. "
                                f"Essentially with the information extracted from the screenshots, you can help the user with their queries,"
                                f" be carefully with the information, the user only need a array of jsons with the next fields: "
                                f"'type' set to 'eTransaction', "
                                f"'date' (YYYY-MM-DD), "
                                f"'amount', "
                                f"'ammount_letter', "
                                f"'reference', "
                                f"'currency', "
                                f"'ordering_party' with fields 'name', 'rfc', 'account' (If the account has only the las 4 numbersm, take it), and 'issuer' (bank name), "
                                f"'beneficiary_party' with fields 'name', 'rfc', 'account' (If the account has only the las 4 numbersm, take it), and 'receiver' (bank name). "
                                f"This is the text extracted from the document: {result}"
                    },
                    ],
                )
            result = completion.choices[0].message.content
            print(result)
            return result
        except Exception as e:
            print(e)
    
    

    def string_to_json(self,json_string):
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {e}"
