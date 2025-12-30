from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import os
from datetime import datetime
from ..models import Personarq, Camaras, Detallepersonacamara
from ..serializers import PersonarqSerializer, DetallepersonacamaraSerializer


@api_view(['GET'])
def extractPersonaRq(request):
    base_path = os.path.join(settings.MEDIA_ROOT)
    dia_actual = datetime.now().strftime("%Y-%m-%d")
    carpetas_dia_actual = os.path.join(base_path, dia_actual)

    # Verifica si la carpeta del día existe
    if not os.path.exists(carpetas_dia_actual):
        return Response({"error": f"No existe carpeta: {carpetas_dia_actual}"}, status=400)

    carpetas = os.listdir(carpetas_dia_actual)

    for carpeta in carpetas:
        persona = Personarq.objects.filter(estado=True, nombre__icontains=carpeta).first()

        if persona is None:
            persona_data = {
                "nombre": carpeta,
                "estado": True
            }
            persona_serializer = PersonarqSerializer(data=persona_data)
            if persona_serializer.is_valid():
                persona = persona_serializer.save()
            else:
                print("Error persona:", persona_serializer.errors)
                continue  # Salta a la siguiente carpeta si no se pudo crear

        # Lógica común que siempre se ejecuta UNA VEZ
        nombres = os.path.join(carpetas_dia_actual, carpeta)
        if not os.path.exists(nombres):
            continue

        for nombre in os.listdir(nombres):
            camaras = Camaras.objects.filter(estado=True, nombrecamara__icontains=nombre)

            for camara in camaras:
                carpeta_minuto = os.path.join(nombres, nombre)
                if not os.path.exists(carpeta_minuto):
                    continue

                for minuto in os.listdir(carpeta_minuto):
                    hora_formateada = minuto.replace('-', ':') + ':00'

                    detalle_data = {
                        "idcamara": camara.idcamara,
                        "idpersona": persona.idpersona,
                        "fecha": dia_actual,
                        "hora": hora_formateada,
                        "estado": True
                    }

                    detalle_serializer = DetallepersonacamaraSerializer(data=detalle_data)
                    if detalle_serializer.is_valid():
                        print("Entro")
                        detalle_serializer.save()
                    else:
                        print("Error detalle:", detalle_serializer.errors)

    return Response({"status": "ok"})

@api_view(['GET'])
def getPersonasRq(request):
    personas = Personarq.objects.filter(estado=True)
    serializer = PersonarqSerializer(personas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getPersonasRqPk(request, pk):
    try:
        persona = Detallepersonacamara.objects.filter(idpersona=pk, estado=True).order_by("fecha", "hora")
    except Detallepersonacamara.DoesNotExist:
        return Response({"error": "Persona no encontrada"}, status=404)

    serializer = DetallepersonacamaraSerializer(persona, many=True)
    # print(persona)
    return Response(serializer.data)