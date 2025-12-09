# -*- coding: utf-8 -*-
# Importing
import tkinter as tk
import random
import datetime

import Generation_parole as Gen

PathToUserFile = r"Source\user_data.json"


class Answer(tk.Frame):
    def __init__(self, master, from_user):
        super().__init__(master)
        self.from_user = from_user.lower()

        self.ponctuation = [":", ";", ",", ".", "!", "?", " ", "-", "'", "\""]
        self.for_verif = []
        self.answer = ""

        self.PathToUserFile = self.master.PathToUserFile
        self.syllables = self.master.syllables
        self.butt_logo = self.master.butt_logo
        self.butt_logo = self.master.butt_logo
        self.vitesse = self.master.vitesse
        self.timbre = self.master.timbre
        self.volume = self.master.volume
        # self.info_user = Profil_user.InfoUser.load_from_json(PathToUserFile)

    def Answer(self):
        for i in ["bonjour", "salut", "hey", "hi"]:
            if i in self.from_user:
                self.answer += self.Salutation()
                break

        self.Rectification_syllable()

        for i in ["comment", "pourquoi"]:
            if i in self.from_user:
                if self.answer != "":
                    if self.answer[-1] not in [".", "!", "?"]:
                        self.answer += "."
                    self.answer += " "
                self.answer += self.Explication(i)
                break

        if self.answer != "":
            if self.answer[-1] not in [".", "!", "?"]:
                self.answer += "."
            self.answer += " "
        # self.answer += self.Renseignement()

        return self.answer

    def Salutation(self):
        salute_answer = ""
        list_salutation = ["Salut", "Bonjour", "Hey"]
        messages = open("Source/previous_messages.log", 'r').readlines()
        now = datetime.datetime.now()
        today = now.strftime("%d/%m/%Y")
        mess_auj = [messages[i - 1][4:] for i in range(1, len(messages), 2) if messages[i][:10] == today
                    and messages[i - 1][:3] == "JOY"]

        salute_today = False
        for i in list_salutation:
            for j in mess_auj:
                if i.lower() in j.lower():
                    salute_today = True
                    break
            if salute_today:
                break

        if not salute_today:
            rnd = random.randint(0, len(list_salutation) - 1)
            salute_answer = list_salutation[rnd]
            if random.randint(0, 1) == 1:
                salute_answer += " !"

        return salute_answer

    def Explication(self, question_word):
        explicative_answer = ""
        rnd = 0
        explicative_answer_start = []
        if question_word in ["pourquoi"]:
            explicative_answer_start = ["parce que", "car"]
            rnd = random.randint(0, len(explicative_answer_start) - 1)

        elif question_word in ["comment", "quoi"]:
            explicative_answer_start = ["comme ça", "comme ceci"]
            rnd = random.randint(0, len(explicative_answer_start) - 1)

        elif question_word in ["quand"]:
            explicative_answer_start = ["hier", "ce matin", "ce soir", "demain", "la semaine prochaine"]
            rnd = random.randint(0, len(explicative_answer_start) - 1)

        elif question_word in ["où"]:
            # A compléter
            explicative_answer_start = ["derrière", "à côté", "devant", "au-dessus", "en-dessous"]
            rnd = random.randint(0, len(explicative_answer_start) - 1)

        elif question_word in ["qu'est_ce qu"]:
            # A compléter
            explicative_answer_start = ["ceci", "cela", "ça"]
            rnd = random.randint(0, len(explicative_answer_start) - 1)

        elif question_word in ["est-ce qu"]:
            # A compléter
            explicative_answer_start = ["oui", "non", "peut-être", "je ne sais pas", "qui sait"]
            rnd = random.randint(0, len(explicative_answer_start) - 1)

        else:
            explicative_answer = "Je n'ai pas bien compris ta demande"

        explicative_answer += explicative_answer_start[rnd]

        return explicative_answer

    def Renseignement(self):
        return "Mais dis-moi, toi, comment te sens-tu vraiment ?"

    def Rectification_syllable(self):
        local = [" de ", " dans "]
        for rect_marker in ["se prononce", "se dit"]:
            if rect_marker in self.from_user:
                index = self.from_user.index(rect_marker)
                if index != 0:
                    for loc_from in local:
                        if loc_from in self.from_user[:index]:
                            mot_from = self.from_user[self.from_user.index(loc_from) + len(loc_from):index].strip()
                            index_syl = self.from_user.index(loc_from)
                            while index_syl > 0 and self.from_user[index_syl-1] != " ":
                                index_syl -= 1
                            syl_from = self.from_user[index_syl:self.from_user.index(loc_from)].strip()

                            index += len(rect_marker)
                            for loc_to in local:
                                if loc_to in self.from_user[index:]:
                                    mot_to = self.from_user[self.from_user[index:].index(loc_to) + len(loc_to) + index:]
                                    while mot_to[-1] in self.ponctuation:
                                        mot_to.pop()
                                    mot_to.strip()
                                    index_syl = self.from_user[index:].index(loc_to) + index
                                    while index_syl > index and self.from_user[index_syl - 1] != " ":
                                        index_syl -= 1
                                    syl_to = self.from_user[index_syl:self.from_user[index:].index(loc_to)+index].strip()
                                    # print(f"'{syl_from}' de '{mot_from}' = '{syl_to}' de '{mot_to}'")

                                    index_syl_in_mot = mot_from.index(syl_from)
                                    new_mot = "-".join([mot_from[0:index_syl_in_mot], syl_to,
                                                        mot_from[index_syl_in_mot + len(syl_from):]])
                                    if new_mot[-1] == '-':
                                        new_mot = new_mot[:-1]

                                    # print(new_mot)
                                    new_prononciation = Gen.Generation(new_mot).script_phoneme[:-1]
                                    # print(new_prononciation)
                                    self.for_verif = [syl_from, mot_from, syl_to, mot_to]
                                    self.answer += Interaction(self).Verification(mot_from, new_prononciation)

    def Sujet(self, script):
        if "chat" in script:
            return "chat"


