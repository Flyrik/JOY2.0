import tkinter as tk
from tkinter import ttk
import json
import os

PathToUserFile = r"Source\user_data.json"


class InfoUser:
    def __init__(self, name='Joy', age=16, genre='Non-binaire'):
        self.name = name
        self.age = age
        self.genre = genre

    def to_dict(self):
        return self.__dict__

    def save_to_json(self, filename):
        with open(filename, 'w') as json_file:
            json.dump(self.to_dict(), json_file, indent=4)

    @classmethod
    def load_from_json(cls, filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
            return cls(**data)


# Page de configuration de l'identité de l'utilisateur
class FrameProfilUser(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg='#f0f0f0')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Créer un Canvas pour le défilement
        self.canvas = tk.Canvas(self, bg='#f0f0f0')
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')

        # Configurer le Canvas et la Scrollbar
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Ajouter le Canvas et la Scrollbar à la frame principale
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Ajouter les widgets dans la scrollable_frame
        self.label1 = tk.Label(self.scrollable_frame, text="Salut, quel est ton nom ?", font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
        self.label1.pack(pady=10)

        self.entry_name = tk.Entry(self.scrollable_frame, font=('Arial', 14), width=30, bd=2, relief='sunken')
        self.entry_name.pack(pady=10)
        self.entry_name.bind("<FocusIn>", self.on_entry_focus)
        self.entry_name.bind("<FocusOut>", self.on_entry_focus_out)

        self.label2 = tk.Label(self.scrollable_frame, text="Quel âge as tu ?", font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
        self.label2.pack(pady=10)

        self.entry_age = tk.Entry(self.scrollable_frame, font=('Arial', 14), width=30, bd=2, relief='sunken')
        self.entry_age.pack(pady=10)
        self.entry_age.bind("<FocusIn>", self.on_entry_focus)
        self.entry_age.bind("<FocusOut>", self.on_entry_focus_out)

        self.label3 = tk.Label(self.scrollable_frame, text="Et ton genre ?", font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
        self.label3.pack(pady=10)

        self.genre_var = tk.StringVar(value="None")
        self.genre_combobox = ttk.Combobox(self.scrollable_frame, textvariable=self.genre_var, values=["Femme", "Homme", "Non-binaire", "--"], font=('Arial', 14))
        self.genre_combobox.pack(pady=10)

        self.submit_button = tk.Button(self.scrollable_frame, text="Valider", font=('Arial', 14), width=15, height=1, command=self.submit_info, bg='#4CAF50', fg='white', bd=0, highlightthickness=0, padx=10, pady=10, border=7)
        self.submit_button.pack(pady=20)

        # Ajouter un espaceur en bas de la scrollable_frame
        self.spacer = tk.Frame(self.scrollable_frame, height=0, bg='#f0f0f0')
        self.spacer.pack(fill='x')

    # On enregistre les info utilisateurs dans le fichier info.json
    def submit_info(self):
        name = self.entry_name.get() or 'Joy'
        age = self.entry_age.get() or 16
        genre = self.genre_var.get() or 'Binary'

        self.master.info_user = InfoUser(name=name, age=age, genre=genre)
        self.master.info_user.save_to_json(PathToUserFile)

        self.hide_it()

        self.master.frame_accueil.show_it()
        self.update_labels()

    # On met a jour les labels qui dise bonjour xxx
    def update_labels(self):
        if os.path.exists(PathToUserFile):
            self.master.frame_accueil.label1.config(text=f"Salut {self.master.info_user.name}!")

    # Quand focus sur entry on augmente la taille de la scrollbar pour placer clavier
    def on_entry_focus(self, event, taille_clavier_compris = 400):
        # Ajuster la hauteur de l'espaceur lorsque le clavier virtuel est présumé ouvert
        self.spacer.config(height=taille_clavier_compris)  # Ajuster la valeur selon la hauteur du clavier virtuel

    # Quand on perd le focus sur entry on reset scrollbar
    def on_entry_focus_out(self, event):
        # Réinitialiser la hauteur de l'espaceur lorsque le champ d'entrée perd le focus
        self.spacer.config(height=0)

    # Montrer
    def show_it(self):
        self.master.hide_all()
        self.grid(row=1, rowspan=7, column=0, sticky="nsew")
    
    # Cacher
    def hide_it(self):
        self.grid_forget()
        self.entry_name.delete(0, tk.END)
        self.entry_age.delete(0, tk.END)
        self.genre_var.set("None")  # Réinitialiser la combobox à "None"


if __name__ == "__main__":
    # To test
    # user = InfoUser(name="John Doe", age=30, genre="male")
    user = InfoUser(name="Melissa", age=21, genre="female")
    user.save_to_json(r"Source\user_data.json")

    # Charger un utilisateur à partir du fichier JSON
    loaded_user = InfoUser.load_from_json(r"Source/user_data.json")
    print(f"Nom: {loaded_user.name}, Age: {loaded_user.age}, Genre: {loaded_user.genre}")
