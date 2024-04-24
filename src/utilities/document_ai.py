import logging
import os
import unicodedata
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from openai import OpenAI
from utilities.config import OPENAI_API_KEY
import json 
import re

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
        for document in os.listdir('src/utilities/documents/'):
            if document.endswith(".pdf"):
                complete_path = os.path.join('src/utilities/documents/', document)
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
                                f"'date (date of credit in the beneficiary account and change format from d month yyyy to YYYY-MM-DD) , "
                                f"'amount'(Just number), "
                                f"'ammount_letter', "
                                f"'reference' ('reference is Number reference' not the 'Concept of payment'), "
                                f"'currency', "
                                f"'ordering_party' with fields 'name (name of the Account holder)', 'rfc (rfc of ordering party)', 'account (which is the CLABE/IBAN of the person who ordered the ticket)', and 'issuer' (bank name), "
                                f"'beneficiary_party' with fields 'name (beneficiary name)', 'rfc (rfc of beneficiary)', 'account (beneficiary CLABE/IBAN)', and 'receiver' (bank name). "
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
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an assistant specialized in handling electronic transactions. "
                        "Your role is to distinguish between the ordering party and the beneficiary party. "
                        "Using the information extracted from the provided screenshots, you will assist the user with their queries. "
                        "Be cautious with the information handling. The user requires an array of JSON objects (but like a string) with the following fields "
                        "(if any field is unknown, use 'NA'): 'type' set to 'eTransaction', 'date' (format: YYYY-MM-DD), "
                        "'amount' (an integer), 'amount_letter' (the ammount using words), 'reference', 'currency', 'ordering_party' "
                        "(origin account) including 'name' (NA), 'rfc', 'account' (if only the last four numbers are available, use them, is the origin account), "
                        "and 'issuer' (bank name). 'beneficiary_party' (details of the receiver) including 'name' (the name of receipt), "
                        "'rfc', 'account' (if only the last four numbers are available, use them, it's closer of the receipt name), and 'receiver' (bank name). "
                        f"This is the text extracted from the document: {result}"
                    )
                },
            ]

                )
            result = completion.choices[0].message.content
            return result
        except Exception as e:
            print(e)

    def remove_code_block_delimiters(self, json_string):
        clean_string = re.sub(r'', '', json_string)
        return clean_string
    
    def string_to_json(self,json_string):
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {e}"

    def reverse_account_numbers(self, json_data):
        try:
            for transaction in json_data:
                if ("ordering_party" in transaction and "account" in transaction["ordering_party"]) and \
                   ("beneficiary_party" in transaction and "account" in transaction["beneficiary_party"]):
                    temp_account = transaction["ordering_party"]["account"]
                    transaction["ordering_party"]["account"] = transaction["beneficiary_party"]["account"]
                    transaction["beneficiary_party"]["account"] = temp_account
                else:
                    logging.error("Missing 'ordering_party'/'beneficiary_party' or 'account' field in transaction.")

            return json_data

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None
    
    def drop_processed_documents(self):
        for document in os.listdir('src/utilities/documents/'):
            if document.endswith(".pdf"):
                complete_path = os.path.join('src/utilities/documents/', document)
                os.remove(complete_path) 
        return None