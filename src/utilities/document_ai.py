import logging
import os
import unicodedata
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
                    {"role": "system", "content": "You are an assistant that extract information from a document which is written in Spanish."
                     +"You have to extract the following information:"
                     +" 1. 'Name' (Ordering party), "
                     +" 2. 'RFC' (Ordering party), "
                     +" 3. 'CLABE'(Ordering party), "
                     +" 4. 'Date', "
                     +" 5. 'Amount', "
                     +" 6. 'Currency' "
                     +" 7. 'Issuer'."},  
                     {"role": "user", "content": "Please provide a json with the next fields:"
                        +"'Name' of the person who ordered the ticket,"
                        +"'RFC' of the person who ordered the ticket,"
                        +"'Account' which is the CLABE/IBAN of the person who ordered the ticket,"
                        +"'Date' of the ticket,"
                        +"'Amount' of the ticket,"
                        +"'Currency' of the ticket, which might be 'MXN' or 'USD',"
                        +"'Issuer' of the ticket."
                        +"This is the text extracted from the document:"
                        +f"{text}"},
                    ],
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
                    {"role": "system", "content": "You are a helpful assistant that helps people with their eTransactions. "
                    +"Essentially with the information extracted from the screenshots, you can help the user with their queries,"
                    +" be carefully with the information, the user only need a array of jsons with the next fields: "
                    +"'Name' (Account holder) , "
                    +"'RFC' (Account Holder), "
                    +"'Account', "
                    +"'Date', "
                    +"'Ammount', "
                    +"'CurrencyType and "
                    +"the 'Issuer', "
                    +"if you don't detect some fields put 'None' in the field. "
                    +" without explanations, just that info. Also, if you detect that the document have 2 screenshots or more please add the info of all of them."
                    +"If the document is not visible or is not a ticket, please let the user know returning this message 'Please check the information of the ticket' ."},
                    {"role": "user", "content": "Please provide a json with the next fields:"
                    +"Name of the person who issued the ticket,"
                    +"Date of the ticket,"
                    +"Amount of the ticket,"
                    +"This is the text extracted from the document:"
                    +f"{result}"},
                    ],
                )
            result = completion.choices[0].message.content
            print(result)
            return result
        except Exception as e:
            print(e)