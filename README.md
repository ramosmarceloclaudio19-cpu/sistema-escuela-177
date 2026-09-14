# Sistema real — Escuela Franca Austral N.º 177

## Qué incluye
- Página web para celulares.
- Registro inicial de personal.
- DNI + PIN personal para confirmar identidad.
- QR de entrada y QR de salida.
- Hora automática del servidor.
- Impide dos entradas abiertas.
- Impide una salida sin entrada abierta.
- Panel administrativo privado.
- Listado de personal.
- Exportación CSV compatible con Excel.
- Generación automática de QR mediante /qr/entrada.png y /qr/salida.png.

## Probar en una computadora
1. Instalar Python 3.11 o superior.
2. Abrir una terminal en esta carpeta.
3. Ejecutar: `python -m venv .venv`
4. Activar el entorno virtual.
5. Ejecutar: `pip install -r requirements.txt`
6. Definir una contraseña administrativa segura:
   - Windows PowerShell: `$env:ADMIN_PASSWORD="una-clave-segura"`
   - Linux/macOS: `export ADMIN_PASSWORD="una-clave-segura"`
7. Ejecutar: `python app.py`
8. Abrir: `http://127.0.0.1:5000`

## Para ponerlo en internet
La escuela necesitará un servicio de hosting/servidor con HTTPS. Al publicarlo, definir `BASE_URL` con la dirección definitiva, por ejemplo `https://registro.tuescuela.gob.ar` (ejemplo solamente).

Luego:
- QR entrada: `/qr/entrada.png`
- QR salida: `/qr/salida.png`

## Seguridad antes de uso oficial
Esta es una primera versión funcional de servidor, pero antes de usarla con datos reales conviene agregar:
- HTTPS obligatorio.
- Copias de seguridad automáticas.
- Roles y permisos administrativos.
- Registro de auditoría.
- Política de privacidad y conservación de datos.
- Protección contra abuso de formularios.
- Mecanismo de recuperación/cambio de PIN.
- Opcionalmente, verificación de presencia dentro del establecimiento.

NO publicar con la contraseña por defecto `CAMBIAR-ESTA-CLAVE`.
