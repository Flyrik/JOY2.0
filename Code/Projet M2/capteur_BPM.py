try:
    from gpiozero import Button
    HAS_GPIOZERO = True
except Exception:
    Button = None
    HAS_GPIOZERO = False
    # gpiozero not available (e.g., running on Windows). Pulse reading will need to be simulated.

import time
import os
import subprocess  # Pour exécuter des programmes externes

# Configuration des GPIO
#SENSOR_PIN = 17  # Modifiez cette valeur en fonction de votre configuration

# Initialisation de gpiozero
#sensor = Button(SENSOR_PIN)

# Variables globales
pulse_count = 0
bpm = 0
last_time = time.time()

# Chemin d'accès à la vidéo
video_folder = "./Video/"  # Chemin vers le dossier contenant la vidéo
video_filename = "Respiration Guidée  Calme et Paix.mp4"  # Nom du fichier vidéo à lire

# Fonction pour lire les impulsions du capteur
def read_pulse():
    global pulse_count, bpm, last_time
    pulse_count += 1
    current_time = time.time()
    interval = current_time - last_time
    last_time = current_time
    if interval > 0:
        bpm = 60 / interval

# For systems without gpiozero, provide a simple simulator for testing
if not HAS_GPIOZERO:
    def simulate_pulse():
        """Call this function to simulate a pulse (useful on Windows/dev machine)."""
        read_pulse()

# Attacher l'interruption gpiozero
#sensor.when_pressed = read_pulse

# Fonction pour lancer la vidéo
def launch_video():
    video_path = os.path.join(video_folder, video_filename)
    if os.path.exists(video_path):
        if os.name == 'posix':  # Si le système est de type Unix (Linux, macOS)
            subprocess.Popen(['vlc', video_path])  # Ouvre avec VLC
        elif os.name == 'nt':  # Si le système est Windows
            os.startfile(video_path)  # Ouvre avec le lecteur vidéo par défaut de Windows
    else:
        print(f"Le fichier vidéo '{video_filename}' n'existe pas dans le dossier '{video_folder}'.")
