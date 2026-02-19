import streamlit as st
import requests
import random

# Configuración de la página
st.set_page_config(page_title="Guess Who Familiar", layout="wide")

# --- CONFIGURACIÓN DE GITHUB ---
# REEMPLAZA ESTOS DATOS CON LOS TUYOS
USER = "drshadow84" 
REPO = "who-is-that-pkm"
FOLDER = "photos"

st.title("🕵️‍♂️ Guess Who? - Edición PKM")

# Función para traer las fotos de GitHub
@st.cache_data
def cargar_personajes():
    try:
        url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FOLDER}"
        res = requests.get(url)
        if res.status_code == 200:
            return [f['name'] for f in res.json() if f['name'].lower().endswith(('jpg', 'png', 'jpeg'))]
        return []
    except:
        return []

personajes = cargar_personajes()

# --- ESTADOS DEL JUEGO (Individuales por jugador) ---
if 'eliminados' not in st.session_state:
    st.session_state.eliminados = set()

if 'mi_personaje' not in st.session_state:
    st.session_state.mi_personaje = None

# --- BARRA LATERAL (Menú de controles) ---
with st.sidebar:
    st.header("Controles")
    
    # Opción 1: Sortear Personaje
    if st.button("🎲 Sortear mi personaje"):
        if personajes:
            st.session_state.mi_personaje = random.choice(personajes)
        else:
            st.error("No hay fotos cargadas.")

    # Mostrar el personaje secreto si ya fue sorteado
    if st.session_state.mi_personaje:
        nombre_secreto = st.session_state.mi_personaje.split('.')[0].replace("_", " ").title()
        url_secreta = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{FOLDER}/{st.session_state.mi_personaje}"
        st.write("---")
        st.success(f"Tu personaje es: **{nombre_secreto}**")
        st.image(url_secreta, width=150)
        st.caption("🤫 ¡No se lo muestres a nadie!")
    
    st.write("---")
    
    # Opción 2: Reiniciar Tablero
    if st.button("🔄 Reiniciar Partida"):
        st.session_state.eliminados = set()
        st.session_state.mi_personaje = None
        st.rerun()
    
    st.write("---")
    modo_movil = st.checkbox("Optimizar para Celular", value=True)

# --- TABLERO PRINCIPAL ---
# --- LÓGICA DE ORGANIZACIÓN ---
if not personajes:
    st.info("💡 Esperando fotos... Asegúrate de subir archivos a la carpeta /fotos.")
else:
    # 1. Separamos los personajes en dos listas
    sospechosos = [p for p in personajes if p not in st.session_state.eliminados]
    descartados = [p for p in personajes if p in st.session_state.eliminados]

    n_cols = 2 if modo_movil else 5

    # --- SECCIÓN 1: SOSPECHOSOS (Arriba) ---
    st.subheader(f"🔍 Sospechosos ({len(sospechosos)})")
    if sospechosos:
        cols_sos = st.columns(n_cols)
        for idx, foto in enumerate(sospechosos):
            nombre = foto.split('.')[0].replace("_", " ").title()
            url_foto = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{FOLDER}/{foto}"
            with cols_sos[idx % n_cols]:
                st.image(url_foto, caption=nombre, use_container_width=True)
                if st.button(f"🚫 Descartar", key=f"hide_{foto}"):
                    st.session_state.eliminados.add(foto)
                    st.rerun()
    else:
        st.write("¡Has descartado a todos! ¿Ya sabes quién es?")

    st.markdown("---") # Línea divisoria visual

    # --- SECCIÓN 2: DESCARTADOS (Abajo) ---
    if descartados:
        with st.expander("Ver personajes descartados", expanded=True):
            cols_des = st.columns(n_cols)
            for idx, foto in enumerate(descartados):
                nombre = foto.split('.')[0].replace("_", " ").title()
                url_foto = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{FOLDER}/{foto}"
                with cols_des[idx % n_cols]:
                    # Mostramos la imagen en blanco y negro (BGR para simular gris en Streamlit)
                    st.image(url_foto, caption=f"❌ {nombre}", use_container_width=True, channels="BGR")
                    if st.button(f"✅ Activar", key=f"revive_{foto}"):
                        st.session_state.eliminados.remove(foto)
                        st.rerun()

