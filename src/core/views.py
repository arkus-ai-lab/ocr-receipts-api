from django.shortcuts import render
from django.http import JsonResponse


def test_view(request):
    data = {
        'name': 'test',
        'rfc': 'XAXX010101000',
        'account': '1234567890123',

    }
    return JsonResponse(data)
     