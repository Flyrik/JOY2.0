# -*- coding: utf-8 -*-
# Importing
import tkinter as tk
import os
import time
import wave

import pygame
import threading
from matplotlib import pyplot as plt
import argparse
import queue
import sys
import sounddevice as sd
from vosk import Model, KaldiRecognizer

from Generation_parole import Generation

syllables = Generation("").syllables


class Jouer(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.pygame_mixer = pygame.mixer
        self.sounds_folder = "Source/Audio/Parole_en_cours"
        self.face_path = "Source/Face/face.txt"

        self.Exe()

    def Play(self, sound_path):
        self.pygame_mixer.init()
        self.pygame_mixer.music.load(f"{self.sounds_folder}/{sound_path}")
        self.pygame_mixer.music.play()
        while True:
            if self.pygame_mixer.music.get_pos() == -1:
                threading.Thread(target=self.pygame_mixer.music.stop())
                break

    def Parler(self, sound_path):
        return threading.Thread(target=self.Play(sound_path)).start()

    def Exe(self):
        # Lecture du fichier face.txt
        new_script = open(self.face_path).readlines()

        # 🔒 Sécurisation : garantir au moins 4 lignes
        while len(new_script) <= 3:
            new_script.append("\n")

        index_file = 0

        for syb in self.master.syllables:
            # Activer la bouche (ON + syllabe)
            new_script[3] = f"on {syb}\n"
            open(self.face_path, 'w').writelines(new_script)

            if syb in syllables:
                self.Parler(f"sound{index_file}.wav")
                index_file += 1
            elif syb == "pause_courte":
                time.sleep(0.25)
            else:
                time.sleep(0.5)

        # Fin de parole → bouche OFF
        self.Parler("vide.wav")

        new_script = open(self.face_path).readlines()

        # 🔒 RE-sécurisation AVANT index 3
        while len(new_script) <= 3:
            new_script.append("\n")

        new_script[3] = "off\n"
        open(self.face_path, 'w').writelines(new_script)


class Modulation:
    def __init__(self, script):
        self.script = script
        self.syllables = [i for i in Generation(self.script).Phoneme2Syllable() if i not in
                          ["pause", "pause_courte", "end"]]
        self.ponctuation = [":", ";", ",", ".", "!", "?", '"']
        if self.script[-1] not in self.ponctuation:
            self.script += '.'
        self.oral_ponctuation = []
        self.mod = [[], [], []]
        self.Adapted_mod()

    def Cut_sentence(self):
        short_script = [[]]
        i = 0
        while i < len(self.script):
            j = 0
            ponct = []
            if self.script[i] == "[" and "]" in self.script[i + 1:]:
                short_script[-1] += self.script[i:self.script[i + 1:].index("]") + i]
                i += self.script[i + 1:].index("]")
            if self.script[i] in self.ponctuation and i != 0:
                while self.script[i+j] in self.ponctuation:
                    ponct.append(self.script[i+j])
                    j += 1
                    if i + j >= len(self.script):
                        break
                short_script.append(ponct)
                if i + j >= len(self.script):
                    break
                short_script.append([])
            short_script[-1].append(self.script[i+j])
            i += 1 + j
        short_script = [[''.join(i)]for i in short_script]
        for i in range(len(short_script)-1, 0, -1):
            if short_script[i] == [' ']:
                short_script.pop(i)
        return short_script

    def Adapted_mod(self):
        self.oral_ponctuation = []
        cut_script = self.Cut_sentence()
        for i in range(1, len(cut_script), 2):
            self.oral_ponctuation.append([])
            cut_script[i] = [i for i in cut_script[i][0]]
            if "?" in cut_script[i]:
                self.oral_ponctuation[-1].append("interrogation")
            if "!" in cut_script[i]:
                self.oral_ponctuation[-1].append("exclamation")
            if i > 1:
                if '"' in cut_script[i-2] and '"' in cut_script[i] or ":" in cut_script[i-2]:
                    self.oral_ponctuation[-1].append("énonciation")
            if not self.oral_ponctuation[-1]:
                self.oral_ponctuation[-1].append("neutre")

        for i in range(0, len(cut_script), 2):
            size = len([i for i in Generation(cut_script[i][0]).Phoneme2Syllable() if i not in
                        ["pause", "pause_courte", "end"]])
            self.mod = [self.mod[j]+[round(i[j], 2) for i in self.Filters(size, self.oral_ponctuation[int(i/2)])]
                        for j in range(3)]

        return self.oral_ponctuation

    @staticmethod
    def Filters(size, ponct):
        filtre = [[1.0, 1.0, 0.0] for _ in range(size)]
        for i in range(size):
            prop = (i + 1) / size
            if "interrogation" in ponct:
                if prop < .26:
                    filtre[i][0] += prop * 4 * .05
                    filtre[i][1] -= prop * 4 * .05
                elif .26 <= prop < .6:
                    filtre[i][0] += 0
                elif i == size - 1:
                    filtre[i][0] += .1
                    filtre[i][1] -= .05
                else:
                    filtre[i][0] -= (prop / (size - (size / 3)) * i) / 10 - .08
                    filtre[i][1] += (i % 2 * 2 - 1) * .025
                if .26 > prop or prop > .74:
                    filtre[i][2] += prop % .75 * 4 * 5
            if "exclamation" in ponct:
                filtre[i][0] += (i - (size / 2.5)) / ((i + 1) * 50)
                filtre[i][1] -= ((i - (size / 2)) / (i + 1) + 1.5) / 20
                filtre[i][2] += prop * 5
            if "énonciation" in ponct:
                if prop >= .85 and i != 0:
                    filtre[i][0] = filtre[i - 1][0] - ((size-i) / i) - filtre[int(size * .85) - 1][0] + 1
                    filtre[i][1] -= prop * .05
                    filtre[i][2] += (prop - 1) * 10 + 5
                filtre[i][0] += prop * .2
                filtre[i][1] -= prop * .05
                filtre[i][2] += (prop - 1) * 10 + 5
            elif "neutre" in ponct:
                if prop < .26 or i == 0:
                    filtre[i][0] -= prop * 4 * .1
                if i == size - 1:
                    filtre[i][0] += .1
                    filtre[i][1] -= .1
                    filtre[i][2] += 5
                else:
                    filtre[i][0] += (prop + .25) * .1
                    filtre[i][1] -= (prop + .25) * .1
                    filtre[i][2] += (prop + .25) * 5

            filtre[i] = [max(min(filtre[i][0], 1.75), .5), max(min(filtre[i][1], 1.25), .95),
                         max(min(filtre[i][2], 10), -10)]

        return filtre

    def Plotting(self):
        size = [i for i in range(len(self.syllables))]
        fig, axis = plt.subplots(3, 1)
        fig.suptitle("Modulation")

        for i in range(3):
            axis[i].plot(size, self.mod[i], label="Sans Lissage", color=["blue", "green", "black"][i])
            axis[i].legend()
            axis[i].set_xlabel("Syllable_index")
            axis[i].set_ylabel(["Vitesse", "Timbre", "Volume"][i])
            axis[i].grid(True)


class Setting(tk.Frame):
    def __init__(self, master, script, vit=1.0, timbre=1.0, volume=0):
        super().__init__(master)

        self.script = script
        self.modulation = Modulation(script).mod
        self.vitesses = [i * vit for i in self.modulation[0]]
        self.timbres = [i * timbre for i in self.modulation[1]]
        self.volumes = [i + volume for i in self.modulation[2]]
        self.sounds_folder = "Source/Audio/Parole_en_cours"
        self.list_dir = []
        self.exception = ""
        self.Exe()

    def Exe(self):
        self.Delete_file()
        for i in self.master.syllables:
            if i in syllables:
                index = len(self.list_dir)
                self.list_dir.append(f"{self.sounds_folder}/sound{index}.wav")

        actual_syllables_used = [i for i in self.master.syllables if i not in ["pause", "pause_courte", "end"]]
        (Parler("", self.list_dir, vit=self.vitesses, timbre=self.timbres, volume=self.volumes)
         .Son(actual_syllables_used))

    def Delete_file(self):
        for i in os.listdir(self.sounds_folder):
            if i != "vide.wav":
                try:
                    os.remove(f"{self.sounds_folder}/{i}")
                except Exception as e:
                    self.exception = e
                    pass


class Parler:
    def __init__(self, script, sound_path=None, vit=None, timbre=None, volume=None):
        self.script = script
        self.sound_path = sound_path
        self.vit = vit
        self.timbre_voix = timbre
        self.volume = volume

        self.gen_son = Generation(script=script, sound_file=sound_path, vitesse=self.vit, timbre=self.timbre_voix,
                                  volume=self.volume)

    def Son(self, syllable=None):
        self.gen_son.Syllable2son(syllable)


class Audio2text(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.q = queue.Queue()
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument(
            "-l", "--list-devices", action="store_true",
            help="show list of audio devices and exit")
        self.args, self.remaining = self.parser.parse_known_args()
        if self.args.list_devices:
            print(sd.query_devices())
            self.parser.exit(0)
        self.parser = argparse.ArgumentParser(description=__doc__,
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              parents=[self.parser])
        self.parser.add_argument("-f", "--filename", type=str, metavar="FILENAME",
                                 help="audio file to store recording to")
        self.parser.add_argument("-d", "--device", type=self.int_or_str,
                                 help="input device (numeric ID or substring)")
        self.parser.add_argument("-r", "--samplerate", type=int, help="sampling rate")
        self.parser.add_argument("-m", "--model", type=str, help="language model; e.g. fr")
        self.args = self.parser.parse_args(self.remaining)

        if self.args.samplerate is None:
            device_info = sd.query_devices(self.args.device, "input")
            # soundfile expects an int, sounddevice provides a float:
            self.args.samplerate = int(device_info["default_samplerate"])
        if self.args.model is None:
            self.model = Model(lang="fr")
        else:
            self.model = Model(lang=self.args.model)

        if self.args.filename:
            self.dump_fn = open(self.args.filename, "wb")
        else:
            self.dump_fn = None

    @staticmethod
    def int_or_str(text):
        try:
            return int(text)
        except ValueError:
            return text

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def Exe(self):
        with sd.RawInputStream(samplerate=self.args.samplerate, blocksize=8000, device=self.args.device, dtype="int16",
                               channels=1,
                               callback=self.callback):
            print("Écoute en cours...")

            rec = KaldiRecognizer(self.model, self.args.samplerate)
            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    return rec.Result()[14:-3]
                if self.dump_fn is not None:
                    self.dump_fn.write(data)


if __name__ == "__main__":
    text = "Mot ajouté"
    text_neutre = "Bonjour, je suis heureux de faire ta connaissance Médéric. Comment vas-tu aujourd'hui."
    modulation = Modulation(text)
    print(text)
    print(modulation.Cut_sentence())
    print(modulation.oral_ponctuation)
    print(modulation.syllables)
    print(Generation(text).Phoneme2Syllable())
    print(modulation.mod)
    print(len(modulation.mod[0]), len(modulation.mod[1]), len(modulation.mod[2]))
    print(len([i for i in Generation(text).Phoneme2Syllable() if i not in ["pause", "pause_courte", "end"]]))
    print(modulation.Plotting())
    plt.show()
    obj = wave.open("Source/Audio/Parole_en_cours/vide.wav", 'w')
    obj.setnchannels(1)
    obj.setsampwidth(2)
    obj.setframerate(44100)
    obj.writeframes(bytes(1)*1000)
    obj.close()
    # Setting(script=text, vit=1.1, timbre=.7, volume=0)
    # Jouer()
