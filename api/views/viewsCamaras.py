import cv2
import os
import time
import threading
import requests
import numpy as np
from datetime import datetime, date
from django.http import StreamingHttpResponse, JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from .face_recognition_service import *
import pygame

# =========================
# CONFIG
# =========================
RUTA_MEDIA = "media"
SIM_THRESHOLD = 0.65      # solo para colorear / lógica local (la API ya filtra también)
SOUND_COOLDOWN = 3        # seg. entre sonidos

HOY = date.today()
camaras_activas = {}
alert_sound = None

# =========================
# AUDIO
# =========================
try:
    pygame.mixer.init()
    alert_sound = pygame.mixer.Sound(os.path.join(settings.BASE_DIR, 'api', 'sonido', 'alerta.mp3'))
except pygame.error as e:
    print(f"No se pudo inicializar el audio: {e}")
    alert_sound = None

# =========================
# HILO: consulta API
# =========================
class ProcesadorAPI(threading.Thread):
    def __init__(self):
        super().__init__()
        self.frame = None
        self.resultado = []
        self.lock = threading.Lock()
        self.running = True

    def detener(self):
        self.running = False

    def actualizar_frame(self, frame):
        with self.lock:
            self.frame = frame.copy()

    def obtener_resultado(self):
        with self.lock:
            return list(self.resultado)

    def run(self):
        while self.running:
            frame = None

            with self.lock:
                if self.frame is not None:
                    frame = self.frame
                    self.frame = None

            if frame is not None:
                resultado = procesar_frame(frame)
                with self.lock:
                    self.resultado = resultado

            time.sleep(0.05)
# =========================
# STREAMING: abre RTSP, manda a API, pinta y emite MJPEG
# =========================
def gen_camera_stream(camera_id, nombre):
    print(f"Conectando a la cámara {camera_id}...")
    rtsp_url = f"rtsp://admin:Serenazgo1234@{str(camera_id)}/video?tcp"
    print(camera_id)
    cap = cv2.VideoCapture(rtsp_url)
    # cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    # cap.set(cv2.CAP_PROP_BUFFERSIZE,    1)

    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return

    camaras_activas[camera_id] = cap
    procesador = ProcesadorAPI()
    procesador.start()

    last_sound_time = 0
    os.makedirs(os.path.join(RUTA_MEDIA, str(HOY)), exist_ok=True)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            frame = cv2.resize(frame, (640, 360))
            procesador.actualizar_frame(frame)

            # Usar última inferencia ya disponible
            for x1, y1, x2, y2, name, sim in procesador.obtener_resultado():
                color = (255, 0, 0) if name == "Desconocido" else (0, 0, 255)

                # Guardado de evidencia para reconocidos (sólo 1 carpeta por minuto por persona)
                if name != "Desconocido":
                    horaCompleta = datetime.now().strftime("%H-%M")
                    carpeta_persona = os.path.join(RUTA_MEDIA, str(HOY), name, str(nombre), horaCompleta)
                    if not os.path.exists(carpeta_persona):
                        os.makedirs(carpeta_persona, exist_ok=True)
                        cv2.imwrite(os.path.join(carpeta_persona, f"{name}_rostro.jpg"), frame[y1:y2, x1:x2])
                        cv2.imwrite(os.path.join(carpeta_persona, f"{name}_general.jpg"), frame)

                # Pintar
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{name} ({sim:.2f})", (x1, max(20, y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                # Sonido si reconocido (cooldown)
                if name != "Desconocido" and (time.time() - last_sound_time > SOUND_COOLDOWN):
                    if alert_sound and not pygame.mixer.get_busy():
                        alert_sound.play()
                    last_sound_time = time.time()

            ok, jpeg = cv2.imencode('.jpg', frame)
            if not ok:
                continue
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    except Exception as e:
        print(f"Error en el flujo de la cámara: {e}")
    finally:
        procesador.detener()
        procesador.join()
        cap.release()
        cv2.destroyAllWindows()

def camera_feed(request, camera_id, nombre):
    try:
        return StreamingHttpResponse(gen_camera_stream(camera_id, nombre),
                                     content_type='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
def deseleccionar_camara(request, camera_id):
    if camera_id not in camaras_activas:
        return JsonResponse({'error': 'La cámara no está activa o no existe.'}, status=400)
    cap = camaras_activas[camera_id]
    cap.release()
    cv2.destroyAllWindows()
    del camaras_activas[camera_id]
    return JsonResponse({'success': f'Cámara {camera_id} cerrada correctamente'}, status=200)
