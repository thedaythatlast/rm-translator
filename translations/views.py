from django.shortcuts import render
import argostranslate.translate
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def translate(request):
    text = request.data.get('text')
    result = argostranslate.translate.translate(text, "en", "vi")
    return Response({'translation': result})