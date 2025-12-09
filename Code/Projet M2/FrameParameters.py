import tkinter as tk
import os

PathToUserFile = r"Source\user_data.json"


# Page de paramétrage : réglage hauteur cam, effacement des données, ...
class FrameParameters(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg='#f0f0f0')  # Couleur de fond pour rendre la frame plus agréable
        self.grid_columnconfigure(0, weight=1)

        # Créer un Canvas pour le défilement
        self.canvas = tk.Canvas(self, bg='#f0f0f0')
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')

        # Configurer le Canvas et la Scrollbar
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Ajouter le Canvas et la Scrollbar à la frame principale
        self.canvas.pack(side="left", fill="both", expand=True, padx=60)
        self.scrollbar.pack(side="right", fill="y")

        # Bouton pour effacer les données
        self.label1 = tk.Label(self.scrollable_frame, text="Visage", font=('Arial', 18, 'bold'), bg='#F0F0F0',
                               fg='#333')
        self.label1.pack(expand=True, pady=5)
        self.face_button = tk.Button(self.scrollable_frame, font=('Arial', 14), command=self.On_Off_face, fg='black',
                                     bd=0, highlightthickness=0, padx=5, pady=5, border=7)
        self.face_button.pack(expand=True, pady=5)

        self.start_on_ff = tk.Button(self.scrollable_frame, font=('Arial', 14), command=self.set_default_cam,
                                     bg='#F0F0F0', bd=0, highlightthickness=0, padx=5, pady=5)
        self.start_on_ff.pack(expand=True, pady=5)

        # Bouton pour effacer les données
        self.label2 = tk.Label(self.scrollable_frame, text="Suppression des données biométriques",
                               font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
        self.label2.pack(expand=True, pady=5)
        self.clear_button = tk.Button(self.scrollable_frame, text="Données personnelles", font=('Arial', 14),
                                      command=self.clear_info_user, bg='#66DDFF', fg='black', bd=0,
                                      highlightthickness=0, padx=5, pady=5, border=7)
        self.clear_button.pack(expand=True, pady=5)

        self.clear_button_model = tk.Button(self.scrollable_frame, text="Model", font=('Arial', 14),
                                            command=self.clear_model, bg='#66DDFF', fg='black', bd=0,
                                            highlightthickness=0, padx=5, pady=5, border=7)
        self.clear_button_model.pack(expand=True, pady=5)

        self.label3 = tk.Label(self.scrollable_frame, text="Suppression des historiques", font=('Arial', 18, 'bold'),
                               bg='#f0f0f0', fg='#333')
        self.label3.pack(expand=True, pady=5)
        self.clear_button_history_feeling = tk.Button(self.scrollable_frame, text="Historique d'émotion",
                                                      font=('Arial', 14), command=self.clear_history_feel, bg='#66DDFF',
                                                      fg='black', bd=0, highlightthickness=0, padx=5, pady=5, border=7)
        self.clear_button_history_feeling.pack(expand=True, pady=5)

        self.clear_button_history_conv = tk.Button(self.scrollable_frame, text="Historique de discussion",
                                                   font=('Arial', 14), command=self.clear_history_conv, bg='#66DDFF',
                                                   fg='black', bd=0, highlightthickness=0, padx=5, pady=5, border=7)
        self.clear_button_history_conv.pack(expand=True, pady=5)

        self.label4 = tk.Label(self.scrollable_frame, text="Réinitialisation complète", font=('Arial', 18, 'bold'),
                               bg='#f0f0f0', fg='#333')
        self.label4.pack(pady=5)
        self.clear_button_all = tk.Button(self.scrollable_frame, text="Tous", font=('Arial', 14),
                                          command=self.clear_all, bg='#66DDFF', fg='black', bd=0, highlightthickness=0,
                                          padx=5, pady=5, border=7)
        self.clear_button_all.pack(expand=True, pady=5)

        self.set_start_on_ff_button()
        self.exception = None

    # Face
    def On_Off_face(self):
        on_off = open("Source/Face/face.txt").readlines()
        if on_off[0][:3].strip() == "on":
            on_off[0] = f"off {on_off[0][-4:].strip()}\n"
            if "notif" in self.master.logo_img:
                self.master.logo_img = "Source/Items/logo_notif_off.png"
            else:
                self.master.logo_img = "Source/Items/logo_off.png"
            self.face_button.configure(text="OFF", bg="#ff0000")
        else:
            on_off[0] = f"on {on_off[0][-4:].strip()}\n"
            if "notif" in self.master.logo_img:
                self.master.logo_img = "Source/Items/logo_notif_on.png"
                self.face_button.configure(text="OFF", bg="#ff0000")
            else:
                self.master.logo_img = "Source/Items/logo_on.png"
                self.face_button.configure(text="ON", bg="#00ff00")
        self.master.photo1 = tk.PhotoImage(file=self.master.logo_img)
        self.master.butt_logo.configure(image=self.master.photo1)
        open("Source/Face/face.txt", 'w').writelines(on_off)

    def set_default_cam(self):
        on_off = open("Source/Face/face.txt").readlines()
        if on_off[0][-4:].strip() == "on":
            on_off[0] = f"{on_off[0][:3].strip()} off\n"
        else:
            on_off[0] = f"{on_off[0][:3].strip()} on\n"
        open("Source/Face/face.txt", 'w').writelines(on_off)
        self.set_start_on_ff_button()

    def set_start_on_ff_button(self):
        on_off = open("Source/Face/face.txt").readlines()
        if on_off[0][-4:].strip() == "on":
            self.start_on_ff.configure(text="Caméra activée au démarrage", fg='#33EE22')
        else:
            self.start_on_ff.configure(text="Caméra désactivée au démarrage", fg='#EE3322')

    # Supprimer les infos user
    def clear_info_user(self):
        try:
            os.remove(PathToUserFile)
            print("Fichier JSON effacé")
        except FileNotFoundError:
            print("Le fichier JSON n'existe pas")

        # Réinitialiser self.info_user
        self.master.info_user = None
        self.master.frame_profil_user.show_it()

    # Supprimer le model ré-entrainé
    def clear_model(self):
        pass
        """try:
            os.remove(f"Source/Models/new_model.h5")
            self.master.frame_detect.loaded_model = tf.keras.models.load_model(f"Source/Models/model2.h5")
            print("Modèle est restauré")
        except:
            print("Pas de modèle à restaurer")"""

    def clear_history_feel(self):
        try:
            self.master.frame_history.history.clear_log()
            print("Historique d'émotion effacé")
        except Exception as e:
            self.exception = e
            print("Erreur suppression historique")

    # Supprimer l'historique des émotions
    def clear_history_conv(self):
        try:
            open("Source/previous_messages.log", 'w').writelines([])
            print("Historique de discussion effacé")
        except Exception as e:
            self.exception = e
            print("Erreur suppression historique")

    # Supprimer le model ré-entrainé, l'historique, et les infos de l'user
    def clear_all(self):
        try:
            self.clear_info_user()
            self.clear_model()
            self.clear_history_feel()
            self.clear_history_conv()
        except Exception as e:
            self.exception = e
            print("Erreur suppression données")

    # Montrer ++ créer un objet cam uniquement lorsque la page apparait
    def show_it(self):
        self.master.hide_all()
        self.grid(row=1, rowspan=7, column=0, sticky="nsew")
        self.canvas.yview_moveto(0)

    # Cacher
    def hide_it(self):
        self.pack_forget()
        self.grid_forget()


if __name__ == '__main__':
    """# Titre de la section
    self.label1 = tk.Label(self, text="Réglage de la caméra", font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
    self.label1.pack(pady=5)

    self.camera_label = tk.Label(self, bg='#f0f0f0', bd=2, relief='solid')
    self.camera_label.pack()

    # Initialisation de l'angle
    self.angle = 0

    # Affichage de l'angle actuel
    self.angle_label = tk.Label(self, text=f"Angle: {self.angle}°", font=('Arial', 14), bg='#f0f0f0', fg='#333')
    self.angle_label.pack(pady=5)

    # Réglage initial du servo
    self.set_servo_angle(self.angle)

    # SLIDER :: Option 1
    # Slider pour régler l'angle de la caméra step = 5
    self.angle_slider = tk.Scale(self, from_=0, to=180, resolution=5, orient='horizontal',
                                 label='Angle de la caméra', font=('Arial', 12), length=400, bg='#f0f0f0',
                                 fg='#333', command=self.on_slider_change)
    self.angle_slider.pack(pady=10)"""