# -*- coding: utf-8 -*-
# Importing
import tkinter as tk
from datetime import datetime
import os

import FrameProfilUser
import FrameParameters
import FrameHistorique
import FrameDetectingMood_extra
import FrameActivities
import FrameEachActivity
import FrameDiscussion
import Reponse_verbale
import Audio
import Generation_parole


class Application(tk.Tk):
    def __init__(self, window_size="600x1024"):
        super().__init__()
        self.title("JOY te souhaite la bienvenue !")
        self.geometry(window_size)  # Résolution de l'écran du torse pour le test
        # self.state('zoomed') # Ouvre la fenêtre à la taille de l'écran
        # --- THEME VISUEL (enfants) ---
        self.configure(bg="#FFF6E9")  # fond doux
        self.font_title = ("Arial", 22, "bold")
        self.font_text = ("Arial", 16, "bold")
        self.font_small = ("Arial", 13)

        # optionnel: homogénéiser le look des boutons (tk.Button classique)
        self.btn_style = {
            "font": self.font_text,
            "bd": 0,
            "highlightthickness": 0,
            "activebackground": "#FFE1A8",
            "cursor": "hand2",
            "padx": 14,
            "pady": 10
        }

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.PathToUserFile = "Source/user_data.json"
        lines = open("Source/Face/face.txt").readlines()
        lines[2] = "off"
        open("Source/Face/face.txt", 'w').writelines(lines)

        """ INITIALISATION DES PAGES (frames) """
        self.frame_profil_user = FrameProfilUser.FrameProfilUser(self)

        if not os.path.exists(self.PathToUserFile):
            self.info_user = FrameProfilUser.InfoUser('None', 'Any', 'Binary')
            self.frame_profil_user.show_it()  # On affiche la page de profil
        else:
            self.info_user = FrameProfilUser.InfoUser.load_from_json(self.PathToUserFile)

        self.frame_feeling_mood = FrameDetectingMood_extra.FrameFeelingMood(self)
        self.frame_history = FrameHistorique.FrameHistorique(self)
        self.frame_detect = FrameDetectingMood_extra.FrameDetectingMood(self)
        self.frame_activities = FrameActivities.FrameActivities(self)
        self.frame_accueil = FrameAccueil(self)
        self.audio = Audio
        self.audio2text = self.audio.Audio2text(self)

        self.generation = Generation_parole

        text_salutation = f"Bonjour {self.info_user.name}. Bienvenue sur JOY !"
        self.syllables = self.generation.Generation(text_salutation).Phoneme2Syllable()
        self.vitesse = 1.1
        self.timbre = .7
        self.volume = 0
        self.audio.Setting(self, script=text_salutation, vit=self.vitesse, timbre=self.timbre, volume=self.volume)

        self.on_off = False

        self.frame_parameters = FrameParameters.FrameParameters(self)

        on_off = open("Source/Face/face.txt").readlines()
        if on_off[0][-4:].strip() == "on":
            on_off[0] = "on on\n"
            self.frame_parameters.face_button.configure(text="ON", bg="#00ff00")
        else:
            on_off[0] = "off off\n"
            self.frame_parameters.face_button.configure(text="OFF", bg="#ff0000")
        open("source/Face/face.txt", 'w').writelines(on_off)

        if on_off[0][:3].strip() == "on":
            self.logo_img = "Source/Items/logo_notif_on.png"
        else:
            self.logo_img = "Source/Items/logo_notif_off.png"
        self.photo1 = tk.PhotoImage(file=self.logo_img)
        self.butt_logo = tk.Button(self, image=self.photo1, borderwidth=0, command=self.update_vocal, bg="#FFF6E9", activebackground="#FFF6E9")
        self.butt_logo.grid(row=0, column=0, sticky="n", padx=10, pady=10)

        self.salute_today = Reponse_verbale.Answer(self, "salut").Answer()
        if self.salute_today == "":
            list_salutation = ["Salut", "Bonjour", "Hey"]
            messages = open("Source/previous_messages.log", 'r').readlines()
            now = datetime.now()
            today = now.strftime("%d/%m/%Y")
            mess_auj = [messages[i - 1][4:] for i in range(1, len(messages), 2) if messages[i][:10] == today
                        and messages[i - 1][:3] == "JOY"]

            salute_today = "aujourd'hui"
            for i in list_salutation:
                for j in mess_auj:
                    if i.lower() in j.lower():
                        salute_today = "depuis"
                        break
            self.salute_today += f"Quoi de neuf {salute_today} ?"
            messages = open("Source/previous_messages.log", 'r').readlines()
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            messages.append(f"JOY:{self.salute_today}\n{current_time}\n")
            open("Source/previous_messages.log", 'w').writelines(messages)

        self.frame_discussion = FrameDiscussion.FrameDiscussion(self)
        self.frame_each_activity = FrameEachActivity.Activity(self)

        if os.path.exists(self.PathToUserFile):
            self.frame_accueil.show_it()

        """ HEURE et DATE + Bouton navigation ROOT """
        self.time_label = tk.Label(self, font=self.font_small, bg="#FFE1A8", fg="#3A2E2A")
        self.time_label.grid(row=10, column=0, columnspan=2, sticky="se", padx=10, pady=10)
        self.update_time()

        self.photo0 = tk.PhotoImage(file="Source/Items/maison.png")
        self.butt_accueil = tk.Button(self, image=self.photo0, borderwidth=0, command=self.frame_accueil.show_it, bg="#FFF6E9", activebackground="#FFF6E9")
        self.butt_accueil.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        self.photo2 = tk.PhotoImage(file="Source/Items/engrenage.png")
        self.butt_param = tk.Button(self, image=self.photo2, borderwidth=0, command=self.frame_parameters.show_it, bg="#FFF6E9", activebackground="#FFF6E9")
        self.butt_param.grid(row=0, column=0, sticky="ne", padx=10, pady=10)

        self.photo3 = tk.PhotoImage(file="Source/Items/message.png")
        self.butt_message = tk.Button(self, image=self.photo3, borderwidth=0, command=self.frame_discussion.show_it, bg="#FFF6E9", activebackground="#FFF6E9")
        self.butt_message.grid(row=7, column=0, sticky="se", padx=10, pady=10)

        self.exception = None

    # Fonction de mise à jour de l'heure en bas de l'écran
    def update_time(self):
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        self.time_label.config(text=current_time)
        self.after(1000, self.update_time)

    def update_vocal(self):
        self.audio.Jouer(self)
        on_off = open("Source/Face/face.txt").readlines()
        if on_off[0][:3].strip() == "on":
            self.logo_img = "Source/Items/logo_on.png"
        else:
            self.logo_img = "Source/Items/logo_off.png"
        self.photo1 = tk.PhotoImage(file=self.logo_img)
        self.butt_logo.configure(image=self.photo1)

    # !!! Veuillez tenir à jour la liste suivante sinon on crée un dico ou une liste à parcourir
    def hide_all(self):
        for i in [self.frame_accueil, self.frame_profil_user, self.frame_history, self.frame_feeling_mood,
                  self.frame_detect, self.frame_activities, self.frame_parameters, self.frame_each_activity,
                  self.frame_discussion]:
            try:
                i.hide_it()
            except Exception as e:
                self.exception = e


