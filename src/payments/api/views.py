from django.views.generic.base import TemplateView

class PaymentsView(TemplateView):
    template_name = 'payments.html'