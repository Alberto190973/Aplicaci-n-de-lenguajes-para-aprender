import tkinter as tk
from tkinter import messagebox
import random
from difflib import SequenceMatcher
import sounddevice as sd
import speech_recognition as sr
import numpy as np
from GLOBALS import *

white = False
voice_window = None
voice_phrase_label = None
voice_entry = None
voice_status_label = None
voice_title = None
idioma_actual = "es"
dificultad_actual = 1
idioma_dif_label = None

# Mapeo de idiomas a códigos de Google Speech Recognition
IDIOMA_SPEECH_CODES = {
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "pt": "pt-BR",
    "ru": "ru-RU",
    "zh": "zh-CN",
    "ja": "ja-JP",
    "ko": "ko-KR",
}

# Función para cambiar el fondo de la ventana
def change_background():
    global white
    if white:
        ventana.config(bg="#222222")
        frase_label.config(bg="#222222", fg="#00ffcc")
        score_label.config(bg="#222222", fg="white")
        if idioma_dif_label is not None:
            idioma_dif_label.config(bg="#222222", fg="#00ffcc")
        if voice_window is not None:
            voice_window.config(bg="#222222")
            if voice_title is not None:
                voice_title.config(bg="#222222", fg="white")
            if voice_phrase_label is not None:
                voice_phrase_label.config(bg="#222222", fg="#00ffcc")
            if voice_status_label is not None:
                voice_status_label.config(bg="#222222", fg="#00ffcc")
        white = False
    else:
        ventana.config(bg="white")
        frase_label.config(bg="white", fg="black")
        score_label.config(bg="white", fg="black")
        if idioma_dif_label is not None:
            idioma_dif_label.config(bg="white", fg="black")
        if voice_window is not None:
            voice_window.config(bg="white")
            if voice_title is not None:
                voice_title.config(bg="white", fg="black")
            if voice_phrase_label is not None:
                voice_phrase_label.config(bg="white", fg="black")
            if voice_status_label is not None:
                voice_status_label.config(bg="white", fg="black")
        white = True


def actualizar_ventana_voz():
    global voice_phrase_label, voice_entry
    if voice_phrase_label is not None:
        voice_phrase_label.config(text=f"Traduce al inglés:\n\n{ronda_actual['es']}")
    if voice_entry is not None:
        voice_entry.delete(0, tk.END)


def actualizar_info_idioma_dificultad():
    global idioma_dif_label, idioma_actual, dificultad_actual
    if idioma_dif_label is not None:
        nombre_idioma = LANGS_NAMES.get(idioma_actual, "Desconocido")
        idioma_dif_label.config(text=f"Idioma: {nombre_idioma} | Dificultad: {dificultad_actual}")
        if white:
            idioma_dif_label.config(bg="white", fg="black")
        else:
            idioma_dif_label.config(bg="#222222", fg="#00ffcc")


def process_voice_answer(respuesta, window=None):
    global puntuacion
    correcta = ronda_actual["en"]
    similitud = SequenceMatcher(None, respuesta.lower(), correcta.lower()).ratio()
    puntos = int(similitud * 100)

    puntuacion += puntos
    score_label.config(text=f"Puntuación total: {puntuacion}")

    with open("answeredwords.txt", "a") as file:
        file.write(f"Frase: {ronda_actual['es']} | Respuesta voz: {respuesta} | Correcta: {correcta} | Puntos: {puntos}\n")

    messagebox.showinfo(
        "Resultado",
        f"Tu respuesta (voz): {respuesta}\n"
        f"Correcta: {correcta}\n\n"
        f"Precisión: {puntos}%"
        f"\nPuntuación total: {puntuacion}"
        f"\n\nGuardado en answeredwords.txt"
    )

    nueva_ronda()
    if window is not None:
        window.lift()


