import cv2

# URL de la cámara RTSP
# rtsp_url = "http://admin:Serenazgo1234@192.168.1.99/doc/page/preview.asp"
rtsp_url = "rtsp://admin:Serenazgo1234@192.168.1.93:554/stream"
cap = cv2.VideoCapture(1)
cap2 = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se puede conectar a la cámara.")
    exit()

while True:

    ret, frame = cap.read()
    ret2, frame2 = cap2.read()
    nueva4 = cv2.resize(frame, (800,600))
    nueva2 = cv2.resize(frame, (800,600))
    if not ret:
        print("No se pudo obtener el frame.")
        break

    cv2.imshow("Video en vivo", nueva4)
    cv2.imshow("Video en vivo", nueva2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()