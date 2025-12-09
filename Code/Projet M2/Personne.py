# -*- coding: utf-8 -*-
import os
import json

path_people = "Source/People_set"


class Personne:
    def __init__(self, lien=None, first_name=None, last_name=None, age=None, genre=None, physique=None, anecdote=None):
        self.lien = lien
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.genre = genre
        self.physique = physique
        self.anecdote = anecdote

    def to_dict(self):
        return self.__dict__

    def New_people(self):
        last_index = len(os.listdir(path_people))
        json.dump(self.to_dict(), open(f"{path_people}/people{str(last_index)}.json", 'w'), indent=3)

    def Maj_people(self, filename):
        people = self.load_from_json(filename)
        pers = Personne(lien=self.lien or people.lien, first_name=self.first_name or people.first_name, last_name=self.last_name or people.last_name, age=self.age or people.age, genre=self.genre or people.genre, physique=self.physique or people.physique, anecdote=self.anecdote or people.anecdote)
        json.dump(pers.to_dict(), open(f"{path_people}/{filename}", 'w'), indent=3)

    def Maj_feature(self, list_feat):
        file_py = open('Personne.py', "r").readlines()
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
            file_py[index_end_init + 9] = f"{file_py[index_end_init + 9][:-2]}, {', '.join([f'{i}=self.{i} or people.{i}' for i in list_feat])})\n"
            open('Personne.py', "w").writelines(file_py)

    def Info(self, filename):
        presentation = ""
        people = self.load_from_json(filename)
        if people.genre == "male":
            pronom_personal = "il"
            pronom_demonstrative = "celui"
            pronom_demonstrative = "lequel"
            pronom_definite = "le"
            pronom_indefinite = "un"
            if int(people.age) < 18:
                civility = "garçon"
            else:
                civility = "homme"
        elif people.genre == "female":
            pronom_personal = "elle"
            pronom_demonstrative = "celle"
            pronom_demonstrative = "laquelle"
            pronom_definite = "la"
            pronom_indefinite = "une"
            if int(people.age) < 18:
                civility = "fille"
            else:
                civility = "femme"
        else:
            pronom_personal = "iel"
            pronom_demonstrative = "celui ou celle"
            pronom_demonstrative = "lequel ou laquelle"
            pronom_definite = "le"
            pronom_indefinite = "une"
            civility = "personne"

        if people.first_name is not None or people.last_name is not None:
            if people.first_name is not None:
                presentation += people.first_name
                if people.last_name is not None:
                    presentation += " "
            if people.last_name is not None:
                presentation += people.last_name
        else:
            presentation += f"Je ne sais pas comment {pronom_personal} s'appelle, mais"

        if people.age is not None:
            if people.first_name is None and people.last_name is None:
                presentation += f" {pronom_personal}"
            presentation += f" a {people.age} an"
            if people.age > 1:
                presentation += "s"
            presentation += "."

        if self.physique != "" and self.physique is not None:
            presentation += f"{pronom_personal} est {pronom_indefinite} {civility}"
            presentation += self.physique

        presentation += "."

        if people.lien is not None:
            presentation += f" Et {pronom_personal} est "
            if " de " in people.lien or " d'" in people.lien:
                presentation += "l"
                if people.lien[0] in ["a", "e", "é", "è", "ê", "ë", "i", "î", "ï", "o", "u", "y", "h"]:
                    presentation += "'"
                else:
                    prem_mot = ""
                    for i in people.lien:
                        if i != " ":
                            prem_mot += i
                        else:
                            prem_mot += i
                            break
                    if self.Genre(prem_mot) == "m":
                        presentation += "e "
                    else:
                        presentation += pronom_definite[1]
            else:
                presentation += "votre "
            presentation += f"{people.lien}"

        else:
            presentation += f" J'ignore cependant qui {pronom_personal} est pour toi."

        return presentation

    def Genre(self, mot):
        if mot in ["ami ", "cousin ", "fils ", "frère ", "père ", "oncle ", "chat ", "chien ", "hamster ", "oiseau ", "poisson ", "animal ", "patron ", "chef ", "professeur ", "médecin "]:
            return "m"
        else:
            return "f"

    def load_from_json_set(self):
        for i in os.listdir(path_people):
            print(self.load_from_json(i).Info(i))

    @classmethod
    def load_from_json(cls, filename):
        with open(f"{path_people}/{filename}", 'r') as json_file:
            data = json.load(json_file)
            return cls(**data)


class Physique:
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


for i in os.listdir(path_people):
    Personne().Maj_people(i)

if __name__ == "__main__":
    """print(Personne().Info("people0.json"))
    (Personne(lien="ami", first_name="Médéric", last_name="Rousseau", age=24, genre="male",
              physique=Physique(taille="1m80", taille_cheveux="courts", couleur_cheveux="bleus").Info()).
     Maj_people("people0.json"))
    Personne().load_from_json_set()
    Personne(lien="ami", first_name="Médéric", last_name="Rousseau", age=24, genre="male",
             physique=Physique(taille="1m80", taille_cheveux="courts", couleur_cheveux="bleus").Info()).New_people()"""

    Personne().Maj_feature(list_feat=["taille", "physique", "couleur", "yeux"])
    #Personne(genre="female").Maj_people("people0.json")
