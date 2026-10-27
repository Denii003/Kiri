"""Cliente de prueba: inicia sesión, obtiene un JWT y consulta un endpoint protegido.
Uso:  python script.py <usuario>   (te pedirá la contraseña)
"""
import getpass
import sys

import requests

BASE = "http://127.0.0.1:8000/api/v1/users"

username = sys.argv[1] if len(sys.argv) > 1 else input("Usuario: ")
password = getpass.getpass("Contraseña: ")

login = requests.post(f"{BASE}/token", data={"username": username, "password": password})
if login.status_code != 200:
    sys.exit(f"Error {login.status_code}: {login.text}")

headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
me = requests.get(f"{BASE}/me", headers=headers)
print("Autenticación exitosa:" if me.ok else f"Error {me.status_code}:", me.json())