def grabar_respuesta_voz(window):
    global voice_entry, voice_status_label, idioma_actual
    duration = 4
    sample_rate = 16000
    try:
        voice_status_label.config(text="Grabando... habla ahora")
        window.update_idletasks()

        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()

        voice_status_label.config(text="Procesando audio...")
        window.update_idletasks()

        audio_data = recording.tobytes()
        recognizer = sr.Recognizer()
        audio = sr.AudioData(audio_data, sample_rate, 2)

        # Usar el código de idioma seleccionado
        idioma_code = IDIOMA_SPEECH_CODES.get(idioma_actual, "es-ES")
        texto = recognizer.recognize_google(audio, language=idioma_code)
        voice_entry.delete(0, tk.END)
        voice_entry.insert(0, texto)
        process_voice_answer(texto, window)
    except sr.UnknownValueError:
        messagebox.showinfo("No se entendió", "No pude reconocer tu voz. Intenta de nuevo.")
    except sr.RequestError:
        messagebox.showerror("Error", "No se pudo conectar al servicio de reconocimiento de voz.")
    except Exception as e:
        messagebox.showerror("Error", f"Error de grabación: {e}")
    finally:
        if voice_status_label is not None:
            voice_status_label.config(text="")


def open_voice_window():
    global voice_window, voice_phrase_label, voice_entry, voice_status_label
    if not ronda_actual:
        nueva_ronda()
    voice_window = tk.Toplevel(ventana)
    voice_window.title("Modo Voz")
    voice_window.geometry("500x350")
    voice_window.config(bg="#333333")

    global voice_title
    voice_title = tk.Label(
        voice_window,
        text="Modo de voz",
        font=("Arial", 16, "bold"),
        bg="#333333",
        fg="white"
    )
    voice_title.pack(pady=10)

    voice_phrase_label = tk.Label(
        voice_window,
        text=f"Traduce al inglés:\n\n{ronda_actual['es']}",
        font=("Arial", 14),
        bg="#333333",
        fg="white",
        justify="center"
    )
    voice_phrase_label.pack(pady=15)

    voice_entry = tk.Entry(
        voice_window,
        font=("Arial", 14),
        width=30
    )
    voice_entry.pack(pady=10)

    voice_status_label = tk.Label(
        voice_window,
        text="",
        font=("Arial", 12),
        bg="#333333",
        fg="#00ffcc"
    )
    voice_status_label.pack(pady=5)

    grabar_boton = tk.Button(
        voice_window,
        text="Grabar respuesta",
        font=("Arial", 12),
        command=lambda: grabar_respuesta_voz(voice_window),
        bg="#00aa88",
        fg="white"
    )
    grabar_boton.pack(pady=10)

    verificar_boton = tk.Button(
        voice_window,
        text="Verificar texto",
        font=("Arial", 12),
        command=lambda: process_voice_answer(voice_entry.get().strip(), voice_window),
        bg="#00aa88",
        fg="white"
    )
    verificar_boton.pack(pady=10)

    cerrar_boton = tk.Button(
        voice_window,
        text="Cerrar",
        font=("Arial", 12),
        command=voice_window.destroy,
        bg="#00aa88",
        fg="white"
    )
    cerrar_boton.pack(pady=10)

    voice_window.transient(ventana)

# Función para abrir la ventana de configuración
def open_language_window():
    global idioma_actual, frases
    lang_window = tk.Toplevel(ventana)
    lang_window.title("Seleccionar Idioma")
    lang_window.geometry("400x450")
    lang_window.config(bg="#333333")

    lang_label = tk.Label(
        lang_window,
        text="Selecciona un idioma:",
        font=("Arial", 14, "bold"),
        bg="#333333",
        fg="white"
    )
    lang_label.pack(pady=15)

    for lang in LANGS:
        color = COLORSFLAGS[lang]
        def select_lang(l=lang):
            global idioma_actual, frases
            idioma_actual = l
            nueva_ronda()
            actualizar_info_idioma_dificultad()
            lang_window.destroy()
        
        boton_idioma = tk.Button(
            lang_window,
            text=LANGS_NAMES[lang],
            font=("Arial", 12),
            command=select_lang,
            bg=color,
            fg="white",
            width=20,
            pady=10
        )
        boton_idioma.pack(pady=8)
    
    cerrar_lang = tk.Button(
        lang_window,
        text="Cerrar",
        font=("Arial", 12),
        command=lang_window.destroy,
        bg="#00aa88",
        fg="white"
    )
    cerrar_lang.pack(pady=15)
    lang_window.transient(ventana)


