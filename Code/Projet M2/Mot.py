# -*- coding: utf-8 -*-
import os
import json

path_object = "Source/Object_set"


class Mot:
    def __init__(self, name=None, material=None, forme=None, usage=None, genre=None, taille=None):
        self.name = name
        self.material = material
        self.forme = forme
        self.usage = usage
        self.genre = genre
        self.taille = taille

    def to_dict(self):
        return self.__dict__

    def New_word(self):
        last_index = len(os.listdir(path_object))
        json.dump(self.to_dict(), open(f"{path_object}/object{str(last_index)}.json", 'w'), indent=3)

    def Maj_word(self, filename):
        object = self.load_from_json(filename)
        pers = Mot(name=self.name or object.name, material=self.material or object.material, forme=self.forme or object.forme, usage=self.usage or object.usage, genre=self.genre or object.genre, taille=self.taille or object.taille)
        json.dump(pers.to_dict(), open(f"{path_object}/{filename}", 'w'), indent=3)

    def Maj_feature(self, list_feat):
        file_py = open('Objet.py', "r").readlines()
        list_feat = [i for i in list_feat if f" {i}=" not in file_py[8]]
        if len(list_feat) != 0:
            file_py[8] = f"{file_py[8][:-3]}, {', '.join([i + '=None' for i in list_feat])}):\n"
            index_end_init = 0
            for i in file_py:
                if "def to_dict(self):" in i:
                    index_end_init = file_py.index(i)
                    break
            for i in range(len(list_feat)):
                file_py[index_end_init - 2] += f"        self.{list_feat[i]} = {list_feat[i]}\n"
            # file_py[index_end_init + len(list_feat) - 2] += "\n"
            file_py[
                index_end_init + 9] = f"{file_py[index_end_init + 9][:-2]}, {', '.join([f'{i}=self.{i} or object.{i}' for i in list_feat])})\n"
            open('Objet.py', "w").writelines(file_py)

    def Info(self, filename):
        presentation = ""
        word = self.load_from_json(filename)
        if word.genre == "male":
            pronom_personal = "il"
            pronom_demonstrative = "celui"
            pronom_demonstrative = "lequel"
            pronom_definite = "le"
            pronom_indefinite = "un"

        elif word.genre == "female":
            pronom_personal = "elle"
            pronom_demonstrative = "celle"
            pronom_demonstrative = "laquelle"
            pronom_definite = "la"
            pronom_indefinite = "une"

        else:
            pronom_personal = "ça"
            pronom_demonstrative = "celui"
            pronom_demonstrative = "lequel"
            pronom_definite = "l'"
            pronom_indefinite = "un"

        if word.name is not None:
            presentation += word.name
        else:
            presentation += f"Je ne sais pas ce que c'est,"

        if word.usage is not None:
            if word.name is None:
                presentation += f" {pronom_personal}"
            presentation += f" sert à {word.usage},"

        if self.forme != "" and self.forme is not None:
            presentation += f"{pronom_personal} est en {self.forme}"

            presentation += "."

        else:
            presentation += f" J'ignore cependant qui {pronom_personal} est pour toi."

        return presentation

    def Genre(self, mot):
        if mot in ["ami ", "cousin ", "fils ", "frère ", "père ", "oncle ", "chat ", "chien ", "hamster ", "oiseau ",
                   "poisson ", "animal ", "patron ", "chef ", "professeur ", "médecin "]:
            return "m"
        else:
            return "f"

    def load_from_json_set(self):
        for i in os.listdir(path_object):
            print(self.load_from_json(i).Info(i))

    @classmethod
    def load_from_json(cls, filename):
        with open(f"{path_object}/{filename}", 'r') as json_file:
            data = json.load(json_file)
            return cls(**data)


class Forme:
    def __init__(self, taille=None, taille_cheveux=None, couleur_cheveux=None):
        self.taille = taille
        self.taille_cheveux = taille_cheveux
        self.couleur_cheveux = couleur_cheveux

    def Info(self):
        presentation = ""
        if self.taille is not None:
            if self.taille_cheveux is not None or self.couleur_cheveux is not None:
                presentation += " qui "
        if self.taille is not None:
            presentation += f"mesure {self.taille}"
            if self.taille is not None or self.couleur_cheveux is not None:
                presentation += ", et "
        if self.taille_cheveux is not None:
            presentation += f"a de {self.taille_cheveux} cheveux"
            if self.couleur_cheveux is not None:
                presentation += f" {self.couleur_cheveux}"
        elif self.couleur_cheveux is not None:
            presentation += f"a des cheveux {self.couleur_cheveux}"

        return presentation


for i in os.listdir(path_object):
    Mot().Maj_word(i)

if __name__ == "__main__":
    Mot().Maj_feature(list_feat=["taille"])
    # Objet(genre="female").Maj_object("object.json")
