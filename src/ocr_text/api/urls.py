from django.urls import path
from ocr_text.api.views import OCRTextView


urlpatterns = [
    path('ocr_text/', OCRTextView.as_view(), name='ocr_text'),
]