def open_difficulty_window():
    global dificultad_actual, frases
    diff_window = tk.Toplevel(ventana)
    diff_window.title("Seleccionar Dificultad")
    diff_window.geometry("400x350")
    diff_window.config(bg="#333333")

    diff_label = tk.Label(
        diff_window,
        text="Selecciona la dificultad:",
        font=("Arial", 14, "bold"),
        bg="#333333",
        fg="white"
    )
    diff_label.pack(pady=15)

    dificultades = [
        (1, "Fácil", "#90EE90"),          # Verde claro
        (2, "Normal", "#228B22"),          # Verde oscuro
        (3, "Intermedio", "#FFD700"),      # Amarillo
        (4, "Difícil", "#FF8C00"),         # Naranja
        (5, "Muy Difícil", "#FF0000"),     # Rojo
    ]

    for nivel, nombre, color in dificultades:
        def select_difficulty(n=nivel):
            global dificultad_actual, frases
            dificultad_actual = n
            frases = frases_por_dificultad[n]
            nueva_ronda()
            actualizar_info_idioma_dificultad()
            diff_window.destroy()
        
        boton_dificultad = tk.Button(
            diff_window,
            text=f"{nombre} (Nivel {nivel})",
            font=("Arial", 12, "bold"),
            command=select_difficulty,
            bg=color,
            fg="black" if nivel == 3 else "white",
            width=20,
            pady=10
        )
        boton_dificultad.pack(pady=8)
    
    cerrar_diff = tk.Button(
        diff_window,
        text="Cerrar",
        font=("Arial", 12),
        command=diff_window.destroy,
        bg="#00aa88",
        fg="white"
    )
    cerrar_diff.pack(pady=15)
    diff_window.transient(ventana)


def opennewwindow():
    new_window = tk.Toplevel(ventana)
    new_window.title("Configuración")
    new_window.geometry("600x500")
    new_window.config(bg="#333333")

    config_label = tk.Label(
        new_window,
        text="Aquí puedes configurar el juego",
        font=("Arial", 14),
        bg="#333333",
        fg="white"
    )
    config_label.pack(pady=20)
    
    boton_color = tk.Button(
        new_window,
        text="Cambiar fondo",
        font=("Arial", 12),
        command=lambda: change_background()
        ,bg="#00aa88",
        fg="white"
    )
    boton_color.pack(pady=10)
    
    boton_cerrar = tk.Button(
        new_window,
        text="Cerrar",
        font=("Arial", 12),
        command=new_window.destroy,
        bg="#00aa88",
        fg="white"
    )
    boton_cerrar.pack(pady=10)

# Lista de frases por dificultad (1-5)
frases_por_dificultad = {
    1: [
        {"es": "Hola", "en": "Hello"},
        {"es": "Sí", "en": "Yes"},
        {"es": "No", "en": "No"},
        {"es": "Agua", "en": "Water"},
        {"es": "Fuego", "en": "Fire"},
    ],
    2: [
        {"es": "Buenos días", "en": "Good morning"},
        {"es": "Buenas noches", "en": "Good night"},
        {"es": "Por favor", "en": "Please"},
        {"es": "Gracias", "en": "Thank you"},
        {"es": "De nada", "en": "You're welcome"},
    ],
    3: [
        {"es": "¿Cómo estás?", "en": "How are you?"},
        {"es": "¿Cuál es tu nombre?", "en": "What is your name?"},
        {"es": "¿Dónde vives?", "en": "Where do you live?"},
        {"es": "Me gusta aprender", "en": "I like learning"},
        {"es": "¿Hablas inglés?", "en": "Do you speak English?"},
    ],
    4: [
        {"es": "¿Dónde está la escuela?", "en": "Where is the school?"},
        {"es": "Tengo hambre", "en": "I am hungry"},
        {"es": "¿Cuál es la hora?", "en": "What time is it?"},
        {"es": "Me encanta la música", "en": "I love music"},
        {"es": "¿Cuántos años tienes?", "en": "How old are you?"},
    ],
    5: [
        {"es": "La educación es fundamental para el desarrollo de una sociedad", "en": "Education is essential for the development of society"},
        {"es": "¿Podrías ayudarme a entender este concepto complejo?", "en": "Could you help me understand this complex concept?"},
        {"es": "Estoy interesado en aprender sobre la historia y la cultura", "en": "I am interested in learning about history and culture"},
        {"es": "¿Cuáles son tus perspectivas sobre el futuro?", "en": "What are your perspectives on the future?"},
        {"es": "La comunicación efectiva es clave en el mundo moderno", "en": "Effective communication is key in the modern world"},
    ]
}

