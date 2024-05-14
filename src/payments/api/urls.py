from django.urls import path

from . import views

urlpatterns = [
    path('',views.PaymentsView.as_view(),name='payments'),
]