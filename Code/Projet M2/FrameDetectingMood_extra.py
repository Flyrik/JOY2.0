import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2

# Simulation du module capteur_BPM
class CapteurBPM:
    bpm = 70
    @staticmethod
    def launch_video():
        print("Video triggered due to high BPM")

capteur_BPM = CapteurBPM()

class FrameDetectingMood(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.configure(bg='#FFF6E9')
        self.columnconfigure(0, weight=1)

        # Load Haar cascades
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

        # Label BPM
        self.label_bpm = tk.Label(self, text="BPM: --", font=("Helvetica", 20, 'bold'), bg="#FFF6E9", fg='#333')
        self.label_bpm.grid(row=0, column=0, pady=(0,0))

        # Label Caméra
        self.camera_label = tk.Label(self, bg='#FFF6E9', bd=2, relief='solid')
        self.camera_label.grid(row=1, column=0, pady=10)

        # Label émotion
        self.label_emotion = tk.Label(self, text="Emotion: ...", font=("Arial", 20), bg='#FFF6E9', fg='#333')
        self.label_emotion.grid(row=2, column=0, pady=10)

        # Label SOS (texte rouge)
        self.sos_label = tk.Label(
            self,
            text="",
            font=("Arial", 14, "bold"),
            bg="#FFF6E9",
            fg="red",
            wraplength=400,
            justify="left"
        )
        self.sos_label.grid(row=3, column=0, pady=10)

        # Initialisation caméra et variables
        self.cap = None
        self.global_emotion = ""
        self.bpm_readings = []

    # Afficher la frame et lancer caméra
    def show_it(self):
        self.master.hide_all()
        self.grid(row=1, rowspan=7, column=0, sticky="nsew")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Erreur", "Impossible d'ouvrir la caméra")
            return

        # Lancer caméra fluide (~30 FPS)
        self.update_camera()
        # Lancer BPM
        self.update_bpm()

    # Cacher
    def hide_it(self):
        self.grid_forget()
        if self.cap:
            self.cap.release()

    # Boucle caméra fluide
    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Détection des visages
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            emotion_text = "Neutral"

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)  # rectangle bleu autour du visage
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]

                # Détection sourire
                smiles = self.smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.7, minNeighbors=22)
                if len(smiles) > 0:
                    emotion_text = "Happy"
                    for (sx, sy, sw, sh) in smiles:
                        cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 255, 0), 2)  # rectangle vert pour sourire

            self.global_emotion = emotion_text
            self.label_emotion.config(text=f"Emotion: {emotion_text}")

            # Conversion pour Tkinter
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)

        self.after(30, self.update_camera)  # ~30 FPS

    # Boucle BPM
    def update_bpm(self):
        if capteur_BPM.bpm > 0:
            self.bpm_readings.append(capteur_BPM.bpm)
            if len(self.bpm_readings) > 5:
                self.bpm_readings.pop(0)
            average_bpm = sum(self.bpm_readings) / len(self.bpm_readings)
            self.label_bpm.config(text=f"BPM: {average_bpm:.2f}")
            if average_bpm > 100:
                capteur_BPM.launch_video()
        self.after(1000, self.update_bpm)
class FrameFeelingMood(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Frame vide pour éviter les erreurs
        pass
