from PIL import Image
import pytesseract
import pandas as pd
import re

# === CONFIGURAR RUTA DE TESSERACT SI ES NECESARIO ===
# En Windows puede ser algo como:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# === CARGAR IMAGEN ===
imagen = "D:\Mirko\MedicalFarma\pdfs\medicalfarma.png"
img = Image.open(imagen)

# === EXTRAER TEXTO DE LA IMAGEN ===
texto = pytesseract.image_to_string(img, lang="spa")

# === DIVIDIR TEXTO EN LÍNEAS ===
lineas = [l.strip() for l in texto.split("\n") if l.strip()]

# === EXPRESIÓN REGULAR PARA DETECTAR FILAS DE TABLA ===
pattern = re.compile(
    r"(\d+)\s+(\d+)\s+(.*?)\s+(\d{2,5}-\d{1,3})\s*\$?\s*([\d.,]+)\s*\$?\s*([\d.,]+)"
)

datos = []
for linea in lineas:
    match = pattern.search(linea)
    if match:
        rb, cant, desc, pm, unit, total = match.groups()
        datos.append({
            "RB": rb,
            "Cant.": cant,
            "DESCRIPCIÓN": desc.strip(),
            "P.M.": pm,
            "P. UNITARIO": unit,
            "PRECIO TOTAL": total
        })

# === CONVERTIR A DATAFRAME ===
df = pd.DataFrame(datos)

# === GUARDAR A EXCEL ===
df.to_excel("tabla_extraida.xlsx", index=False)

# === MOSTRAR RESULTADO EN CONSOLA ===
print(df.to_string(index=False))
print("\nArchivo generado: tabla_extraida.xlsx")
