import json
import pyttsx3
from unidecode import unidecode
from experta import *

# Ruta al archivo JSON
RUTA_JSON = 'enfermedades.json'

# Clase para representar enfermedades
class Enfermedad:
    def __init__(self, nombre, sintomas, gravedad, farmacos):
        self.nombre = nombre
        self.sintomas = [unidecode(s.lower()) for s in sintomas]
        self.gravedad = unidecode(gravedad.lower())
        self.farmacos = farmacos

# Inicializa el motor de voz
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('voice', 'spanish')  # Ajusta si no reconoce español

# Mensaje de bienvenida
engine.say("Bienvenido al sistema experto de diagnóstico médico.")
engine.runAndWait()
print("Bienvenido al sistema experto de diagnóstico médico.")

# Carga de enfermedades
with open(RUTA_JSON, 'r', encoding="utf-8") as f:
    datos = json.load(f)

# Convierte cada entrada del JSON en una instancia de la clase Enfermedad
enfermedades = [Enfermedad(e['nombre'], e['sintomas'], e['gravedad'], e['farmacos']) for e in datos]

# Entrada de síntomas
engine.say("Por favor, escribe tus síntomas, separados por comas.")
engine.runAndWait()
entrada_sintomas = input("Síntomas: ")
sintomas = [unidecode(s.strip().lower()) for s in entrada_sintomas.split(",") if s.strip()]
print(f"Tus síntomas detectados: {sintomas}")

# Entrada de gravedad
engine.say("¿Cómo te sientes? bien, regular, mal o muy mal?")
engine.runAndWait()
respuesta_gravedad = input("¿Cómo te sientes?: ").strip().lower()

# Hechos
class Sintoma(Fact): pass
class Gravedad(Fact): pass

# Sistema experto
class SistemaExpertoDiagnostico(KnowledgeEngine):
    def __init__(self, enfermedades):
        super().__init__()
        self.enfermedades = enfermedades
        self.resultados = []

# Regla que diagnostica según gravedad y síntomas
    @Rule(Gravedad(g=MATCH.gravedad))
    def diagnosticar(self, gravedad):
        sintomas_usuario = [f["s"] for f in self.facts.values() if isinstance(f, Sintoma)]   # Recopila todos los síntomas que el usuario ha ingresado
        for enf in self.enfermedades: #  # Recorre todas las enfermedades cargadas en la base de datos
            if gravedad == enf.gravedad:
                sintomas_comunes = set(sintomas_usuario) & set(enf.sintomas)
                if sintomas_comunes:
                    self.resultados.append({
                        "nombre": enf.nombre,
                        "coincidencias": len(sintomas_comunes),
                        "farmacos": enf.farmacos
                    })

    #  Estado crítico
    @Rule(Gravedad(g="muy mal"))
    def alerta_gravedad(self):
        engine.say("Tu estado es crítico. Te recomiendo buscar atención médica de inmediato.")
        engine.runAndWait()
        print(" Estado crítico. Busca atención médica urgente.")


    # No se reconoce ningún síntoma
    @Rule(NOT(Sintoma(s=MATCH.sintoma)))
    def sin_sintomas_reconocidos(self):
        engine.say("No se encontró ninguna enfermedad.")
        engine.runAndWait()
        print("No se encontró ninguna enfermedad.")

# Inicializa y ejecuta el sistema experto
motor = SistemaExpertoDiagnostico(enfermedades)
motor.reset()


# Declara hechos
print("\nHechos declarados antes de ejecutar el motor:")
print(f"Gravedad: {respuesta_gravedad}")
for sintoma in sintomas:
    print(f"- Sintoma: {sintoma}")

motor.declare(Gravedad(g=respuesta_gravedad))
if sintomas:
    for sintoma in sintomas:
        motor.declare(Sintoma(s=sintoma))
else:
    # Fuerza activación de la regla de síntomas no reconocidos
    motor.declare(Fact(sin_sintomas=True))

motor.run()

# Presentación de resultados
if motor.resultados:
    engine.say("Estas podrían ser tus enfermedades.")
    engine.runAndWait()
    print("\nPosibles enfermedades:")
    resultados_ordenados = sorted(motor.resultados, key=lambda x: x["coincidencias"], reverse=True)
    for enf in resultados_ordenados[:3]:
        print(f"- {enf['nombre']} (coincidencias: {enf['coincidencias']})")
        print(f"  Medicamentos: {', '.join(enf['farmacos'])}")
        engine.say(f"{enf['nombre']}. Medicamentos recomendados: {', '.join(enf['farmacos'])}")
        engine.runAndWait()
else:
    engine.say("No encontré enfermedades que coincidan con tus síntomas.")
    engine.runAndWait()
    print("No se encontró ninguna enfermedad.")
