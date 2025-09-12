# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.http import JsonResponse
from ..models import Camaras
from ..models import Tipocamara
from ..serializers import CamarasSerializer
from ..serializers import CamarasAgregar
from ..serializers import TipocamaraSerializer
from ..serializers import CamarasUpdate
from ..serializers import Detalleusuariocamara
import requests
import os
from django.http import HttpResponse


@api_view(['GET'])
def getListSerenos(request):
    try:
        url = "https://alerta-serenazgo-mpsm.onrender.com/api/alertas/listar/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return Response(data)  # Esto solo funciona si se usa DRF correctamente
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def getBanda(request):
    try:
        url = "https://alerta-serenazgo-mpsm.onrender.com/api/proxy-banda/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return Response(data)  # Esto solo funciona si se usa DRF correctamente
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=500)
@api_view(['GET'])
def getTarapoto(request):
    try:
        url = "https://alerta-serenazgo-mpsm.onrender.com/api/proxy-tarapoto/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return Response(data)  # Esto solo funciona si se usa DRF correctamente
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def getMorales(request):
    try:
        url = "https://alerta-serenazgo-mpsm.onrender.com/api/proxy-morales/"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return Response(data)  # Esto solo funciona si se usa DRF correctamente
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=500)




@api_view(['GET'])
def getMapa(request, z, x, y):
    print(f"🔄 getMapa: z={z}, x={x}, y={y}")
    url = f"https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"

    headers = {
        'User-Agent': 'SerenazgoMPSM/1.0 (cristianmestanzaortiz870@gmail.com)'
    }

    try:
        response = requests.get(url, timeout=10, headers=headers)
        if response.status_code == 200:
            return HttpResponse(response.content, content_type="image/png")
        else:
            print(f"❌ Tile no encontrado: {response.status_code}")
            return HttpResponse(f"Tile no encontrado: {response.status_code}", status=response.status_code)

    except requests.exceptions.ReadTimeout:
        print(f"⏳ Timeout al descargar {url}")
        return HttpResponse("Timeout", status=504)

    except Exception as e:
        print("⚠️ Error:", str(e))
        return HttpResponse("Error interno", status=500)