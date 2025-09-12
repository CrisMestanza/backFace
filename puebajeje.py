import requests

URL = "https://fbadb501d25b.ngrok-free.app/recognize"  # <- tu URL pública
files = {"image": ("frame.jpg", open("cara.jpg","rb"), "image/jpeg")}
r = requests.post(URL, files=files, timeout=10)
print(r.json())
