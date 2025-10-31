import cv2
import pytesseract
import pandas as pd
import re
import unicodedata

# === Configuración ===
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
ruta_imagen = r"D:\Mirko\MedicalFarma\pdfs\imagenprueba2.png"
salida_csv = "resultado.csv"

# === 1. Preprocesamiento ===
img = cv2.imread(ruta_imagen)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
gray = cv2.bitwise_not(gray)

# === 2. OCR ===
texto = pytesseract.image_to_string(gray, lang="spa")

# === 3. Limpieza de texto general ===
# Normalizar acentos mal codificados (como “resecci�n” → “reseccion”)
texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")

# Quitar caracteres invisibles o raros
texto = texto.replace("—", "-").replace("ﬂ", "fl").replace("ﬁ", "fi")
texto = re.sub(r"[^\x00-\x7F]+", " ", texto)
texto = texto.replace("  ", " ")

# === 4. Unir líneas que pertenecen a la misma fila ===
lineas = [l.strip() for l in texto.split("\n") if l.strip()]
filas_unidas = []
fila_actual = ""

for l in lineas:
    # Si empieza con un número, probablemente sea nueva fila
    if re.match(r"^\d{1,3}\s*[| ]\s*\d+", l):
        if fila_actual:
            filas_unidas.append(fila_actual.strip())
        fila_actual = l
    else:
        # Si la línea no empieza con número, la consideramos continuación
        fila_actual += " " + l

if fila_actual:
    filas_unidas.append(fila_actual.strip())

# === 5. Extraer datos con regex flexible mejorada ===
patron_fila = re.compile(
    r"(?P<RB>\d{1,3})\s*[| ]\s*(?P<Cant>\d+)\s*[| ]\s*(?P<Descripcion>.+?)\s+"
    r"(?P<PM>\d{2,4}-\d{1,3})?\s*\$?\s*([\s]*)(?P<PUnitario>[\d\.,]+)\s*[| ]?\s*\$?\s*(?P<PrecioTotal>[\d\.,]+)",
    re.IGNORECASE,
)

filas = []
for linea in filas_unidas:
    m = patron_fila.search(linea)
    if m:
        data = m.groupdict()
        # Limpieza de precios
        data["PUnitario"] = data["PUnitario"].replace(" ", "").replace(".", "").replace(",", ".")
        data["PrecioTotal"] = data["PrecioTotal"].replace(" ", "").replace(".", "").replace(",", ".")
        filas.append(data)

# === 6. Exportar a CSV ===
df = pd.DataFrame(filas, columns=["RB", "Cant", "Descripcion", "PM", "PUnitario", "PrecioTotal"])
df.to_csv(salida_csv, sep=";", index=False, encoding="utf-8-sig")

print(f" CSV generado: {salida_csv}")
print(f" Filas detectadas: {len(df)}")

if len(df) == 0:
    print("\n No se detectaron filas válidas. Mostrando líneas unidas para depurar:")
    for l in filas_unidas:
        print(">", l)
