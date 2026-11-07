import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. Configuración de la página
st.set_page_config(page_title="Auditor de Proyectos de Física", page_icon="🪐", layout="centered")

# 2. Configuración de API
API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))

if not API_KEY:
    st.error("Error: No se encontró la API Key de Gemini. Configúrala en la carpeta .streamlit/secrets.toml o en la terminal.")
    st.stop()

# Configuración con transport='rest' para estabilidad en Windows
genai.configure(api_key=API_KEY, transport="rest")
# Modelo activo y compatible con generateContent en v1beta
model = genai.GenerativeModel('gemini-flash-lite-latest')

# 3. Variables de estado
if "modo_profesor" not in st.session_state:
    st.session_state.modo_profesor = False

# 4. Prompts Maestros
PROMPT_ESTUDIANTE = """
Rol: Eres un Auditor Socrático de Física y Matemáticas. 
Objetivo: Evaluar el código HTML/Three.js y las evidencias fotográficas del estudiante.
Reglas: 
1. Revisa los archivos subidos. Si falta la simulación o los cálculos a mano, exige que los suban y califica con 0/10.
2. Si los archivos están bien, señala errores lógicos o físicos sin dar la respuesta directa.
3. Haz una pregunta de estrés (ej. alterar la masa, cambiar la gravedad).
4. Cierra SIEMPRE tu mensaje con el siguiente formato exacto:
--- ESTADO DE EVALUACIÓN ---
Calificación Proyectada: [X]/10
Fase: [Revisión / Defensa / Aprobado]
"""

PROMPT_PROFESOR = """
Rol: Asistente de Calificación Final de Proyectos de Física.
Usuario: Profesor titular.
Objetivo: Emitir la nota final sobre 10 basada en los archivos HTML y fotos de cálculos.
Reglas:
1. Sé flexible con errores menores de sintaxis si la física es correcta.
2. Otorga hasta 2 puntos extra (Bonus de Genialidad) si el estudiante añadió controles interactivos, variables no solicitadas (fricción del aire) o un diseño 3D complejo.
3. Estructura tu respuesta estrictamente así:
- Nota Base: [X]/10
- Puntos por Genialidad: [Y] (Justificación)
- Nota Definitiva: [X+Y]
- Resumen para el estudiante: [Párrafo empático y constructivo]
"""

# 5. Barra Lateral (Modo Profesor Oculto)
with st.sidebar:
    st.header("Acceso Administrativo")
    codigo_acceso = st.text_input("Código de validación", type="password")
    
    codigo_maestro = st.secrets.get("CODIGO_MAESTRO", "10-04")
    
    if codigo_acceso == codigo_maestro:
        st.session_state.modo_profesor = True
        st.success("Modo Evaluación de Profesor Activado")
    else:
        st.session_state.modo_profesor = False
        st.info("Modo Estudiante")

# 6. Interfaz Principal
if st.session_state.modo_profesor:
    st.title("👨‍🏫 Panel de Calificación Final")
    st.markdown("Sube los archivos definitivos del estudiante para obtener la rúbrica final flexibilizada y los puntos de genialidad.")
    prompt_activo = PROMPT_PROFESOR
else:
    st.title("🪐 Auditor de Proyectos: Simulación 3D")
    st.markdown("Sube tu archivo `.html` y las fotografías de tus cálculos manuales. El auditor revisará tu avance.")
    prompt_activo = PROMPT_ESTUDIANTE

# 7. Gestión de Archivos y Análisis
archivos_subidos = st.file_uploader("Sube tus archivos (HTML, JPG, PNG)", accept_multiple_files=True)

if st.button("Iniciar Auditoría"):
    if archivos_subidos:
        with st.spinner("Analizando archivos y evaluando modelos físicos..."):
            contenido_a_enviar = [prompt_activo]
            
            for archivo in archivos_subidos:
                if archivo.name.endswith(".html"):
                    html_texto = archivo.getvalue().decode("utf-8")
                    contenido_a_enviar.append(f"Archivo HTML ({archivo.name}):\n{html_texto}")
                elif archivo.name.endswith((".jpg", ".png", ".jpeg")):
                    img = Image.open(archivo)
                    contenido_a_enviar.append(img)
            
            try:
                respuesta = model.generate_content(contenido_a_enviar)
                st.write(respuesta.text)
            except Exception as e:
                st.error(f"Se produjo un error al procesar los archivos: {e}")
    else:
        st.warning("Por favor, sube al menos un archivo para comenzar la auditoría.")
