# FrameDetectingMood_extra.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from deepface import DeepFace

# Simulation du module capteur_BPM (remplacer par ton vrai module)
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

        # Label BPM
        self.label_bpm = tk.Label(self, text="BPM: --", font=("Helvetica", 20, 'bold'), bg="#FFF6E9", fg='#333')
        self.label_bpm.grid(row=0, column=0, pady=(0,0))

        # Label Caméra
        self.camera_label = tk.Label(self, bg='#FFF6E9', bd=2, relief='solid')
        self.camera_label.grid(row=1, column=0, pady=10)

        # Label émotion
        self.label_emotion = tk.Label(self, text="Emotion: ...", font=("Arial", 20), bg='#FFF6E9', fg='#333')
        self.label_emotion.grid(row=2, column=0, pady=10)

        # Boutons Oui/Non
        self.label2 = tk.Label(self, text="Est-ce correct ?", font=('Arial', 18, 'bold'), bg='#FFF6E9', fg='#333')
        self.label2.grid(row=3, column=0, pady=5)
        self.label2.grid_remove()

        self.butt_1 = tk.Button(self, text="Oui", font=('Arial', 14), command=self.on_yes, bg='#4CAF50', fg='white')
        self.butt_1.grid(row=4, column=0, padx=(0,100), pady=10)
        self.butt_1.grid_remove()

        self.butt_2 = tk.Button(self, text="Non", font=('Arial', 14), command=self.on_no, bg='#FF5722', fg='white')
        self.butt_2.grid(row=4, column=0, padx=(100,0), pady=10)
        self.butt_2.grid_remove()

        # Label SOS (texte rouge)
        self.sos_label = tk.Label(
            self,
            text="",  # vide au départ
            font=("Arial", 14, "bold"),
            bg="#FFF6E9",
            fg="red",
            wraplength=400,
            justify="left"
        )
        self.sos_label.grid(row=5, column=0, pady=10)

        # Initialisation caméra et variables
        self.cap = None
        self.global_emotion = ""
        self.bpm_readings = []
        self.negative_emotions = ["sad", "angry", "fear", "disgust"]
        self.positive_emotions = ["happy", "surprise", "neutral"]

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
        # Lancer détection d'émotion 1x/sec
        self.update_emotion()
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
            small_frame = cv2.resize(frame, (400, 300))
            cv2image = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
        self.after(30, self.update_camera)  # ~30 FPS

    # Boucle détection d'émotion (1x/sec)
    def update_emotion(self):
        ret, frame = self.cap.read()
        if ret:
            small_frame = cv2.resize(frame, (400, 300))
            try:
                result = DeepFace.analyze(small_frame, actions=['emotion'], enforce_detection=False)
                emotion = result[0]['dominant_emotion'].lower()
                self.global_emotion = emotion
                self.label_emotion.config(text=f"Emotion: {emotion.capitalize()}")

                # Stabilisation pour éviter le clignotement
                if not hasattr(self, 'last_emotion'):
                    self.last_emotion = ""
                    self.emotion_count = 0

                if emotion == self.last_emotion:
                    self.emotion_count += 1
                else:
                    self.last_emotion = emotion
                    self.emotion_count = 1
                
                # Mise à jour message SOS si stable
                if self.emotion_count >= 1:
                    if emotion in self.negative_emotions + self.positive_emotions:
                        
                        self.butt_1.grid()
                        self.butt_2.grid()
                        self.label2.grid()
                        if emotion == "sad":
                            self.sos_label.config(
                                text="Vous semblez triste ces derniers temps. "
                                     "Peut-être devriez-vous penser à consulter.\n"
                                     "Contacter SOS Amitié au 01 42 96 26 26\n"
                                     "Ou rendez-vous sur leur site et discuter dans un chat : "
                                     "https://www.sosamitieidf.asso.fr/"
                            )

                        elif emotion == "happy":
                             self.sos_label.config(
                                text="Ca fait plaisir que tu sois aussi heureux ! Continue comme ça :)"
                            )
                        
                    else:
                        self.label2.grid_remove()
                        self.butt_1.grid_remove()
                        self.butt_2.grid_remove()
                        self.sos_label.config(text="")  # vide si neutre/heureux

            except Exception as e:
                print("Erreur DeepFace:", e)

        self.after(1000, self.update_emotion)  # 1x/sec

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

    # Bouton Oui
    def on_yes(self):
        messagebox.showinfo("Emotion confirmée", f"Tu sembles {self.global_emotion}")
        self.label2.grid_remove()
        self.butt_1.grid_remove()
        self.butt_2.grid_remove()
        if hasattr(self, 'show_emotion_job'):
            self.after_cancel(self.show_emotion_job)
            del self.show_emotion_job
                
        
    # Bouton Non
    def on_no(self):
        messagebox.showinfo("Info", "Merci pour ton retour, on peut corriger l'IA plus tard")
        self.label2.grid_remove()
        self.butt_1.grid_remove()
        self.butt_2.grid_remove()


# Optionnel : frame pour retour utilisateur
class FrameFeelingMood(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # Ici tu peux garder ton ancien code pour signaler si l'émotion détectée est fausse
        pass