frases = frases_por_dificultad[1]

puntuacion = 0
ronda_actual = {}

def nueva_ronda():
    global ronda_actual
    ronda_actual = random.choice(frases)
    frase_label.config(text=f"Traduce al inglés:\n\n{ronda_actual['es']}")
    entrada.delete(0, tk.END)
    actualizar_ventana_voz()


def revisar():
    global puntuacion

    respuesta = entrada.get().strip()
    correcta = ronda_actual["en"]

    similitud = SequenceMatcher(None, respuesta.lower(), correcta.lower()).ratio()
    puntos = int(similitud * 100)

    puntuacion += puntos
    score_label.config(text=f"Puntuación total: {puntuacion}")
    
    with open("answeredwords.txt", "a") as file:
        file.write(f"Frase: {ronda_actual['es']} | Respuesta: {respuesta} | Correcta: {correcta} | Puntos: {puntos}\n")

    messagebox.showinfo(
        "Resultado",
        f"Tu respuesta: {respuesta}\n"
        f"Correcta: {correcta}\n\n"
        f"Precisión: {puntos}%"
        f"\nPuntuación total: {puntuacion}"
        f"\n\nGuardado en answeredwords.txt"
    )

    nueva_ronda()

# Ventana principal
ventana = tk.Tk()
ventana.title("Juego de Idiomas")
ventana.geometry("1200x800")
ventana.config(bg="#222222")

titulo = tk.Label(
    ventana,
    text="🌍 Aprende Idiomas Jugando",
    font=("Arial", 18, "bold"),
    bg="#222222",
    fg="white"
)
titulo.pack(pady=10)

frase_label = tk.Label(
    ventana,
    text="",
    font=("Arial", 14),
    bg="#222222",
    fg="#00ffcc"
)
frase_label.pack(pady=20)

entrada = tk.Entry(
    ventana,
    font=("Arial", 14),
    width=30
)
entrada.pack(pady=10)

boton = tk.Button(
    ventana,
    text="Comprobar",
    font=("Arial", 12),
    command=revisar,
    bg="#00aa88",
    fg="white"
)
boton.pack(pady=10)

score_label = tk.Label(
    ventana,
    text="Puntuación total: 0",
    font=("Arial", 12),
    bg="#222222",
    fg="white"
)
score_label.pack(pady=20)

idioma_dif_label = tk.Label(
    ventana,
    text=f"Idioma: Español | Dificultad: 1",
    font=("Arial", 10),
    bg="#222222",
    fg="#00ffcc"
)
idioma_dif_label.pack(pady=5)

idioma_boton = tk.Button(
    ventana,
    text="Seleccionar Idioma",
    font=("Arial", 12),
    command=open_language_window,
    bg="#00aa88",
    fg="white"
)
idioma_boton.pack(pady=8)

dificultad_boton = tk.Button(
    ventana,
    text="Seleccionar Dificultad",
    font=("Arial", 12),
    command=open_difficulty_window,
    bg="#00aa88",
    fg="white"
)
dificultad_boton.pack(pady=8)

config_boton = tk.Button(
    ventana,
    text="Configurar",
    font=("Arial", 12),
    command=lambda: opennewwindow(),
    bg="#00aa88",
    fg="white"
)
config_boton.pack(pady=8)

voice_mode_boton = tk.Button(
    ventana,
    text="Modo voz",
    font=("Arial", 12),
    command=lambda: open_voice_window(),
    bg="#00aa88",
    fg="white"
)
voice_mode_boton.pack(pady=8)

nueva_ronda()
actualizar_info_idioma_dificultad()

ventana.mainloop()
