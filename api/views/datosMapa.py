from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import os
from api.models import Camaras  

@api_view(['GET'])
def datosForMapa(request):
    base_path = os.path.join(settings.MEDIA_ROOT)
    media_url = request.build_absolute_uri(settings.MEDIA_URL)

    # 🔹 Cargar coordenadas de cámaras en un diccionario {nombre: (lat, lng)}
    camaras = Camaras.objects.all().values("nombrecamara", "corInicial", "corFinal")
    coordenadas = {
        c["nombrecamara"]: {
            "corInicial": c["corInicial"],
            "corFinal": c["corFinal"]
        }
        for c in camaras
    }

    estructura = {}

    for fecha in os.listdir(base_path):
        fecha_path = os.path.join(base_path, fecha)
        if not os.path.isdir(fecha_path):
            continue

        estructura[fecha] = {}

        for nombre in os.listdir(fecha_path):
            nombre_path = os.path.join(fecha_path, nombre)
            if not os.path.isdir(nombre_path):
                continue

            estructura[fecha][nombre] = {}

            for camara in os.listdir(nombre_path):
                camara_path = os.path.join(nombre_path, camara)
                if not os.path.isdir(camara_path):
                    continue

                # 🔹 Obtener coordenadas si existen
                coords = coordenadas.get(camara, None)

                estructura[fecha][nombre][camara] = {
                    "coordenadas": coords,  # ← agregado aquí
                    "horas": {}
                }

                for hora in os.listdir(camara_path):
                    hora_path = os.path.join(camara_path, hora)
                    if not os.path.isdir(hora_path):
                        continue

                    estructura[fecha][nombre][camara]["horas"][hora] = []

                    for imagen in os.listdir(hora_path):
                        if imagen.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                            url = f"{media_url}{fecha}/{nombre}/{camara}/{hora}/{imagen}"
                            estructura[fecha][nombre][camara]["horas"][hora].append(url)

    return Response(estructura)
