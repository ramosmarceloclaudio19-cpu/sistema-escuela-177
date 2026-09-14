import os, qrcode
base=os.environ.get("BASE_URL","https://TU-DOMINIO")
for tipo in ("entrada","salida"):
    qrcode.make(f"{base}/{tipo}").save(f"qr_{tipo}.png")
print("QR generados.")
