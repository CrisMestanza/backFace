import cv2
import os
import torch
from datetime import datetime
from django.http import StreamingHttpResponse, JsonResponse
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import numpy as np
import pygame
import time
import threading
from facenet_pytorch import MTCNN, InceptionResnetV1
from sklearn.metrics.pairwise import cosine_similarity
import os
from datetime import date

ruta = "media"
# Fecha de hoy (solo fecha)
hoy = date.today()

os.makedirs(os.path.join(ruta, str(hoy)), exist_ok=True)

# Lista para almacenar las cámaras activas
camaras_activas = {}

def gen_camera_stream(camera_id):
    """Generar un flujo de video desde la cámara indicada."""
    
    # Rutas de los modelos
  
    rutaModeloVehiculo = os.path.join(settings.BASE_DIR, 'api', 'dataBase', 'database_embeddings.npy')
    sonido = os.path.join(settings.BASE_DIR, 'api', 'sonido', 'alerta.mp3')

    # Selección automática de dispositivo (GPU o CPU)
    # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    device = torch.device('cuda')

    # Inicialización de MTCNN para detección facial
    mtcnn = MTCNN(image_size=160, margin=20, keep_all=True, device=device)

    # Modelo para extracción de embeddings faciales
    model = InceptionResnetV1(pretrained='vggface2').eval().to(device)

    # Sonido
    pygame.mixer.init()
    alert_sound = pygame.mixer.Sound('./sonido/alerta.mp3')
    # Variable global para controlar la frecuencia de alertas
    last_sound_time = 0
    sound_cooldown =  3 # segundos

    def play_alert():
        alert_sound.play()

    def get_embedding(face_img):
        """
        Recibe tensor [3,160,160] con imagen RGB normalizada.
        Retorna embedding facial normalizado.
        """
        face_img = face_img.unsqueeze(0).to(device)  # Añadir batch y enviar a device
        with torch.no_grad():
            embedding = model(face_img).cpu().numpy()
        embedding = embedding / np.linalg.norm(embedding)
        return embedding

    def recognize_face(embedding, database, threshold=0.40):
        """
        Compara embedding con base de datos y devuelve nombre e índice de similitud.
        """
        max_sim = -1
        identity = "Desconocido"
        for name, db_emb in database.items():
            sim = cosine_similarity(embedding.reshape(1, -1), db_emb.reshape(1, -1))[0][0]
            if sim > max_sim:
                max_sim = sim
                identity = name
        if max_sim < threshold:
            identity = "Desconocido"
        return identity, max_sim
    
    # Para proximamente guardar por el nombre de la calle
    nombre = "Jr. Manco Inca"
    
    cap = cv2.VideoCapture(camera_id)  # Ajusta índice según cámara (0,1,...)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return None
    camaras_activas[camera_id] = cap
    print("Reconocimiento facial en tiempo real. Presiona 'q' para salir.")
    
    # Cargar base de datos guardada
    database = np.load(rutaModeloVehiculo, allow_pickle=True).item()
    print(f"Base cargada con {len(database)} personas.")
    
    try:
         while True:
            ret, frame = cap.read()
            if not ret:
                print("Error al capturar frame de cámara.")
                break

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes, _ = mtcnn.detect(img_rgb)

            if boxes is not None:
                h, w, _ = img_rgb.shape
                for box in boxes:
                    try:
                        # Limitar coordenadas dentro de la imagen
                        x1, y1, x2, y2 = [int(b) for b in box]
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(w, x2), min(h, y2)
                        if x2 <= x1 or y2 <= y1:
                            continue  # bounding box inválido, saltar

                        # Recortar y preparar imagen para embedding
                        face_img = img_rgb[y1:y2, x1:x2]
                        face_img = cv2.resize(face_img, (160, 160))
                        face_tensor = torch.tensor(face_img).permute(2, 0, 1).float() / 255.0  # Convertir a tensor y normalizar

                        # Obtener embedding y reconocer persona
                        embedding = get_embedding(face_tensor)
                        name, similarity = recognize_face(embedding, database)

                        # Dibujar rectángulo y texto en imagen original
                        if name == "Desconocido":
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (255,0,0), 2)
                            cv2.putText(frame, f"{name} ({similarity:.2f})", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
                        else: 
                            
                            # Controlar el sonido con un cooldown
                            if time.time() - last_sound_time > sound_cooldown:
                                threading.Thread(target=play_alert).start()
                                last_sound_time = time.time()
                                
                            horaCompleta = datetime.now().strftime("%H-%M")
                            carpeta_persona = os.path.join(ruta, str(hoy), name, str(camera_id), horaCompleta)
                            
                            if not os.path.exists(carpeta_persona):
                            # Crear carpeta para la persona
                                
                                os.makedirs(carpeta_persona, exist_ok=True)
                                # Guardar imágenes
                                cv2.imwrite(os.path.join(carpeta_persona, f"{name}_rostro.jpg"), frame[y1:y2, x1:x2])
                                cv2.imwrite(os.path.join(carpeta_persona, f"{name}_general.jpg"), frame)

                                
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 2)
                            cv2.putText(frame, f"{name} ({similarity:.2f})", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
                    except Exception as e:
                        print(f"Error procesando rostro: {e}")
                        continue

            # Convertir el frame a JPEG y enviarlo
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue

            # Convertir la imagen a bytes y enviarla
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    except Exception as e:
        print(f"Error en el flujo de la cámara: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def camera_feed(request, camera_id):
    """Vista para mostrar el flujo de la cámara."""
    try:
        return StreamingHttpResponse(gen_camera_stream(camera_id),
                                     content_type='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def deseleccionar_camara(request, camera_id):
    print(f"Intentando cerrar la cámara {camera_id}...")
    
    # Verifica si la cámara está activa
    if camera_id not in camaras_activas:
        return JsonResponse({'error': 'La cámara no está activa o no existe.'}, status=400)
    cap = camaras_activas[camera_id]
    cap.release()

    # Cerrar todas las ventanas de OpenCV si es necesario
    cv2.destroyAllWindows()

    del camaras_activas[camera_id]
    print(f"Cámara {camera_id} cerrada correctamente.")
    return JsonResponse({'success': f'Cámara {camera_id} cerrada correctamente'}, status=200)
