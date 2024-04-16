from rest_framework import status, generics
from rest_framework.response import Response
import logging
class OCRTextView(generics.GenericAPIView):
    """   
        Handle POST Adds a new source to the OCR Text API.
                            
    """
    
    def post(self, request,*args, **kwargs):
        try:
            source = add_ocr_source()
            return Response(source, status=status.HTTP_200_OK)   
        except Exception as e:            
            logging.exception("Unexpected error occurred when adding new resource.")
            return Response({"detail": " An unexpected error occurred, " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

