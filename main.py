# Importación de bibliotecas necesarias
import json                 # Para leer datos desde archivos JSON
import pyttsx3              # Para síntesis de voz (texto a voz)
from unidecode import unidecode  # Para eliminar acentos en los textos
from experta import *       # Para construir el sistema experto basado en reglas

# Ruta del archivo JSON que contiene las enfermedades
RUTA_JSON = 'enfermedades.json'

# Clase que representa una enfermedad
class Enfermedad:
    def __init__(self, nombre, sintomas, gravedad, farmacos):
        self.nombre = nombre
        self.sintomas = [unidecode(s.lower()) for s in sintomas]  # Normaliza los síntomas (sin acentos, minúsculas)
        self.gravedad = unidecode(gravedad.lower())               # Normaliza la gravedad
        self.farmacos = farmacos                                  # Lista de medicamentos

# Inicializa el motor de voz
engine = pyttsx3.init()
engine.setProperty('rate', 160)            # Velocidad de la voz
engine.setProperty('voice', 'spanish')     # Voz en español (puede variar según sistema operativo)

# Mensaje de bienvenida por voz y por consola
engine.say("Bienvenido al sistema experto de diagnóstico médico.")
engine.runAndWait()
print("Bienvenido al sistema experto de diagnóstico médico.")

# Carga de enfermedades desde archivo JSON
with open(RUTA_JSON, 'r', encoding="utf-8") as f:
    datos = json.load(f)

# Crea una lista de objetos Enfermedad
enfermedades = [Enfermedad(e['nombre'], e['sintomas'], e['gravedad'], e['farmacos']) for e in datos]

# Solicita al usuario los síntomas
engine.say("Por favor, escribe tus síntomas, separados por comas.")
engine.runAndWait()
entrada_sintomas = input("Síntomas: ")

# Normaliza los síntomas ingresados (minúsculas y sin acentos)
sintomas = [unidecode(s.strip().lower()) for s in entrada_sintomas.split(",") if s.strip()]
print(f"Tus síntomas detectados: {sintomas}")

# Solicita al usuario cómo se siente (nivel de gravedad)
engine.say("¿Cómo te sientes? bien, regular, mal o muy mal?")
engine.runAndWait()
respuesta_gravedad = input("¿Cómo te sientes?: ").strip().lower()

# Definición de hechos para el sistema experto
class Sintoma(Fact): pass
class Gravedad(Fact): pass

# Clase que define el motor experto de diagnóstico
class SistemaExpertoDiagnostico(KnowledgeEngine):
    def __init__(self, enfermedades):
        super().__init__()
        self.enfermedades = enfermedades
        self.resultados = []  # Guarda posibles enfermedades detectadas

    # Regla que diagnostica según gravedad y síntomas
    @Rule(Gravedad(g=MATCH.gravedad))
    def diagnosticar(self, gravedad):
        sintomas_usuario = [f["s"] for f in self.facts.values() if isinstance(f, Sintoma)]
        for enf in self.enfermedades:
            if gravedad == enf.gravedad:
                sintomas_comunes = set(sintomas_usuario) & set(enf.sintomas)
                if sintomas_comunes:
                    self.resultados.append({
                        "nombre": enf.nombre,
                        "coincidencias": len(sintomas_comunes),
                        "farmacos": enf.farmacos
                    })

    # Regla para advertencia de estado crítico
    @Rule(Gravedad(g="muy mal"))
    def alerta_gravedad(self):
        engine.say("Tu estado es crítico. Te recomiendo buscar atención médica de inmediato.")
        engine.runAndWait()
        print(" Estado crítico. Busca atención médica urgente.")

    # Regla que recomienda hidratación si hay tos
    @Rule(Sintoma(s="tos"))
    def sugerencia_hidratacion(self):
        engine.say("Recuerda mantenerte hidratado. La tos puede empeorar sin suficiente líquido.")
        engine.runAndWait()

    # Regla si no se reconoce ningún síntoma
    @Rule(NOT(Sintoma(s=MATCH.sintoma)))
    def sin_sintomas_reconocidos(self):
        engine.say("No pude reconocer los síntomas ingresados. Por favor, revisa la escritura.")
        engine.runAndWait()
        print("No se reconocieron síntomas válidos.")

# Inicializa el sistema experto
motor = SistemaExpertoDiagnostico(enfermedades)
motor.reset()  # Limpia hechos previos

# Declara el hecho de gravedad del usuario
motor.declare(Gravedad(g=respuesta_gravedad))

# Declara los síntomas como hechos, o si no hay síntomas válidos, lanza una advertencia
if sintomas:
    for sintoma in sintomas:
        motor.declare(Sintoma(s=sintoma))
else:
    motor.declare(Fact(sin_sintomas=True))  # Activa la regla de síntomas no reconocidos

# Ejecuta las reglas
motor.run()

# Muestra al usuario los resultados posibles
if motor.resultados:
    engine.say("Estas podrían ser tus enfermedades.")
    engine.runAndWait()
    print("\nPosibles enfermedades:")
    resultados_ordenados = sorted(motor.resultados, key=lambda x: x["coincidencias"], reverse=True)
    for enf in resultados_ordenados[:3]:  # Muestra solo las 3 más relevantes
        print(f"- {enf['nombre']} (coincidencias: {enf['coincidencias']})")
        print(f"  Medicamentos: {', '.join(enf['farmacos'])}")
        engine.say(f"{enf['nombre']}. Medicamentos recomendados: {', '.join(enf['farmacos'])}")
        engine.runAndWait()
else:
    # No se encontró ninguna coincidencia
    engine.say("No encontré enfermedades que coincidan con tus síntomas.")
    engine.runAndWait()
    print("No se encontró ninguna enfermedad.")
