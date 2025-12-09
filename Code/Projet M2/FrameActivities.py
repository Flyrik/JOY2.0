import tkinter as tk
import os


# Page des activités en fonction de l'émotion
class FrameActivities(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg='#f0f0f0')  # Couleur de fond pour rendre la frame plus agréable

        # Configurer les colonnes pour centrer les widgets
        #self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Titre de la section
        self.label1 = tk.Label(self, text="Que veux-tu faire ?", font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
        self.label1.grid(row=0, column=0, sticky="ew")

    def activities_by_emotion(self, emotion):
        if emotion == "Neutre":
            self.act1 = "Vidéo drôle"
            self.act2 = "Vidéo de yoga"
            self.act3 = "Conseil"
        elif emotion == "Triste":
            self.act1 = "Excercice de\nRespiration"
            self.act2 = "Vidéo de motivation"
            self.act3 = "Conseil"
        elif emotion == "Stressé":
            self.act1 = "Excercice de\nRespiration"
            self.act2 = "Vidéo de yoga"
            self.act3 = "Conseil"
        elif emotion == "En colere":
            self.act1 = "Excercice de\nRespiration"
            self.act2 = "Vidéo de yoga"
            self.act3 = "Vidéo drôle"
        else:
            self.act1 = "Vidéo drôle"
            self.act2 = "Vidéo de yoga"
            self.act3 = "Vidéo de motivation"

        # Boutons pour les activités
        self.butt_1 = tk.Button(self, text=self.act1, font=('Arial', 14), width=15, height=2, command=lambda: self.show_act(self.act1), bg='#2196F3', fg='white', bd=0,highlightthickness=0, padx=10, pady=10, border=7)
        self.butt_1.grid(row=1, column=0, pady=10)

        self.butt_2 = tk.Button(self, text=self.act2, font=('Arial', 14), width=15, height=2, command=lambda: self.show_act(self.act2), bg='#4CAF50', fg='white', bd=0, highlightthickness=0, padx=10, pady=10, border=7)
        self.butt_2.grid(row=2, column=0, pady=10)

        self.butt_3 = tk.Button(self, text=self.act3, font=('Arial', 14), width=15, height=2, command=lambda: self.show_act(self.act3), bg='#FF5722', fg='white', bd=0, highlightthickness=0, padx=10, pady=10, border=7)
        self.butt_3.grid(row=3, column=0, pady=10)

    def show_act(self, act):
        self.master.frame_each_activity.Act(act)
        self.master.frame_each_activity.show_it()

    # Montrer
    def show_it(self):
        if os.path.exists(self.master.PathToUserFile):
            self.master.hide_all()
            self.grid(row=1, rowspan=7, column=0, sticky="nsew")

    # Cacher
    def hide_it(self):
        self.grid_forget()
