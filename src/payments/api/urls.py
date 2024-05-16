from django.urls import path

from  payments.api import views
from payments.api.views import PaymentsView

urlpatterns = [
    path('', PaymentsView.as_view(),name='payments'),
    path('config/', views.stripe_config),
    path('create-checkout-session/',views.create_checkout_session),
]