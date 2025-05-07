# Importación de módulos necesarios
import json  # Para leer archivos JSON
import pyttsx3  # Para síntesis de voz (texto a voz)
from unidecode import unidecode  # Para eliminar acentos y caracteres especiales
from experta import *  # Librería para construir sistemas expertos basados en reglas

# Ruta al archivo JSON que contiene los datos de enfermedades
RUTA_JSON = 'enfermedades.json'

# Clase que representa una enfermedad
class Enfermedad:
    def __init__(self, nombre, sintomas, gravedad, farmacos):
        self.nombre = nombre
        # Normaliza los síntomas (sin acentos y en minúsculas)
        self.sintomas = [unidecode(s.lower()) for s in sintomas]
        # Normaliza la gravedad
        self.gravedad = unidecode(gravedad.lower())
        self.farmacos = farmacos  # Lista de medicamentos recomendados

# Inicializa el motor de voz
engine = pyttsx3.init()
engine.setProperty('rate', 160)  # Configura velocidad del habla
engine.setProperty('voice', 'spanish')  # Voz en español (puede necesitar ajuste en algunos sistemas)

# Mensaje de bienvenida
engine.say("Bienvenido al sistema experto de diagnóstico médico básico.")
engine.runAndWait()
print("Bienvenido al sistema experto de diagnóstico médico básico.")

# Carga de enfermedades desde archivo JSON
with open(RUTA_JSON, 'r', encoding="utf-8") as f:
    datos = json.load(f)

# Convierte cada entrada del JSON en una instancia de la clase Enfermedad
enfermedades = []
for e in datos:
    enfermedad = Enfermedad(e['nombre'], e['sintomas'], e['gravedad'], e['farmacos'])
    enfermedades.append(enfermedad)

# Solicita al usuario que escriba sus síntomas
engine.say("Por favor, escribe tus síntomas, separados por comas.")
engine.runAndWait()
print("Escribe tus síntomas, separados por comas (por ejemplo: dolor de cabeza, fiebre, tos):")
entrada_sintomas = input("Síntomas: ")

# Normaliza los síntomas ingresados por el usuario
sintomas = [unidecode(s.strip().lower()) for s in entrada_sintomas.split(",")]
print(f"Tus síntomas detectados: {sintomas}")

# Pregunta al usuario sobre su estado general (gravedad)
engine.say("¿Cómo te sientes? Responde con 'bien', 'regular', 'mal', o 'muy mal'.")
engine.runAndWait()
respuesta_gravedad = input("¿Cómo te sientes? (bien, regular, mal, muy mal): ").strip().lower()

# Definición de hechos en el sistema experto (clases base)
class Sintoma(Fact):
    pass  # Hecho que representa un síntoma

class Gravedad(Fact):
    pass  # Hecho que representa el nivel de gravedad percibido

# Definición del motor del sistema experto usando Experta
class SistemaExpertoDiagnostico(KnowledgeEngine):
    def __init__(self, enfermedades):
        super().__init__()
        self.enfermedades = enfermedades  # Lista de enfermedades conocidas
        self.resultados = []  # Enfermedades que coinciden con los hechos

    # Regla principal: compara gravedad y síntomas con las enfermedades conocidas
    @Rule(Gravedad(g=MATCH.gravedad))
    def diagnosticar(self, gravedad):
        # Extrae los síntomas que el usuario ha declarado
        sintomas_usuario = [f["s"] for f in self.facts.values() if isinstance(f, Sintoma)]
        for enf in self.enfermedades:
            if gravedad == enf.gravedad:
                # Encuentra coincidencias entre síntomas del usuario y la enfermedad
                sintomas_comunes = set(sintomas_usuario) & set(enf.sintomas)
                if sintomas_comunes:
                    # Guarda resultados con número de coincidencias y medicamentos sugeridos
                    self.resultados.append({
                        "nombre": enf.nombre,
                        "coincidencias": len(sintomas_comunes),
                        "farmacos": enf.farmacos
                    })

# Inicializa el motor experto con las enfermedades cargadas
motor = SistemaExpertoDiagnostico(enfermedades)
motor.reset()  # Limpia hechos anteriores

# Declara el hecho de gravedad del paciente
motor.declare(Gravedad(g=respuesta_gravedad))

# Declara todos los síntomas que el usuario ingresó
for sintoma in sintomas:
    motor.declare(Sintoma(s=sintoma))

# Ejecuta las reglas para inferir posibles enfermedades
motor.run()

# Muestra los resultados al usuario
if motor.resultados:
    engine.say("Estas podrían ser tus enfermedades:")
    engine.runAndWait()
    print("\nPosibles enfermedades:")

    # Ordena por número de síntomas que coinciden
    resultados_ordenados = sorted(motor.resultados, key=lambda x: x["coincidencias"], reverse=True)

    # Muestra solo las 3 más relevantes
    for enf in resultados_ordenados[:3]:
        print(f"- {enf['nombre']} (coincidencias: {enf['coincidencias']})")
        print(f"  Medicamentos: {', '.join(enf['farmacos'])}")
        engine.say(f"{enf['nombre']}. Medicamentos recomendados: {', '.join(enf['farmacos'])}")
        engine.runAndWait()
else:
    # Si no se encontraron coincidencias
    print("No se encontró ninguna enfermedad.")
    engine.say("No encontré enfermedades que coincidan con tus síntomas.")
    engine.runAndWait()
