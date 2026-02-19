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
if not personajes:
    st.info("💡 Esperando fotos... Asegúrate de subir archivos .jpg o .png a la carpeta /fotos en tu GitHub.")
else:
    # Ajuste de columnas según el dispositivo
    n_cols = 2 if modo_movil else 5
    cols = st.columns(n_cols)
    
    for idx, foto in enumerate(personajes):
        nombre = foto.split('.')[0].replace("_", " ").title()
        url_foto = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{FOLDER}/{foto}"
        
        with cols[idx % n_cols]:
            # Si el personaje está eliminado
            if foto in st.session_state.eliminados:
                st.image(url_foto, caption=f"❌ {nombre}", use_container_width=True, channels="BGR")
                if st.button(f"✅ Activar", key=f"revive_{idx}"):
                    st.session_state.eliminados.remove(foto)
                    st.rerun()
            # Si el personaje está activo
            else:
                st.image(url_foto, caption=nombre, use_container_width=True)
                if st.button(f"🚫 Descartar", key=f"hide_{idx}"):
                    st.session_state.eliminados.add(foto)

                    st.rerun()
