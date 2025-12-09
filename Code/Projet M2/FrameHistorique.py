import tkinter as tk
from tkinter import scrolledtext
import logging
import os, datetime
import unicodedata

negative_emotions = {"Triste", "Stressee", "Stresse", "En colere"}


class History():
    def __init__(self):
        self.path_history = 'Source/previous_records.log'
        self.path_warning_date = 'Source/last_warning_date.json'

        self.handler1 = logging.FileHandler(self.path_history)
        self.formatter1 = logging.Formatter("%(asctime)s : %(message)s", "%Y-%m-%d %H:%M:%S")
        self.handler1.setFormatter(self.formatter1)
        self.logger1 = logging.getLogger('logger1')
        self.logger1.addHandler(self.handler1)
        self.logger1.setLevel(logging.INFO)  # Niveau de gravité minimum pour logger1

    # Ecris dans l'historique
    def write_record(self, bpm:int, humeur:str):
        self.logger1.info(f"{self.remove_accents(humeur)} : {bpm} bpm")
        self.trim_log_file_if_needed()

    def remove_accents(self,input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

    # Vider entièrement le fichier de log.
    def clear_log(self):
        open(self.path_history, 'w').close()

    # Supprime les 500 premières lignes si le fichier atteint 1000 lignes
    def trim_log_file_if_needed(self, n_suppr=500, limite=1000):
        with open(self.path_history, 'r') as file:
            lines = file.readlines()
        if len(lines) > limite:
            with open(self.path_history, 'w') as file:
                file.writelines(lines[n_suppr:])
        del lines

    # Récupérer les 10 dernières lignes du fichier de log.
    def get_last_records(self, last_line=15):
        try:
            with open(self.path_history, 'r') as file:
                lines = file.readlines()
                return lines[-last_line:]
        except FileNotFoundError:
            return ["Le fichier de log est introuvable."]

    # Parse the lines to extract emotions by date.
    def parse_emotions(self):
        lines = self.get_last_records(last_line=150)
        emotions_by_day = {}
        for line in lines:
            date_str, emotion, _ = line.split(' : ')
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()
            emotion = emotion.strip()
            if date not in emotions_by_day:
                emotions_by_day[date] = []
            emotions_by_day[date].append(emotion)
        return emotions_by_day

    # Count negative emotions per day.
    def count_negative_emotions(self):
        emotions_by_day = self.parse_emotions()
        negative_emotions_count_by_day = {}
        for date, emotions in emotions_by_day.items():
            negative_emotions_count = sum(1 for emotion in emotions if emotion in negative_emotions)
            negative_emotions_count_by_day[date] = negative_emotions_count
        return negative_emotions_count_by_day
    
    # Check if the number of negative emotions over the past `days` days exceeds the threshold.
    def check_negative_emotions_threshold(self, threshold=15, days=10):
        negative_emotions_count_by_day = self.count_negative_emotions()
        today = datetime.date.today()
        count = 0
        for i in range(days):
            day = today - datetime.timedelta(days=i)
            count += negative_emotions_count_by_day.get(day, 0)
        return count >= threshold

    # Write the current date as the last warning date
    def set_last_warning_date(self):
        with open(self.path_warning_date, 'w') as file:
            file.write(datetime.date.today().strftime("%Y-%m-%d"))

    # Read the last warning date from file
    def get_last_warning_date(self):
        if os.path.exists(self.path_warning_date):
            with open(self.path_warning_date, 'r') as file:
                date_str = file.read().strip()
                return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        return None


# Page de l'historique des émotions précédente
class FrameHistorique(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg='#f0f0f0')  # Couleur de fond pour rendre la frame plus agréable
        self.history = History()

        # Titre de l'historique
        self.label = tk.Label(self, text="Historique des émotions et BPM", font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
        self.label.pack(pady=20)

        # Zone de texte pour afficher l'historique
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=90, height=20, font=("Arial", 12), bd=2, relief='sunken')
        self.text_area.pack(pady=10, padx=20)

    # Affiche les 15 dernières lignes de l'historique 
    def display_history(self):
        # Permettre la modification du texte
        self.text_area.config(state=tk.NORMAL)
        # Effacer tout le contenu
        self.text_area.delete('1.0', tk.END)

        lines = self.history.get_last_records()
        for line in lines:
            self.text_area.insert(tk.END, line + "\n")
        self.text_area.config(state=tk.DISABLED)  # Rendre le texte non éditable

    # Montrer
    def show_it(self):
        if os.path.exists(self.master.PathToUserFile):
            self.master.hide_all()
            self.grid(row=1, rowspan=7, column=0, sticky="nsew")
            self.display_history()

    # Cacher
    def hide_it(self):
        self.grid_forget()


""" if __name__ == "__main__":
    h = History()
    lines = h.get_last_records(last_line=150)
    # print('lines',lines) #ok
    emotions_by_day = h.parse_emotions(lines)
    # print('emotion by day\n',emotions_by_day)
    negative_emotions_count_by_day = h.count_negative_emotions(emotions_by_day)
    # print("negative count by day\n",negative_emotions_count_by_day)
    threshold = 10  # Définissez le seuil d'émotions négatives ici
    if h.check_negative_emotions_threshold(negative_emotions_count_by_day, threshold):
        h.show_warning_popup() """