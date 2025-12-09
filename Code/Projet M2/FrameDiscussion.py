# -*- coding: utf-8 -*-
# Importing
import tkinter as tk
from tkinter import scrolledtext
import os
import datetime

import FrameProfilUser as Profil_user
import Reponse_verbale as Response_verbale
from Reponse_verbale import Interaction as Interact
import Audio
import Generation_parole


class FrameDiscussion(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg='#f0f0f0')
        self.columnconfigure(0, weight=1)

        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=90, height=20, font=("Arial", 12), bd=2,
                                                   relief='sunken')
        self.text_area.grid(row=0, pady=10, padx=20)

        self.message_area = tk.Text(self, width=60, height=1, font=("Arial", 12), bd=2, relief='sunken')
        self.message_area.grid(row=1, sticky="w", padx=10, pady=10)

        self.photo_audio = tk.PhotoImage(file="Source/Items/audio_off.png")
        self.audio_butt = tk.Button(self, image=self.photo_audio, borderwidth=0, command=lambda: self.Turn_on_off())
        self.audio_butt.grid(row=1, column=1, padx=10, pady=10)

        self.photo_envoi = tk.PhotoImage(file="Source/Items/envoyer.png")
        self.envoi_butt = tk.Button(self, image=self.photo_envoi, borderwidth=1, bg="#77DDFF",
                                    command=lambda: self.Type())
        self.envoi_butt.grid(row=1, column=2, padx=10, pady=10)

        self.last_mess = []
        self.answer = ""

        self.PathToUserFile = self.master.PathToUserFile
        self.syllables = self.master.syllables
        self.butt_logo = self.master.butt_logo
        self.vitesse = self.master.vitesse
        self.timbre = self.master.timbre
        self.volume = self.master.volume

        self.audio = Audio
        self.response = Response_verbale

        self.history = HistoryChat(self)

    @staticmethod
    def Reformate(script):
        ponctuation = [":", ";", ",", ".", "!", "?", " ", "-", "'", "\""]
        final_script = list(script.strip())
        index = 0
        while index < len(final_script) - 1:
            if ''.join(final_script[index:index + 3]) == "...":
                index += 2

            elif (final_script[index] in ponctuation and final_script[index + 1] in ponctuation and
                  final_script[index] == final_script[index + 1]):
                final_script.pop(index)
            elif final_script[index] in ponctuation[:6] and final_script[index + 1] != " ":
                i = 1
                final_script.append(final_script[-i])
                for j in range(len(final_script) - index - 2):
                    final_script[- j - 2] = final_script[- j - 3]
                final_script[index + 1] = " "
            else:
                index += 1
        final_script[0] = final_script[0].upper()
        for i in range(2, len(final_script)):
            if i < len(final_script) - 2 and final_script[i] in [".", "!", "?"] and final_script[i + 1] == " ":
                final_script[i + 2] = final_script[i + 2].upper()
        final_script = ''.join(final_script).replace("\n", "")
        return ''.join(final_script)

    def Type(self):
        if self.master.on_off:
            self.Turn_on_off()

        history_mess = self.history.get_last_records()
        input_mess = self.message_area.get("1.0", "end-1c")
        if input_mess.strip() != "":
            self.answer = self.response.Answer(self, input_mess.lower()).Answer()
            now = datetime.datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            reformated_mess = self.Reformate(input_mess)
            history_mess.append("user:" + reformated_mess + "\n" + current_time + "\n")
            open(self.history.path_history_mess, 'w').writelines(history_mess)
            self.message_area.delete('1.0', tk.END)
            new_history_mess = self.history.get_last_records()
            self.display_user(new_history_mess, -2)
            if self.answer != "":
                self.Answer()

    def Turn_on_off(self):
        if self.master.on_off:
            self.master.on_off = False
            self.photo_audio = tk.PhotoImage(file="Source/Items/audio_off.png")
            self.audio_butt.configure(image=self.photo_audio)
        else:
            self.master.on_off = True
            self.photo_audio = tk.PhotoImage(file="Source/Items/audio_on.png")
            self.audio_butt.configure(image=self.photo_audio)
            self.Vocal()

    def Vocal(self):
        if self.master.on_off:
            text = self.master.audio2text.Exe()
            if text != "":
                self.message_area.insert(tk.END, f"{text}. ")
            self.after(10, self.Vocal)

    def Answer(self):
        history_mess = self.history.get_last_records()
        now = datetime.datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        reformated_ans = self.Reformate(self.answer)
        history_mess.append("JOY:" + reformated_ans + "\n" + current_time + "\n")
        open(self.history.path_history_mess, 'w').writelines(history_mess)
        new_history_mess = self.history.get_last_records()
        self.display_joy(new_history_mess, -2)
        self.master.syllables = Generation_parole.Generation(reformated_ans).Phoneme2Syllable()
        self.syllables = self.master.syllables
        self.audio.Setting(self, script=reformated_ans, vit=self.master.vitesse, timbre=self.master.timbre,
                           volume=self.master.volume)
        on_off = open("Source/Face/face.txt").readlines()
        if on_off[0][:3].strip() == "on":
            self.master.logo_img = "Source/Items/logo_notif_on.png"
        else:
            self.master.logo_img = "Source/Items/logo_notif_off.png"
        self.master.photo1 = tk.PhotoImage(file=self.master.logo_img)
        self.master.butt_logo.configure(image=self.master.photo1)
        self.answer = ""

    def Check_answer(self):
        joy_mess = self.last_mess[0]
        user_mess = self.last_mess[1]
        if "se prononce" in joy_mess and "plutôt que" in joy_mess and "?" in joy_mess:
            index = len("Donc ")
            while joy_mess[index] != " ":
                index += 1
            word = joy_mess[len("Donc "):index].strip()
            index = joy_mess.index("se prononce") + len("se prononce ")
            prononciation = []
            phonemes = self.master.generation.Generation("").phonemes
            while joy_mess[index] != "]":
                if (joy_mess[index - 1:index + 2] in [f"'{phon}'" for phon in phonemes] +
                        [f"\"{phon}\"" for phon in phonemes]):
                    prononciation.append(joy_mess[index])
                index += 1
            self.answer = Interact(self).Correction(word, prononciation, user_mess)

    def display_history(self, check):
        # Permettre la modification du texte
        self.text_area.config(state=tk.NORMAL)
        # Effacer tout le contenu
        self.text_area.delete('1.0', tk.END)

        lines = self.history.get_last_records()
        self.text_area.insert(tk.END, "\t\t" + lines[1][:11] + "\n")

        for i in range(0, len(lines), 2):
            if 2 < i < len(lines) - 1 and lines[i - 1][:10] != lines[i + 1][:10]:
                self.text_area.insert(tk.END, "\t\t" + lines[i + 1][:11] + "\n")

            if lines[i][:4] == "JOY:":
                self.display_joy(lines, i)

            elif lines[i][:5] == "user:":
                self.display_user(lines, i, check)

    def display_joy(self, lines, i):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, lines[i][4:])
        self.text_area.insert(tk.END, "\t" + lines[i + 1][11:-4] + "\n")
        self.text_area.config(state=tk.DISABLED)  # Rendre le texte non éditable
        self.text_area.yview(tk.END)
        self.last_mess = [lines[i][4:]]

    def display_user(self, lines, i, check=True):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, "\t\t\t" + lines[i][5:])
        self.text_area.insert(tk.END, "\t\t\t\t" + lines[i + 1][11:-4] + "\n")
        self.text_area.config(state=tk.DISABLED)  # Rendre le texte non éditable
        self.text_area.yview(tk.END)
        self.last_mess.append(lines[i][5:])
        if check:
            self.Check_answer()

    def show_it(self):
        if os.path.exists(self.master.PathToUserFile):
            self.master.hide_all()
            self.grid(row=1, rowspan=10, column=0, sticky="nsew")
            self.Type()
            self.display_history(False)

    # Cacher
    def hide_it(self):
        self.master.on_off = False
        self.grid_forget()