# Page de l'accueil
class FrameAccueil(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg="#FFF6E9")
        self.grid_columnconfigure(0, weight=1)
        

        # Titre
        self.label1 = tk.Label(
            self,
            text=f"🌟 Coucou {master.info_user.name} ! 🌟",
            font=("Arial", 24, "bold"),
            bg="#FFF6E9",
            fg="#2D2A32"
        )
        self.label1.grid(pady=(30, 10))

        # Sous-titre
        self.label2 = tk.Label(
            self,
            text="Comment tu te sens aujourd'hui ? 😊",
            font=("Arial", 16, "bold"),
            bg="#FFF6E9",
            fg="#555"
        )
        self.label2.grid(pady=(0, 25))

        # Bouton humeur
        self.butt_detect_mood = tk.Button(
            self,
            text="🎭 Mon humeur",
            command=self.master.frame_detect.show_it,
            bg="#7ED957", fg="white",
            activebackground="#6BCB4A",
            font=("Arial", 18, "bold"),
            bd=0, highlightthickness=0,
            padx=20, pady=16,
            cursor="hand2"
        )
        self.butt_detect_mood.grid(row=2, column=0, pady=10, ipadx=20, ipady=6)


        # Bouton historique
        self.butt_history = tk.Button(
            self,
            text="📚 Mes souvenirs",
            command=self.master.frame_history.show_it,
            bg="#5DADE2", fg="white",
            activebackground="#4F9ACB",
            font=("Arial", 18, "bold"),
            bd=0, highlightthickness=0,
            padx=20, pady=16,
            cursor="hand2"
        )
        self.butt_history.grid(row=3, column=0, pady=10, ipadx=20, ipady=6) 

       # Bouton activités
        self.master.frame_activities.activities_by_emotion("Neutre")
        self.butt_activities = tk.Button(
            self,
            text="🎮 Activités",
            command=self.master.frame_activities.show_it,
            bg="#FFB347", fg="white",
            activebackground="#E89F3B",
            font=("Arial", 18, "bold"),
            bd=0, highlightthickness=0,
            padx=20, pady=16,
            cursor="hand2"
        )
        self.butt_activities.grid(row=4, column=0, pady=10, ipadx=20, ipady=6)

    """ NE JAMAIS REFAIRE CA ::: INTERDIT """
    # def history(self):
    #     self.master.hide_all()
    #     # NE JAMAIS REFAIRE CA ::: INTERDIT
    #     # self.detect = FrameHistorique.FrameHistorique(self.master)
    #     # self.detect.show_it()

    # def activities(self):
    #     self.master.hide_all()
    #     # NE JAMAIS REFAIRE CA ::: INTERDIT
    #     # self.detect = FrameActivities.FrameActivities(self.master)
    #     # self.detect.show_it()

    # Montrer
    def show_it(self):
        if os.path.exists(self.master.PathToUserFile):
            self.master.hide_all()
            self.grid(row=1, rowspan=7, column=0, sticky="nsew")

    # Cacher
    def hide_it(self):
        self.grid_forget()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
    try:
        FrameParameters.servo.detach()
    except Exception as expt:
        exception = expt
