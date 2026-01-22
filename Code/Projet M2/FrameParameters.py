import tkinter as tk
import os

PathToUserFile = r"Source\user_data.json"


# Page de paramétrage : réglage hauteur cam, effacement des données, ...
class FrameParameters(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        THEME_BG = "#FFF6E9"
        TITLE_FG = "#2D2A32"
        TEXT_FG = "#555"

        self.configure(bg=THEME_BG)
        self.grid_columnconfigure(0, weight=1)

        # Canvas scroll
        self.canvas = tk.Canvas(self, bg=THEME_BG, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=THEME_BG)

        # Configurer le Canvas et la Scrollbar
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        def _resize_scroll_frame(event):
            # event.width = largeur visible du canvas
            self.canvas.itemconfig(self.canvas_window, width=event.width)

        self.canvas.bind("<Configure>", _resize_scroll_frame)


        # Ajouter le Canvas et la Scrollbar à la frame principale
        self.canvas.pack(side="left", fill="both", expand=True, padx=60)
        self.scrollbar.pack(side="right", fill="y")

        # Bouton pour effacer les données
        PADX = 28

        def section_title(text):
            lbl = tk.Label(
                self.scrollable_frame,
                text=text,
                font=("Arial", 18, "bold"),
                bg=THEME_BG,
                fg=TITLE_FG
            )
            lbl.pack(fill="x", padx=PADX, pady=(18, 6), anchor="w")
            return lbl

        def card_button(text, command, bg, fg="white"):
            btn = tk.Button(
                self.scrollable_frame,
                text=text,
                command=command,
                font=("Arial", 16, "bold"),
                bg=bg, fg=fg,
                activebackground=bg,
                bd=0, highlightthickness=0,
                padx=18, pady=14,
                cursor="hand2"
            )
            btn.pack(fill="x", padx=PADX, pady=8)
            return btn

        def divider():
            line = tk.Frame(self.scrollable_frame, bg="#E9DCCB", height=2)
            line.pack(fill="x", padx=PADX, pady=12)

        # Bouton pour effacer les données
        section_title("🙂 Visage")

        self.face_button = card_button(
            text="Activer / Désactiver 👀",
            command=self.On_Off_face,
            bg="#7ED957",
            fg="white"
        )

        self.start_on_ff = tk.Button(
            self.scrollable_frame,
            font=("Arial", 13, "bold"),
            command=self.set_default_cam,
            bg=THEME_BG,
            fg=TEXT_FG,
            bd=0,
            cursor="hand2"
        )
        self.start_on_ff.pack(fill="x", padx=PADX, pady=(2, 4), anchor="w")

        divider()

        section_title("🧹 Effacer mes infos")

        self.clear_button = card_button(
            text="🧒 Mon profil (données perso)",
            command=self.clear_info_user,
            bg="#5DADE2"
        )

        self.clear_button_model = card_button(
            text="🤖 Modèle (IA)",
            command=self.clear_model,
            bg="#5DADE2"
        )

        divider()

        section_title("📜 Effacer l’historique")

        self.clear_button_history_feeling = card_button(
            text="🎭 Émotions",
            command=self.clear_history_feel,
            bg="#FFB347"
        )

        self.clear_button_history_conv = card_button(
            text="💬 Discussions",
            command=self.clear_history_conv,
            bg="#FFB347"
        )

        divider()

        section_title("🚨 Remise à zéro")

        self.clear_button_all = card_button(
            text="🔁 Tout réinitialiser",
            command=self.clear_all,
            bg="#FF6B6B"
        )

        self.set_start_on_ff_button()
        self.exception = None

    # Face
    def On_Off_face(self):
        on_off = open("Source/Face/face.txt").readlines()
        if on_off[0][:3].strip() == "on":
            self.face_button.configure(text="OFF", bg="#ff0000")
            on_off[0] = f"off {on_off[0][-4:].strip()}\n"
            if "notif" in self.master.logo_img:
                self.master.logo_img = "Source/Items/logo_notif_off.png"
            else:
                self.master.logo_img = "Source/Items/logo_off.png"
            
        else:
            on_off[0] = f"on {on_off[0][-4:].strip()}\n"
            self.face_button.configure(text="ON", bg="#00ff00")
            if "notif" in self.master.logo_img:
                self.master.logo_img = "Source/Items/logo_notif_on.png"
                ##self.face_button.configure(text="OFF", bg="#ff0000")
            else:
                self.master.logo_img = "Source/Items/logo_on.png"
                
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