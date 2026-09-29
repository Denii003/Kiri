import requests

# URL del endpoint protegido y tu token JWT
url = "http://127.0.0.1:8000/api/v1/users/"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJSb3NhbGlvIiwiZXhwIjoxNzg5NzA4NzQyfQ.BiIgjtEoodmzuWRdv0BPzoVXD4GOH5SaRJ8C4Ei13XM"

# Encabezados con la autenticación tipo Bearer
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {token}"
}

# Solicitud GET a la API
response = requests.get(url, headers=headers)

# Verificación de la respuesta
if response.status_code == 200:
    print(" Autenticación exitosa. Respuesta del servidor:")
    usuarios = response.json()
    print(usuarios)
else:
    print(f" Error {response.status_code}: {response.text}")