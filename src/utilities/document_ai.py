import logging
import os
import unicodedata
from google.cloud import documentai
from google.api_core.client_options import ClientOptions
from openai import OpenAI
from utilities.config import OPENAI_API_KEY
import json 
import re
import img2pdf
from PIL import Image

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
CLIENT = OpenAI(api_key= OPENAI_API_KEY)

class DocumentAI:
    def __init__(self, project_id, location, processor_id, endpoint):
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        self.endpoint = endpoint        

    def get_documents(self):
        try:
            docs_path = []
            for document in os.listdir('utilities/documents/'):
                if document.endswith(".pdf"):
                    complete_path = os.path.join('utilities/documents/', document)
                    docs_path.append(complete_path) 
            print(docs_path)
            return docs_path
        except Exception as e:
            logging.error(e)
            return logging.error("No documents found in the directory.")    
   
    def convert_image_to_pdf(self):
        try:    
            for image in os.listdir('utilities/documents/'):
                if image.endswith(".jpg"):
                    complete_path = os.path.join('utilities/documents/', image)
                    image = Image.open(complete_path)
                    pdf_path = complete_path.replace(".jpg", ".pdf")
                    pdf_bytes = img2pdf.convert(image.filename)
                    with open(pdf_path, "wb") as pdf_file:
                        pdf_file.write(pdf_bytes)
                        image.close()
                        pdf_file.close()
                elif image.endswith(".jpeg"):
                    complete_path = os.path.join('utilities/documents/', image)
                    image = Image.open(complete_path)
                    pdf_path = complete_path.replace(".jpeg", ".pdf")
                    pdf_bytes = img2pdf.convert(image.filename)
                    with open(pdf_path, "wb") as pdf_file:
                        pdf_file.write(pdf_bytes)
                        image.close()
                        pdf_file.close()
                elif image.endswith(".png"):
                    complete_path = os.path.join('utilities/documents/', image)
                    image = Image.open(complete_path)
                    pdf_path = complete_path.replace(".png", ".pdf")
                    pdf_bytes = img2pdf.convert(image.filename)
                    with open(pdf_path, "wb") as pdf_file:
                        pdf_file.write(pdf_bytes)
                        image.close()
                        pdf_file.close()
                else:
                    logging.error("The document is not an image.")
                    return logging.error("The document is not an image.")
        except Exception as e:
            logging.error(e)
            return logging.error("An error occurred while converting the image to PDF.")

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
            print(document.text)
            return document.text
        except Exception as e:
            logging.exception("An error occurred while extracting text from the document")
            return None
        
    def choose_ticket(self,text):
        try:
          text = self.remove_accents(text)
          if "VENTA" in text:
              return self.get_sale_info(text)
          elif "SISTEMA DE PAGOS" in text:
            return self.get_spei_info(text)
          elif "Enviaste una transferencia" in text:
            return self.get_etransaction_info(text)
          elif 'Comprobante de Operacion' in text:          
            return self.get_proof_of_operation(text)
          elif 'BANCO/CLIENTE' in text:
            return self.get_bank_customer_checking_deposit(text)          
          elif "PAGUESE " in text:
            return self.get_check_info(text)          
          elif "LIBRETON NOMINA" or "CUENTA DE CHEQUES" or "ESTADO DE CUENTA" in text:
            return self.get_payroll_info(text)                  
          else:
            return logging.error("The document does not match any of the available templates.")
        except Exception as e:
            logging.error(e)
            return None
    
    def remove_accents(self,input_str): 
        try:       
            nfkd_form = unicodedata.normalize('NFKD', input_str)
            return "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        except Exception as e:
            logging.error(e)
            return logging.error("An error occurred while removing accents.")

    def get_spei_info(self, text):
        try:
            completion = CLIENT.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that extracts and structures data from Spanish financial documents into JSON format for both the ordering and beneficiary parties."
                        + "Remember to enclose the JSON in curly braces. Be careful with all fields."
                    },
                    {
                        "role": "user",
                        "content": f"Organize the extracted data in the following JSON format: "
                                f"'type': set to 'spei', "
                                f"'date': 'Date of credit to the beneficiary account' (change format from d month yyyy to YYYY-MM-DD), "
                                f"'amount': (just number), "
                                f"'ammount_letter':(for example: 'sesenta y un mil cien mil pesos'), "
                                f"'reference': 'reference' is Numeric reference' and NOT the 'Concept of payment', it must be a string,  "
                                f"'currency': it might be 'MXN' or 'USD', "
                                f"'ordering_party' with fields: \n"                                
                                f"  'name': (Account holder of the ordering party, please do not include the name of 'Issuing institution of the payment')', "
                                f"  'rfc': 'RFC/CURP' of the ordering party (person's RFC or CURP), " 
                                f"  'account': it is the 'CLABE/IBAN' of ordering party, it must be a string, "
                                f"  'issuer': bank name, "
                                f"'beneficiary_party' with fields: \n"
                                f"  'name': beneficiary name, "
                                f"  'rfc': 'RFC/CURP' of the beneficiary party (beneficiary bank RFC or CURP), "
                                f"  'account': 'CLABE/IBAN' of the beneficiary which must be a string, "
                                f"  'receiver': beneficiary bank name, "
                                f"This is the text extracted from the document: {text}"
                    },
                ]
            )
            result = completion.choices[0].message.content
            print(result)
            return result
        except Exception as e:
            logging.error(e)
            return logging.error("An error occurred while getting the SPEI information.")

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
                        "Be cautious with the information handling. The user requires a JSON object (but like a string) with the following fields "
                        "(if any field is unknown, use 'NA'): 'type' set to 'eTransaction', 'date' (format: YYYY-MM-DD), "
                        "'amount' (an integer), 'amount_letter' (the ammount using words), 'reference' (this are just numbers, without letters) it must be a string, 'currency', 'ordering_party' "
                        "(origin account) including 'name' (NA), 'rfc', 'account' (if only the last four numbers are available, use them, is the origin account, it must be a string), "
                        "and 'issuer' (bank name). 'beneficiary_party' (details of the receiver) including 'name' (the name of receipt), "
                        "'rfc', 'account' (if only the last four numbers are available, use them, it's closer of the receipt name, it must be a string), and 'receiver' (bank name). "
                        f"This is the text extracted from the document: {result}"
                    )
                },
            ]
                )
            result = completion.choices[0].message.content
            print(result)
            return result
        except Exception as e:
            logging.error(e)
            return logging.error("An error occurred while getting the eTransaction information.")
    
    def get_proof_of_operation(self, text):
        try:
            completion = CLIENT.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that extracts and structures data from Spanish financial documents into JSON format for both the ordering and beneficiary parties."
                        + "Remember to enclose the JSON in curly braces. Be careful with all fields and do not include trademark/registered symbols."
                    },
                    {
                        "role": "user",
                        "content": f"Organize the extracted data in the following JSON format: "
                                f"'type': set to 'proofOfOperation', "
                                f"'date': change format from d month yyyy to YYYY-MM-DD, "
                                f"'amount': (just number), "
                                f"'ammount_letter':(for example: 'mil doscientos dolares Americanos'), "
                                f"'reference': NA,  "
                                f"'currency': it might be 'MXN' or 'USD', "
                                f"'ordering_party' with fields: \n"                                
                                f"  'name': Customer's name, "
                                f"  'rfc': 'NA', " 
                                f"  'account': account number(No. de cuenta) it must be a string, "
                                f"  'issuer': bank name, "
                                f"'beneficiary_party' with fields: \n"
                                f"  'name': 'NA', "
                                f"  'rfc': 'NA', "
                                f"  'account': account number(/Ref) field, it must be a string, "
                                f"  'receiver': 'NA', "
                                f"This is the text extracted from the document: {text}"
                    },
                ]
            )
            result = completion.choices[0].message.content
            return result
        except Exception as e:
            logging.error(e)
            return logging.error("An error occurred while getting the bank receipt information.")
        
    def get_bank_customer_checking_deposit(self, text):
        try:
            completion = CLIENT.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that extracts and structures data from Spanish financial documents into JSON format for both the ordering and beneficiary parties."
                        + "Remember to enclose the JSON in curly braces. Be careful with all fields and do not include trademark/registered symbols."
                    },
                    {
                        "role": "user",
                        "content": f"Organize the extracted data in the following JSON format: "
                                f"'type': set to 'bankCustomerCheckDeposit', "
                                f"'date': change format from d month yyyy to YYYY-MM-DD, "
                                f"'amount': (just number), "
                                f"'ammount_letter':(for example: 'mil doscientos dolares Americanos'), "
                                f"'reference': Reference number, it must be a string,  "
                                f"'currency': it might be 'MXN' or 'USD', "
                                f"'ordering_party' with fields: \n"                                
                                f"  'name': Customer's name, "
                                f"  'rfc': 'NA', " 
                                f"  'account': account number(No. de cuenta), it must be a string, "
                                f"  'issuer': bank name, "
                                f"'beneficiary_party' with fields: \n"
                                f"  'name': 'NA', "
                                f"  'rfc': 'NA', "
                                f"  'account': account number(/Ref) field, it must be a string, "
                                f"  'receiver': 'NA', "
                                f"This is the text extracted from the document: {text}"
                    },
                ]
            )
            result = completion.choices[0].message.content
            return result
        except Exception as e:
            logging.error(e)
            return logging.error("An error occurred while getting the bank receipt information.")

    def get_check_info(self, result):
        try:
            completion = CLIENT.chat.completions.create(
            model="gpt-3.5-turbo",
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an assistant specialized in handling checks. "
                        "Your role is to distinguish between the ordering party and the beneficiary party. "
                        "Using the information extracted from the provided scanned checks, you will assist the user with their queries. "
                        "Be cautious with the information handling. The user requires a JSON object (but like a string) with the following fields "
                        "(if any field is unknown, use 'NA'): 'type' set to 'check', 'date' (format: YYYY-MM-DD, sometimes the numbers could be letters, please be intuitive, e. g. zozl might be 2022), "
                        "'amount' (an float), 'amount_letter' (the ammount using words e. g. cien mil pesos or mil quinientos dolares), 'reference'  (Number or folio in the check e. g. 1111⑆222222222⑆33333333333⑈XXXXXXX the last 7 numbers) it must be a string, 'currency' (MXN or USD), 'ordering_party' "
                        "(origin account) including 'name' (here is the name of the person who owns the issuing account), 'rfc', 'account' (the 'clabe' or similar) it must be a string, "
                        "and 'issuer' (bank name). 'beneficiary_party' (details of the receiver) including 'name' (here is the name of the person to whom the check is addressed after 'Paguese este cheque a:' or similar, it might be company name or person name, but ignore the name of banks in this field), "
                        "'rfc' (NA), 'account' (NA), and 'receiver' (bank name)."
                        f"This is the text extracted from the document: {result}"
                    )
                },
            ]
                )
            result = completion.choices[0].message.content
            return result
        except Exception as e:
            print(e)

    def get_payroll_info(self, text):
        try:
            completion = CLIENT.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that extracts and structures data from Spanish financial documents into JSON format for both the ordering and beneficiary parties."
                        + "Remember to enclose the JSON in curly braces. Be careful with all fields and do not include trademark/registered symbols."
                    },
                    {
                        "role": "user",
                        "content": f"Organize the extracted data in the following JSON format: "
                                f"'type': set to 'payrollReceipt', "                                
                                f"'currency': it might be 'MXN' or 'USD', "
                                f"'ordering_party' with fields: \n"                                
                                f"  'name': Customer's name, "
                                f"  'rfc': 'R.F.C' of the ordering party (person's R.F.C), "  
                                f"  'account': account number 'NO. DE CUENTA' e.g xx-xxxxxxxx-x or with length max of 11, "
                                f"  'issuer': bank name, "
                                f"  'clabe': which is the 'CLABE'/IBAN of ordering party"                                
                                f""
                                f"This is the text extracted from the document: {text}"
                    },
                ]
            )
            result = completion.choices[0].message.content
            return result
        except Exception as e:
            logging.error(e)
            return logging.error("An error occurred while getting the payroll information.")
        
    def get_sale_info(self, text):
        try:
            completion = CLIENT.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that extracts and structures data from Spanish financial documents into JSON format for both the ordering and beneficiary parties."
                        + "Remember to enclose the JSON in curly braces. Be careful with all fields and do not include trademark/registered symbols."
                    },
                    {
                        "role": "user",
                        "content": f"Organize the extracted data in the following JSON format: "
                                f"'type': set to 'SaleReceipt', "
                                f"'date': it must change format from d month yyyy to YYYY-MM-DD, "
                                f"'amount': (just number), "
                                f"'ammount_letter':(for example: 'mil doscientos dolares Americanos'), "
                                f"'reference': Reference number, it must be a string,  "
                                f"'currency': it might be 'MXN' or 'USD', "
                                f"'ordering_party' with fields: \n"                                
                                f"  'name': 'NA', "
                                f"  'rfc': 'NA', " 
                                f"  'account': card number(Numero de tarjeta), it must be a string e.g ************0423, "
                                f"  'issuer': bank name, "
                                f"'beneficiary_party' with fields: \n"
                                f"  'name': 'NA', "
                                f"  'rfc': 'NA', "
                                f"  'account': 'NA', "
                                f"  'receiver': 'NA', "
                                f"This is the text extracted from the document: {text}"
                    },
                ]
            )
            result = completion.choices[0].message.content
            return result
        except Exception as e:
            logging.error(e)
            return logging.error("An error occurred while getting the sale information.")


    
    def string_to_json(self,json_string):
        try:
            data = json.loads(json_string)
            result_json = json.dumps(data, ensure_ascii=False, indent=4)
            print(result_json)
            return json.loads(result_json)
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {e}"
        
    def remove_code_block_delimiters(self, json_string):
        try:
            clean_string = re.sub(r'```json|```', '', json_string)
            print("clean_string",clean_string)
            return clean_string
        except Exception as e:
            logging.error(e)
            return logging.error("An error occurred while removing code block delimiters.")

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
        
    def iterate_nested_json_for_loop(self,json_obj):
        try:
            for key, value in json_obj.items():
                if isinstance(value, dict):
                    self.iterate_nested_json_for_loop(value)
                    if key == 'eTransaction':
                        self.reverse_account_numbers(json_obj)
                        return json_obj
                else:
                    print(f"{key}: {value}")
        except Exception as e:
            logging.error(e)
            return logging.error("An error occurred while iterating the nested JSON for loop.")

    def drop_processed_documents(self):
        try:
            for document in os.listdir('utilities/documents/'):
                complete_path = os.path.join('utilities/documents/', document)
                os.remove(complete_path) 
            return None
        except Exception as e:
            logging.error(e)
            return logging.error("An error occurred while dropping processed documents.")
        

    
    