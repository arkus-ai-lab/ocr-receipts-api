from rest_framework import status, generics
from rest_framework.response import Response
import logging
from rest_framework.parsers import MultiPartParser, FormParser

from ocr_text.api.serializers import Receipt

class OCRTextView(generics.GenericAPIView):
    """   
        Handle POST Adds a new source to the OCR Text API.
                            
    """
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = Receipt
    
    def post(self, request,*args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )