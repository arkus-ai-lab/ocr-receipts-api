from rest_framework import status, generics
from rest_framework.response import Response
import logging
from rest_framework.parsers import MultiPartParser, FormParser
import json
from utilities.config import PROJECT_SETUP
from utilities.document_ai import DocumentAI

from ocr_text.api.serializers import Receipt
from utilities.process_documents import process_documents

class OCRTextView(generics.GenericAPIView):
    """   
        Handle POST Adds a new PDF, jpeg, jpg or png source to the OCR Text API.
                            
    """
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = Receipt
    
    def post(self, request,*args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        project_id = PROJECT_SETUP["project_id"]
        location = PROJECT_SETUP["location"]
        processor_id = PROJECT_SETUP["processor_id"]
        endpoint = PROJECT_SETUP["endpoint"] 
        documents_manager = DocumentAI(project_id, location, processor_id, endpoint)
        try:
            if serializer.is_valid():
                serializer.save()                
                json_data = process_documents()
                return Response(json_data, status=status.HTTP_200_OK)
        except Exception as e: 
            documents_manager.drop_processed_documents()
            return Response({"detail": "This type of file is not supported: " + str(e)}, status=status.HTTP_400_BAD_REQUEST) 
            
            
            