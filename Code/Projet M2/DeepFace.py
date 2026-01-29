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
        self.configure(bg='#f0f0f0')
        self.columnconfigure(0, weight=1)

        # Label BPM
        self.label_bpm = tk.Label(self, text="BPM: --", font=("Helvetica", 20, 'bold'), bg='#f0f0f0', fg='#333')
        self.label_bpm.grid(row=0, column=0, pady=(0,0))

        # Label Caméra
        self.camera_label = tk.Label(self, bg='#f0f0f0', bd=2, relief='solid')
        self.camera_label.grid(row=1, column=0, pady=10)

        # Label émotion
        self.label_emotion = tk.Label(self, text="Emotion: ...", font=("Arial", 20), bg='#f0f0f0', fg='#333')
        self.label_emotion.grid(row=2, column=0, pady=10)

        # Boutons Oui/Non
        self.label2 = tk.Label(self, text="Est-ce correct ?", font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
        self.label2.grid(row=3, column=0, pady=5)
        self.label2.grid_remove()

        self.butt_1 = tk.Button(self, text="Oui", font=('Arial', 14), command=self.on_yes, bg='#4CAF50', fg='white')
        self.butt_1.grid(row=4, column=0, padx=(0,100), pady=10)
        self.butt_1.grid_remove()

        self.butt_2 = tk.Button(self, text="Non", font=('Arial', 14), command=self.on_no, bg='#FF5722', fg='white')
        self.butt_2.grid(row=4, column=0, padx=(100,0), pady=10)
        self.butt_2.grid_remove()

        # Initialisation caméra
        self.cap = None
        self.global_emotion = ""
        self.bpm_readings = []
        self.negative_emotions = ["sad", "angry", "fear", "disgust"]

    # Afficher la frame et lancer caméra
    def show_it(self):
        self.master.hide_all()
        self.grid(row=1, rowspan=7, column=0, sticky="nsew")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Erreur", "Impossible d'ouvrir la caméra")
            return
        self.show_camera()
        self.update_bpm()

    def hide_it(self):
        self.grid_forget()
        if self.cap:
            self.cap.release()

    # Boucle caméra
    def show_camera(self):
        ret, frame = self.cap.read()
        if ret:
            # Redimensionner pour DeepFace
            small_frame = cv2.resize(frame, (400, 300))
            try:
                result = DeepFace.analyze(small_frame, actions=['emotion'], enforce_detection=False)
                emotion = result[0]['dominant_emotion']
                self.global_emotion = emotion
                self.label_emotion.config(text=f"Emotion: {emotion.capitalize()}")

                # Si émotion négative, afficher boutons et message
                if emotion.lower() in self.negative_emotions:
                    self.label2.grid()
                    self.butt_1.grid()
                    self.butt_2.grid()
                    # Affiche message SOS si triste
                    if emotion.lower() == "sad":
                        messagebox.showwarning(
                            "Attention",
                            "Vous semblez triste ces derniers temps. "
                            + "Peut-être devriez vous pensez à consulter."
                            + "\nContacter SOS Amitié au 01 42 96 26 26"
                            + "\nOu rendez-vous sur leur site et discuter dans un chat : "
                              "https://www.sosamitieidf.asso.fr/"
                        )

            except Exception as e:
                print("Erreur DeepFace:", e)

            # Conversion OpenCV → Tkinter
            cv2image = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)

        self.after(100, self.show_camera)

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

