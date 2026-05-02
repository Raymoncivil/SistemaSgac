import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def register_user(rut, name, password, role):
    url = f"{BASE_URL}/api/auth/register"
    payload = {
        "rut": rut,
        "full_name": name,
        "password": password,
        "role": role
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ Éxito: {role.upper()} creado -> RUT: {rut} | Clave: {password}")
        elif response.status_code == 400 and "ya está registrado" in response.text:
            print(f"ℹ️ Info: El {role.upper()} ({rut}) ya existe en la base de datos.")
        else:
            print(f"❌ Error al crear {role}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Error de conexión: {e}")

if __name__ == "__main__":
    print("Creando usuarios de prueba...\n")
    # 11111111-1 es un RUT matemáticamente válido para módulo 11
    register_user("11111111-1", "Admin de Prueba", "admin123", "admin")
    # 22222222-2 es un RUT matemáticamente válido para módulo 11
    register_user("22222222-2", "Usuario Normal", "user123", "user")
    print("\nYa puedes iniciar sesión en la web con estas credenciales.")