class Interaction(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.word_file = "Source/sound_word.txt"
        self.file_r = open(self.word_file, 'r').readlines()

        self.consonnes = ["b", "ç", "k", "d", "f", "g", "ñ", "j", "l", "ï", "m", "n", "p", "r", "s", "t", "v", "w", "z"]
        self.voyelles = ["a", "ã", "e", "ø", "é", "è", "î", "i", "ì", "o", "ô", "œ", "õ", "u", "ü", "y", "û"]
        self.phonemes = self.consonnes + self.voyelles

        self.PathToUserFile = self.master.PathToUserFile
        self.syllables = self.master.syllables
        self.butt_logo = self.master.butt_logo
        self.vitesse = self.master.vitesse
        self.timbre = self.master.timbre
        self.volume = self.master.volume

    def Verification(self, word, new_prononciation):
        new_prononciation = [j for j in new_prononciation if j in self.phonemes]
        if f"{word}\n" in self.file_r:
            prononciation = ''.join(self.file_r[self.file_r.index(f"{word}\n") + 1])
        else:
            prononciation = Gen.Generation(word).script_phoneme[:-1]
        txt = f"Donc '{word}' se prononce {new_prononciation} plutôt que {prononciation} ?"
        return txt

    def Correction(self, word, new_prononciation, validation):
        word = word[1:-1]
        self.file_r = open(self.word_file, 'r').readlines()
        if "oui" in validation.lower():
            if f"{word}\n" in self.file_r:
                self.file_r[self.file_r.index(f"{word}\n") + 1] = f"{new_prononciation}\n"
                text = "Mot corrigé"
            else:
                self.file_r.append(f"{word}\n{new_prononciation}\n")
                text = "Mot ajouté"
            open(self.word_file, 'w').writelines(self.file_r)
        else:
            text = "Comment alors ?"
        return text


if __name__ == '__main__':
    text = "Bonjour. Désormais, le lle de balle se prononcera comme le l de bal"
    print(text)
    Answer(text).Rectification_syllable()
