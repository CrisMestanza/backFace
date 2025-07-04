import subprocess
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import torch
import numpy as np
from django.conf import settings
import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
import os

@api_view(['GET'])
def extraer_placas(request):
    # Ruta a la carpeta con las imágenes de las personas
    folder = "personasConocidas2"  # Ajusta este path según tu estructura de carpetas

    # Procesar las imágenes de las personas y extraer sus embeddings
    database_embeddings = process_person_images(folder)

    # Guardar la base de datos de embeddings
    np.save(os.path.join(settings.BASE_DIR, 'api', 'dataBase', 'database_embeddings.npy'), database_embeddings)
    print(f"Base de datos con {len(database_embeddings)} embeddings guardada en 'database_embeddings.npy'.")
    print("También paso acá")

    return Response({"output": "Todo bien"}, status=status.HTTP_200_OK)

    
    
    
    
    

# Selección automática de dispositivo (GPU o CPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Usando dispositivo: {device}")

# Inicialización de MTCNN para detección facial
mtcnn = MTCNN(image_size=160, margin=20, keep_all=False, device=device)  # keep_all=False para una sola cara por imagen

# Modelo para extracción de embeddings faciales
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)

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

def load_image(path):
    """
    Carga y convierte una imagen en formato RGB.
    """
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"No se pudo leer la imagen {path}")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img_rgb

def process_person_images(folder_path):
    database = {}
    for person_name in os.listdir(folder_path):
        person_folder = os.path.join(folder_path, person_name)
        if not os.path.isdir(person_folder):
            continue

        embeddings = []  # Lista para almacenar los embeddings de esta persona
        for filename in os.listdir(person_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(person_folder, filename)
                print(f"Procesando {filename} de {person_name}...")
                img_rgb = load_image(path)

                face_tensor = mtcnn(img_rgb)
                if face_tensor is None:
                    print(f"No se detectó cara en {filename}. Se omitirá.")
                    continue

                embedding = get_embedding(face_tensor)
                embeddings.append(embedding)  # Añadir el embedding de esta imagen

        if len(embeddings) == 0:
            print(f"No se obtuvieron embeddings para {person_name}. Se omite.")
            continue

        # Promediar los embeddings de todas las imágenes de esta persona
        avg_embedding = np.mean(embeddings, axis=0)
        avg_embedding /= np.linalg.norm(avg_embedding)  # Normalizar el embedding promedio
        database[person_name] = avg_embedding

    return database

