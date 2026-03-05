import os
import torch
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1

# =========================
# CONFIGURACIÓN MODELO
# =========================

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

mtcnn = MTCNN(image_size=160, margin=20, keep_all=True, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "..", "dataBase", "database_embeddings.npy")
DB_PATH = os.path.abspath(DB_PATH)

if not os.path.exists(DB_PATH):
    raise RuntimeError("No se encontró database_embeddings.npy")

database = np.load(DB_PATH, allow_pickle=True).item()

# Normalizar embeddings
for k, v in list(database.items()):
    v = v.astype(np.float32)
    v = v.reshape(-1)  #  Asegura (512,)
    v = v / (np.linalg.norm(v) + 1e-12)
    database[k] = v

THRESHOLD = 0.65


# =========================
# FUNCIONES
# =========================

def get_embeddings(frame_bgr):
    """
    Recibe frame en formato BGR (OpenCV)
    Devuelve lista de (box, embedding)
    """
    img_rgb = frame_bgr[:, :, ::-1]  # BGR → RGB
    img_pil = Image.fromarray(img_rgb)

    boxes, _ = mtcnn.detect(img_pil)

    if boxes is None:
        return []

    results = []

    for box in boxes:
        x1, y1, x2, y2 = [int(b) for b in box]
        face = img_pil.crop((x1, y1, x2, y2)).resize((160, 160))

        face = torch.tensor(np.array(face)).permute(2, 0, 1).float() / 255.0

        with torch.no_grad():
            emb = resnet(face.unsqueeze(0).to(device)).cpu().numpy()[0]

        emb = emb / (np.linalg.norm(emb) + 1e-12)

        results.append((x1, y1, x2, y2, emb))

    return results


def reconocer(embedding):
    embedding = embedding.reshape(-1)  # fuerza (512,)

    best_name = "Desconocido"
    best_sim = -1

    for name, ref_emb in database.items():
        ref_emb = ref_emb.reshape(-1)  # 🔥 fuerza (512,)
        sim = float(np.dot(embedding, ref_emb))

        if sim > best_sim:
            best_sim = sim
            best_name = name

    if best_sim < THRESHOLD:
        best_name = "Desconocido"

    return best_name, best_sim

def procesar_frame(frame):
    """
    Función principal que reemplaza la API externa
    """
    faces = get_embeddings(frame)

    resultados = []

    for x1, y1, x2, y2, emb in faces:
        name, sim = reconocer(emb)
        resultados.append((x1, y1, x2, y2, name, sim))

    return resultados