class HistoryChat(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.path_history_mess = "Source/previous_messages.log"
        self.info_user = Profil_user.InfoUser.load_from_json(self.master.PathToUserFile)
        self.syllables = self.master.syllables

        self.audio = Audio

    def get_last_records(self):
        if not os.path.exists(self.path_history_mess) or open(self.path_history_mess).readlines() == []:
            now = datetime.datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            first_mess = f"Bonjour {self.info_user.name}. Commençons à discuter. Comment te sens-tu aujourd'hui ?"
            open(self.path_history_mess, 'w').writelines(f"JOY:{first_mess}\n{current_time}\n")
            self.audio.Setting(self, script=first_mess,  vit=self.master.vitesse, timbre=self.master.timbre,
                               volume=self.master.volume)
            on_off = open("Source/Face/face.txt").readlines()
            if on_off[0][:3].strip() == "on":
                self.master.logo_img = "Source/Items/logo_notif_on.png"
            else:
                self.master.logo_img = "Source/Items/logo_notif_off.png"
            self.master.photo1 = tk.PhotoImage(file=self.master.logo_img)
            self.master.butt_logo.configure(image=self.master.photo1)
        return open(self.path_history_mess).readlines()


if __name__ == "__main__":
    """def Reformate(script):
        ponctuation = [":", ";", ",", ".", "!", "?", " ", "-", "'", "\""]
        final_script = list(script.strip())
        index = 0
        while index < len(final_script) - 1:
            if ''.join(final_script[index:index + 3]) == "...":
                index += 2

            elif (final_script[index] in ponctuation and final_script[index + 1] in ponctuation and
                    final_script[index] == final_script[index + 1]):
                final_script.pop(index)
            elif final_script[index] in ponctuation[:6] and final_script[index + 1] != " ":
                i = 1
                final_script.append(final_script[-i])
                for j in range(len(final_script) - index - 2):
                    final_script[- j - 2] = final_script[- j - 3]
                final_script[index + 1] = " "
            else:
                index += 1
        final_script[0] = final_script[0].upper()
        for i in range(2, len(final_script)):
            if i < len(final_script) - 2 and final_script[i] in [".", "!", "?"] and final_script[i + 1] == " ":
                final_script[i + 2] = final_script[i + 2].upper()

        return ''.join(final_script)

    bad_script = "Médéric Rousseau a 24 ans... et il est votre ami."

    print(bad_script)
    print(Reformate(bad_script))
    print(FrameDiscussion.Reformate(bad_script))"""
