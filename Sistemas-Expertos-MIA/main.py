import json
import speech_recognition as sr
from unidecode import unidecode
import pyttsx3

RUTA_JSON = 'enfermedades.json'

# Clase para representar una enfermedad
class Enfermedad:
    def __init__(self, nombre, sintomas, gravedad, farmacos):
        self.nombre = nombre
        self.sintomas = sintomas
        self.gravedad = gravedad
        self.farmacos = farmacos

# Inicializar el motor de voz
engine = pyttsx3.init()
engine.say("Bienvenido al sistema experto de diagnóstico médico básico.")
engine.runAndWait()
print("Bienvenido al sistema experto de diagnóstico médico básico.")

# Cargar enfermedades desde JSON
with open(RUTA_JSON, 'r', encoding="utf-8") as f:
    datos = json.load(f)

# Crear una lista de objetos Enfermedad y un conjunto de todos los síntomas conocidos
enfermedades = []
sintomas_conocidos = set()

# Recorrer cada enfermedad en el JSON y extraer los síntomas normalizados (sin acentos)
for e in datos:
    enfermedad = Enfermedad(e['nombre'], e['sintomas'], e['gravedad'], e['farmacos'])
    enfermedades.append(enfermedad)
    for s in e['sintomas']:
        sintomas_conocidos.add(unidecode(s.lower()))

# Configuración para capturar entrada de voz del usuario
reconocedor = sr.Recognizer()
with sr.Microphone() as source:
    engine.say("Por favor, menciona tus síntomas.")
    engine.runAndWait()
    print("Escuchando síntomas...")
    audio = reconocedor.listen(source)

try:
    frase_sintomas = reconocedor.recognize_google(audio, language='es-ES')
    frase_sintomas = unidecode(frase_sintomas.strip().lower())
    print("Texto reconocido:", frase_sintomas)


    # Comparar los síntomas mencionados con los conocidos
    sintomas = []
    for sintoma in sintomas_conocidos:
        if sintoma in frase_sintomas:
            sintomas.append(sintoma)

except sr.UnknownValueError:
    print("No se entendió lo que dijiste.")
    sintomas = []
except sr.RequestError as e:
    print("Error en el reconocimiento de voz:", e)
    sintomas = []

print(f"Tus síntomas detectados: {sintomas}")

# Obtener gravedad del paciente  por voz
engine.say("¿Cómo te sientes? Por favor, responde con 'bien', 'regular' ,'mal','muy mal'.")
engine.runAndWait()

with sr.Microphone() as source:
    audio_gravedad = reconocedor.listen(source)

try:
    respuesta_gravedad = reconocedor.recognize_google(audio_gravedad, language='es-ES').lower().strip()
    print("Respuesta de gravedad:", respuesta_gravedad)
except sr.UnknownValueError:
    print("No se entendió lo que dijiste.")
    respuesta_gravedad = "regular"
except sr.RequestError as e:
    print("Error en el reconocimiento de voz:", e)
    respuesta_gravedad = "regular"

# Filtrar y contar coincidencias de síntomas + gravedad
coincidencias = []

for enfermedad in enfermedades:
    sintomas_enfermedad = [unidecode(s.lower()) for s in enfermedad.sintomas]
    sintomas_comunes = set(sintomas) & set(sintomas_enfermedad)
    if enfermedad.gravedad == respuesta_gravedad and sintomas_comunes:
        coincidencias.append({
            "nombre": enfermedad.nombre,
            "farmacos": enfermedad.farmacos,
            "cantidad": len(sintomas_comunes)
        })

# Ordenar por cantidad de síntomas coincidentes (de mayor a menor) y tomar las dos primeras
enfermedades_filtradas = sorted(coincidencias, key=lambda x: x["cantidad"], reverse=True)[:2]

# Mostrar resultados
if enfermedades_filtradas:
    engine.say("Podrías estar experimentando alguna de estas enfermedades:")
    engine.runAndWait()
    print("\nPosibles enfermedades:")
    for enf in enfermedades_filtradas:
        nombre = enf["nombre"]
        farmacos = enf["farmacos"]
        mensaje = f"{nombre}"
        print(mensaje)
        engine.say(mensaje)
        engine.runAndWait()

        medicamentos = ", ".join(farmacos)
        mensaje_medicamentos = f"Medicamentos recomendados: {medicamentos}"
        print(mensaje_medicamentos)
        engine.say(mensaje_medicamentos)
        engine.runAndWait()
else:
    engine.say("No se encontró ninguna enfermedad que coincida con tus síntomas y nivel de gravedad.")
    engine.runAndWait()
    print("No se encontró ninguna coincidencia.")
