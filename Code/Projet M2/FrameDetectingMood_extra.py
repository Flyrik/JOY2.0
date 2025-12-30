#Importing
import time
import tkinter as tk
from tkinter import messagebox
import cv2
import os
import imutils
import tensorflow as tf
import numpy as np
from PIL import Image, ImageTk
from datetime import datetime
import keras

import capteur_BPM


# Custom DepthwiseConv2D to handle deprecated 'groups' parameter
class CustomDepthwiseConv2D(keras.layers.DepthwiseConv2D):
    def __init__(self, *args, **kwargs):
        # Remove 'groups' parameter if present (deprecated in newer Keras)
        kwargs.pop('groups', None)
        super().__init__(*args, **kwargs)


# Page de détection des émotions sur 15 seconds
class FrameDetectingMood(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.final_emotion_label = None
        self.configure(bg='#f0f0f0')
        self.columnconfigure(0, weight=1)

        self.label_bpm = tk.Label(self, text="BPM: --", font=("Helvetica", 20, 'bold'), bg='#f0f0f0', fg='#333')
        self.label_bpm.grid(row=0, column=0, pady=(0, 0))

        self.cap = None
        self.camera_label = tk.Label(self, bg='#f0f0f0', bd=2, relief='solid')
        self.camera_label.grid(pady=10)

        self.label2 = tk.Label(self, text="Est-ce correct ?", font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
        self.label2.grid(pady=5)
        self.label2.grid_remove()

        self.butt_1 = tk.Button(self, text="Oui", font=('Arial', 14), command=self.on_yes, bg='#4CAF50', fg='white',
                                bd=0, highlightthickness=0, padx=20, pady=10, border=7)
        self.butt_1.grid(row=4, column=0, padx=(0, 100), pady=10)
        self.butt_1.grid_remove()

        self.butt_2 = tk.Button(self, text="Non", font=('Arial', 14), command=self.on_no, bg='#FF5722', fg='white',
                                bd=0, highlightthickness=0, padx=20, pady=10, border=7)
        self.butt_2.grid(row=4, column=0, padx=(100, 0), pady=10)
        self.butt_2.grid_remove()

        self.img_size = 100

        self.gender = open(self.master.PathToUserFile, 'r').readlines()[3][14:-2]
        if self.gender == "Homme":
            self.Emotions = ["Neutre", "Triste", "Stressé", "En colere", "Heureux"]
        elif self.gender == "Femme":
            self.Emotions = ["Neutre", "Triste", "Stressée", "En colere", "Heureuse"]
        else:
            self.Emotions = ["Neutre", "Triste", "Stressé-e", "En colere", "Heureux-se"]

        if not os.path.exists("Source/img"):
            os.makedirs("Source/img")
        if not os.path.exists("Source/Models"):
            os.makedirs("Source/Models")

        # Load model with custom objects to handle deprecated parameters
        custom_objects = {'DepthwiseConv2D': CustomDepthwiseConv2D}
        
        if os.path.exists("Source/Models/new_model.h5"):
            self.loaded_model = tf.keras.models.load_model(f"Source/Models/new_model.h5", custom_objects=custom_objects)
        else:
            self.loaded_model = tf.keras.models.load_model(f"Source/Models/model2.h5", custom_objects=custom_objects)
        self.emotion = ""
        self.emotions = [0 for _ in self.Emotions]
        self.global_emotion = ""
        self.photo_count = 0
        self.emotion_count = 0

    # Affiche la caméra
    # Met à jour le label de l'émotion
    def show_camera(self, counter=5):
        cnt = 0
        time_now = datetime.now().second
        while True:
            ret, frame = self.cap.read()
            cnt, time_now = self.update_emotion(ret, frame, cnt, counter, time_now)
            frame = imutils.resize(frame, width=400)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
            if not self.cap.isOpened():
                break

    # Prédit l'émotion
    def update_emotion(self, ret, frame, count, counter, time_now):
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            time_wait = (time_now + 1) % 60
            for x, y, w, h in faces:
                roi_color = frame[y:y + h, x:x + w]

                try:
                    face_roi = cv2.resize(roi_color, (self.img_size, self.img_size))
                    face_roi = face_roi / 255.0  # Normalisation
                    face_roi = np.expand_dims(face_roi, axis=0)  # Ajouter une dimension pour le batch

                    if datetime.now().second >= time_wait:
                        prediction = self.loaded_model.predict(face_roi)

                        # Influencer l'émotion basée sur le BPM
                        if capteur_BPM.bpm > 100:  # Seuil BPM pour l'émotion élevée
                            prediction[0][self.Emotions.index("En colere")] += 0.1
                            prediction[0][self.Emotions.index("Stressé")] += 0.1

                        self.emotion = self.Emotions[np.argmax(prediction)]
                        filename = f"Source/Img/photo_{count}.jpg"
                        cv2.imwrite(filename, face_roi)

                        self.emotions[np.argmax(prediction)] += 1
                        time_now = time_wait
                        count += 1

                        print(time_now, time_wait, count, counter)
                        if count >= counter:
                            self.global_emotion = self.Emotions[np.argmax(self.emotions)]
                            self.stop_camera()

                    cv2.putText(frame, self.emotion, (x, y), cv2.FONT_HERSHEY_TRIPLEX, 1, (150, 10, 5))
                except Exception as e:
                    print(f"Error: {e}")

                cv2.rectangle(frame, (x, y), (x + w, y + h), (250, 50, 5), 2)  # Ajout de l'encadrement

        return count, time_now

    # Libère la caméra
    def stop_camera(self):
        self.cap.release()
        self.camera_label.grid_remove()
        self.label_bpm.grid_remove()
        self.label2.grid()
        self.butt_1.grid()
        self.butt_2.grid()
        self.final_emotion_label = tk.Label(self, text=f"Tu sembles {self.global_emotion}",
                                            font=("Helvetica", 24, 'bold'),
                                            bg='#f0f0f0', fg='#333')
        self.final_emotion_label.grid(row=2, column=0, pady=(20, 10))

    # Si c'est la bonne émotion détecter → Frame activités
    def on_yes(self):
        print("prt: Yes")
        img_folder = "Source/Img"
        for file in os.listdir(img_folder):
            try:
                os.remove(img_folder + '/' + file)
            except Exception as e:
                print(f"Error while deleting file : {e}")
        self.master.frame_history.history.write_record(capteur_BPM.bpm, self.global_emotion)
        self.master.frame_activities.activities_by_emotion(self.global_emotion)
        self.master.frame_activities.show_it()
        # APPEL FONCTION POUR FAIRE LA MOYENNE DE L'HISTORIQUE ICI
        if self.master.frame_history.history.check_negative_emotions_threshold(threshold=15, days=10):
            last_warning_date = self.master.frame_history.history.get_last_warning_date()
            if last_warning_date != datetime.date.today():
                self.master.frame_history.history.set_last_warning_date()
                messagebox.showwarning("Attention", "Vous semblez triste ces derniers temps. "
                                       + "Peut-être devriez vous pensez à consulter."
                                       + "\nContacter SOS Amitié au 01 42 96 26 26"
                                       + "\nOu rendez-vous sur leur site et discuter dans un chat : "
                                         "https://www.sosamitieidf.asso.fr/")

    # Si c'est non, on demande de quelle émotion il s'agit
    def on_no(self):
        print("prt: No")
        self.master.frame_feeling_mood.show_it()

    # Met à jour le BPM
    def update_bpm(self):
        if capteur_BPM.bpm > 0:  # Inclure le BPM dès qu'il est supérieur à 0
            self.bpm_readings.append(capteur_BPM.bpm)
            if len(self.bpm_readings) > 5:
                self.bpm_readings.pop(0)

            average_bpm = sum(self.bpm_readings) / len(self.bpm_readings)
            self.label_bpm.config(text=f"BPM: {average_bpm:.2f}")
            if average_bpm > 100:  # Seuil BPM pour lancer la vidéo
                capteur_BPM.launch_video()
            self.after(1000, self.update_bpm)
        else:
            self.after(1000, self.update_bpm)

    # Montrer
    def show_it(self):
        if os.path.exists(self.master.PathToUserFile):
            self.master.hide_all()
            self.grid(row=1, rowspan=10, column=0, sticky="nsew")
            # On remet correctement les widgets
            self.cap = cv2.VideoCapture(0)

            self.show_camera()
            # self.update_emotion()
            self.update_bpm()

    # Cacher
    def hide_it(self):
        self.grid_forget()
        # Reset la detection
        # EST-CE QUE J'AI BESOIN DE RE-LOAD LE MODEL ?
        # if os.path.exists("Source/Models/new_model.h5"):
        #     self.loaded_model = tf.keras.models.load_model(f"Source/Models/new_model.h5")
        self.label_bpm.grid(row=0, column=0, pady=(0, 0))
        self.camera_label.grid(pady=10)
        self.label2.grid_remove()
        self.butt_1.grid_remove()
        self.butt_2.grid_remove()
        try:
            self.final_emotion_label.grid_remove()
            self.final_emotion_label = None
        except:
            pass

        self.emotion = ""
        self.emotions = [0 for _ in self.Emotions]
        self.global_emotion = ""
        self.photo_count = 0
        self.emotion_count = 0


# Page pour signaler une erreur dans votre émotion détectée
class FrameFeelingMood(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.img_size = 100
        self.gender = open(self.master.PathToUserFile, 'r').readlines()[3][14:-2]
        if self.gender == "Homme":
            self.Emotions = ["Neutre", "Triste", "Stressé", "En colere", "Heureux"]
        elif self.gender == "Femme":
            self.Emotions = ["Neutre", "Triste", "Stressée", "En colere", "Heureuse"]
        else:
            self.Emotions = ["Neutre", "Triste", "Stressé-e", "En colere", "Heureux-se"]

        self.configure(bg='#f0f0f0')  # Couleur de fond pour rendre la frame plus agréable
        self.columnconfigure(0, weight=1)

        # Titre de la section
        self.label1 = tk.Label(self, text="Tu te sens ...", font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
        self.label1.grid(padx=(40, 0), pady=20)

        # Boutons pour exprimer les émotions avec des commandes différentes pour chaque bouton
        self.butt_1 = tk.Button(self, text=self.Emotions[0] + " 😊", font=('Arial', 12), width=10, height=2,
                                command=lambda: self.Re_fit(0), bg='#555555', fg='white', bd=0,
                                highlightthickness=0, padx=10, pady=10, border=7)
        self.butt_1.grid(row=1, column=0, padx=(20, 200), pady=10)

        self.butt_2 = tk.Button(self, text=self.Emotions[1] + " 😔", font=('Arial', 12), width=10, height=2,
                                command=lambda: self.Re_fit(1), bg='#00AADD', fg='white', bd=0,
                                highlightthickness=0, padx=10, pady=10, border=7)
        self.butt_2.grid(row=1, column=0, padx=(200, 0), pady=10)

        self.butt_3 = tk.Button(self, text=self.Emotions[2] + " 😖", font=('Arial', 12), width=10, height=2,
                                command=lambda: self.Re_fit(2), bg='#22CC22', fg='white', bd=0,
                                highlightthickness=0, padx=10, pady=10, border=7)
        self.butt_3.grid(pady=10)

        self.butt_4 = tk.Button(self, text=self.Emotions[3] + " 😠", font=('Arial', 12), width=10, height=2,
                                command=lambda: self.Re_fit(3), bg='#FF0000', fg='white', bd=0,
                                highlightthickness=0, padx=10, pady=10, border=7)
        self.butt_4.grid(row=3, column=0, padx=(20, 200), pady=10)

        self.butt_5 = tk.Button(self, text=self.Emotions[4] + " 😀", font=('Arial', 12), width=10, height=2,
                                command=lambda: self.Re_fit(4), bg='#FFAA00', fg='white', bd=0,
                                highlightthickness=0, padx=10, pady=10, border=7)
        self.butt_5.grid(row=3, column=0, padx=(200, 0), pady=10)

    # Entraine le model si la mauvaise emotion est détecter
    def Re_fit(self, label):
        self.master.frame_history.history.write_record(capteur_BPM.bpm, self.Emotions[label])
        path_img = f"Source/img/"  # chemin du dossier contenant les nouvelles images
        path_model = f"Source/Models"  # chemin du dossier contenant les modèles

        print(os.listdir(path_img))
        x = []
        for i in os.listdir(path_img):
            img_array = cv2.imread(path_img + i)
            new_array = cv2.resize(img_array, (100, 100))
            x.append(new_array)
            os.remove(path_img + i)

        X = np.array(x)
        y = np.array([label for _ in range(len(X))])

        self.master.frame_activities.activities_by_emotion(self.Emotions[label])
        self.master.frame_activities.show_it()

        # New training
        self.master.frame_detect.loaded_model.trainable = False  # freeze the model

        self.master.frame_detect.loaded_model.fit(X, y, epochs=4)  # create the new model

        self.master.frame_detect.loaded_model.save(path_model + "/new_model.h5")  # save th new model

        # APPEL FONCTION POUR FAIRE LA MOYENNE DE L'HISTORIQUE ICI
        # Message d'alerte trop d'émotion negative
        if self.master.frame_history.history.check_negative_emotions_threshold(threshold=15, days=10):
            last_warning_date = self.master.frame_history.history.get_last_warning_date()
            if last_warning_date != datetime.date.today():
                self.master.frame_history.history.set_last_warning_date()
                messagebox.showwarning("Attention", "Vous semblez triste ces derniers temps. "
                                       + "Peut-être devriez vous pensez à consulter."
                                       + "\nContacter SOS Amitié au 01 42 96 26 26"
                                       + "\nOu rendez-vous sur leur site et discuter dans un chat : "
                                         "https://www.sosamitieidf.asso.fr/")

    # Montrer
    def show_it(self):
        if os.path.exists(self.master.PathToUserFile):
            self.master.hide_all()
            self.grid(row=1, rowspan=7, column=0, sticky="nsew")

    # Cacher
    def hide_it(self):
        self.grid_forget()
