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


@api_view(['GET'])
def get_camaras(request):
    camaras = Camaras.objects.filter(estado=True)
    serializer = CamarasSerializer(camaras, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def getCamarasSinEstado(request):
    camaras = Camaras.objects.all()
    serializer = CamarasSerializer(camaras, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_camara(request):
    serializer = CamarasAgregar(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_camara(request, pk):
    camara = Camaras.objects.get(idcamara=pk)
    serializer = CamarasUpdate(camara,data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_camara_estado(request, pk):
    camara = Camaras.objects.get(idcamara=pk)
    data = {"estado":"False"}
    serializer = CamarasSerializer(camara, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def tipoCamara(request):
    camaras = Tipocamara.objects.filter(estado=True)
    serializer = TipocamaraSerializer(camaras, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def getCamaraPk(request, pk):
    try:
        camara = Camaras.objects.get(idcamara=pk, estado=True)
        serializer = CamarasSerializer(camara)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Camaras.DoesNotExist:
        return Response({"errwor": "Camara not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def searchCamaras(request, data):
    
    if data:
        camaras = Camaras.objects.filter(estado=True, nombrecamara__icontains=data)
    else:
        camaras = Camaras.objects.filter(estado=True)
    serializer = CamarasSerializer(camaras, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)   

@api_view(['GET'])
def usuarios_mas_activos(request):
    data = (Detalleusuariocamara.objects
            .values('idusuario__nombreusuario')  # Asumimos que 'usuario' es el nombre del campo en el modelo 'Usuarios'
            .annotate(total_usos=Count('idusuario'))
            .order_by('-total_usos')[:5])  # Los 5 usuarios más activos
    return Response(data)

@api_view(['GET'])
def camara_mas_usada(request):
    data = (Detalleusuariocamara.objects
            .values('idcamara__nombrecamara')  # Asumimos que 'nombrecamara' es el campo que representa el nombre de la cámara
            .annotate(total_usos=Count('idcamara'))
            .order_by('-total_usos')[:1])  # La cámara más usada
    return Response(data)


def horas_pico_camaras(request):
    data = (
        Detalleusuariocamara.objects
        .annotate(hora_extraida=ExtractHour('hora'))  # evitar conflicto
        .values('hora_extraida')
        .annotate(total=Count('idcamara'))
        .order_by('hora_extraida')
    )
    resultado = list(data)
    return JsonResponse(resultado, safe=False)