# -*- coding: utf-8 -*-
# Importing
import math
import os
import librosa
import soundfile
from pydub import AudioSegment


class Generation:
    def __init__(self, script, part=0, sound_file=None, vitesse=None, timbre=None, volume=None):
        self.script = script
        self.part = part
        self.sound_file = sound_file
        self.vit = vitesse
        self.timbre_voix = timbre
        self.volume = volume
        if vitesse is not None:
            self.steps = [- math.log(self.timbre_voix[i]) * 10 - math.log(self.vit[i]) * 17.5 for i in range(len(vitesse))]
        self.script_phoneme = []
        self.ponctuation = [":", ";", ",", ".", "!", "?", " ", "\""]
        self.consonnes = ["b", "ç", "k", "d", "f", "g", "ñ", "j", "l", "ï", "m", "n", "p", "r", "s", "t", "v", "w", "z"]
        self.voyelles = ["a", "ã", "e", "ø", "é", "è", "î", "i", "ì", "o", "ô", "œ", "õ", "u", "ü", "y", "û"]
        self.phonemes = self.consonnes + self.voyelles
        self.syllables = [i + j for i in self.consonnes for j in self.voyelles] + self.voyelles + self.consonnes

        self.exception_path = "Source/sound_word.txt"
        self.exception_file = open(self.exception_path, 'r').readlines()

        self.Parole2phoneme()

    def Parole2phoneme(self, for_except=True):
        self.script = " " * 3 + self.script.lower() + " " * 4
        i = 3
        while self.script[i: i + 3] != "   ":
            syb = ""
            if self.script[i] == "[" and "]" in self.script[i + 1:]:
                for syl in range(i, self.script[i + 1:].index("]") + i):
                    if (self.script[syl - 1:syl + 2] in [f"'{phon}'" for phon in self.phonemes] +
                            [f"\"{phon}\"" for phon in self.phonemes]):
                        self.script_phoneme += [self.script[syl]]
                i += self.script[i + 1:].index("]")
            bol, exception = self.Exception(self.script, i)
            if for_except:
                if bol:
                    for expt in exception:
                        self.script_phoneme.append(expt)
                    index = self.exception_file.index(str(exception) + "\n") - 1
                    size_mot = len(self.exception_file[index][:-1])
                    i += size_mot
                    pass
            if self.script[i] == "u" and self.script[i - 1] in ["g", "q"]:
                pass
            elif self.script[i] in [",", ";", ":"]:
                syb = "pause_courte"
            elif self.script[i] in [".", "!", "?"]:
                syb = "pause"
            elif (self.script[i] in ["a", "e"] and self.script[i + 1] in ["m", "n"] and self.script[i + 2]
                  not in ["a", "e", "i", "o", "u", "y", "h", "m"]):
                syb = "ã"
                i += 1
            elif self.script[i:i + 3] == "ail" and self.script[i + 3] != "e":
                for syl in ["a", "i", "ï"]:
                    self.script_phoneme.append(syl)
                if self.script[i + 3] == "l":
                    i += 1
                i += 2
            elif self.script[i:i + 3] == "ing":
                syb = "î"
                i += 3
            elif self.script[i:i + 2] in ["in", "im"] and self.script[i + 2] not in ["a", "e", "i", "o", "u", "y", "h"]:
                syb = "ì"
                i += 1
            elif self.script[i:i + 3] in ["ain", "aim"]:
                if self.script[i + 3] not in self.voyelles + ["h"]:
                    syb = "ì"
                    i += 2
                else:
                    syb = "è"
                    i += 1
            elif self.script[i:i + 2] in ["ai", "aî"] and self.script[i + 2] not in self.ponctuation:
                if self.script[i:i + 4] == "aies" and self.script[i + 4] in self.ponctuation:
                    i += 1
                syb = "è"
                i += 1
            elif self.script[i:i + 2] in ["es", "ex", "aî"]:
                if self.script[i:i + 2] == "aî":
                    i += 1
                syb = "è"
            elif (self.script[i] in ["è", "ê"] or self.script[i] == "e" and self.script[i + 1:i + 3] == "lle"
                  or self.script[i:i + 2] == "ex"):
                syb = "è"
            elif self.script[i:i + 2] in ["ai", "er", "et", "ez", "ée"]:
                syb = "é"
                i += 1
            elif (self.script[i] == "é" or self.script[i] == "e" and self.script[i + 1] == self.script[i + 2]
                  and self.script[i + 1] not in self.ponctuation):
                syb = "é"
            elif self.script[i:i + 2] == "ais":
                syb = "é"
            elif self.script[i:i + 2] == "au":
                syb = "o"
                i += 1
            elif self.script[i] in ["a", "à", "â"]:
                if self.script[i + 1] == "h":
                    i += 1
                syb = "a"
            elif self.script[i] == "b":
                syb = "b"
            elif self.script[i:i + 2] in ["ch", "sh"]:
                syb = "ç"
            elif self.script[i] == "c":
                if self.script[i - 1] == "c" or self.script[i + 1] in ["e", "i", "y", "'"]:
                    syb = "s"
                else:
                    syb = "k"
            elif self.script[i] in ["k", "q", "c"]:
                syb = "k"
            elif self.script[i] == "d":
                syb = "d"
            elif self.script[i:i + 2] == "eu":
                if self.script[i + 2] == "e":
                    i += 1
                syb = "ø"
                i += 1
            elif (self.script[i] == "e" and self.script[i + 1] in self.ponctuation and self.script[i - 1]
                  in ["c", "d", "j", "l", "m", "n", "s", "t"] and self.script[i - 2] in self.ponctuation):
                syb = "e"
            elif (self.script[i] == "e" and self.script[i + 1] in self.ponctuation and self.script[i - 2:i - 1] in "qu"
                  and self.script[i - 3] in self.ponctuation):
                syb = "e"
            elif self.script[i] == "f":
                if self.script[i + 1] == "f":
                    i += 1
                syb = "f"
            elif self.script[i:i + 2] == "ph":
                syb = "f"
                i += 1
            elif self.script[i:i + 2] == "gn":
                syb = "ñ"
                i += 1
            elif self.script[i] == "g":
                if self.script[i + 1] in ["e", "é", "è", "ê", "i", "î", "ï", "y"] or self.script[i - 1] == "g":
                    if self.script[i + 1] == "e":
                        if self.script[i + 2] in ["a", "o"] or self.script[i + 2] in self.ponctuation:
                            i += 1
                    syb = "j"
                else:
                    syb = "g"

            elif self.script[i] in ["i", "î", "ï", "y"]:
                syb = "i"
            elif self.script[i] == "j":
                syb = "j"
            elif (self.script[i:i + 2] == "ll" and self.script[i - 1:i + 3] == "elle" and self.script[i - 2]
                  in self.ponctuation):
                if self.script[i + 3] in self.ponctuation:
                    syb = "l"
                    i += 2
            elif self.script[i] == "l" and self.script[i + 1] != "l":
                syb = "l"
            elif self.script[i:i + 2] == "ll":
                syb = "ï"
                i += 1
            elif self.script[i] == "n":
                syb = "n"
            elif self.script[i] == "m":
                syb = "m"
            elif self.script[i:i + 2] == "oe":
                if self.script[i + 2] == "u":
                    i += 1
                syb = "œ"
                i += 1
            elif self.script[i:i] in ["œ", "ɶ"]:
                if self.script[i + 2] == "u":
                    i += 1
                syb = "œ"
            elif self.script[i] == "o":
                if self.script[i + 1] in ["n", "m"]:
                    if (self.script[i + 2] not in ["a", "e", "i", "o", "u", "y", "n", "m"] or self.script[i + 2]
                            in self.ponctuation):
                        syb = "õ"
                        i += 1
                    if self.script[i + 1: i + 3] in ["nn", "nm", "nm", "mm"]:
                        syb = "ô"
                elif self.script[i + 1] in ["o", "u", "ù"]:
                    syb = "u"
                    i += 1
                elif self.script[i + 1] in ["i", "y"]:
                    if self.script[i + 1] == "i":
                        i += 1
                    for syl in ["w", "a"]:
                        self.script_phoneme += syl
                else:
                    syb = "o"
            elif self.script[i] == "ô":
                syb = "o"
            elif self.script[i:i + 2] == "um" and self.script[i + 2] in self.ponctuation:
                syb = "ô"
                i += 1
            elif self.script[i] == "p":
                syb = "p"
            elif self.script[i] == "r":
                if self.script[i + 1] == "r":
                    i += 1
                syb = "r"
            elif self.script[i] == "ç":
                syb = "s"
            elif self.script[i] == "s":
                if (self.script[i - 1] in ["a", "e", "é", "è", "ê", "ë", "i", "î", "ï", "o", "u", "y"]
                        and self.script[i + 1] in ["a", "e", "é", "è", "ê", "ë", "i", "î", "ï", "o", "u", "y", "h"]
                        or self.script[i + 1] == " " and self.script[i + 2]
                        in ["a", "e", "é", "è", "ê", "ë", "i", "î", "ï", "o", "u", "y", "h"]):
                    syb = "z"
                elif (self.script[i - 1] not in ["a", "e", "é", "è", "ê", "ë", "i", "î", "ï", "o", "u", "y"]
                        and self.script[i + 1] not in self.ponctuation):
                    syb = "s"
                elif (self.script[i - 1] in ["a", "e", "é", "è", "ê", "ë", "i", "î", "ï", "o", "u", "y"]
                        and self.script[i + 1] not in ["a", "e", "é", "è", "ê", "ë", "i", "î", "ï", "o", "u", "y", "h"]
                        and self.script[i + 1] not in self.ponctuation or self.script[i + 1] == "'"):
                    syb = "s"
            elif self.script[i] == "t":
                if self.script[i + 1:i + 4] == "ion":
                    syb = "s"
                if self.script[i + 1] in self.ponctuation:
                    if self.script[i + 2] in self.voyelles:
                        syb = "t"
                else:
                    syb = "t"
            elif self.script[i:i + 2] in ["un", "um"] and self.script[i + 2] not in ["a", "e", "i", "o", "u", "y"]:
                syb = "ü"
                i += 1
            elif self.script[i] == "u":
                if self.script[i + 1] == "i":
                    syb = "û"
                    i += 1
                else:
                    syb = "y"
            elif self.script[i] == "v":
                syb = "v"
            elif self.script[i] == "w":
                syb = "w"
            elif self.script[i] == "zz":
                for syl in ["d", "z"]:
                    self.script_phoneme = syl
            elif self.script[i] == "x":
                if (self.script[i + 1] in ["a", "e", "é", "è", "ê", "ë", "i", "î", "ï", "o", "u", "y", "h"]
                        and self.script[i - 1] not in ["a", "e", "é", "è", "ê", "ë", "i", "î", "ï", "o", "u", "y", "h"]
                        or self.script[i + 1] == " " and self.script[i + 2]
                        in ["a", "e", "é", "è", "ê", "ë", "i", "î", "ï", "o", "u", "y", "h"]):
                    syb = "z"
                elif self.script[i + 1] not in self.ponctuation:
                    for syl in ["s", "k"]:
                        self.script_phoneme += syl
            elif self.script[i] == "z":
                syb = "z"
            else:

                pass
            self.script_phoneme.append(syb)
            if bol:
                self.script_phoneme.pop()
            i += 1
        self.script_phoneme.append("end")
        for _ in range(2):
            index = 0
            while self.script_phoneme[index] != "end":
                if self.script_phoneme[index] == self.script_phoneme[index + 1] or self.script_phoneme[index] == "":
                    self.script_phoneme.pop(index)
                else:
                    index += 1

    def Phoneme2Syllable(self, phonemes=None):
        if phonemes is None:
            phonemes = self.script_phoneme
        syllables = []
        i = 0
        while i < len(phonemes):
            if phonemes[i] in self.consonnes and phonemes[i+1] in self.voyelles:
                syllables.append(phonemes[i]+phonemes[i+1])
                i += 1
            else:
                syllables.append(phonemes[i])
            i += 1
        return syllables

    def Syllable2son(self, syllables=None):
        if syllables is None:
            if self.part == 0:
                syllables = self.script_phoneme
            else:
                syllables = self.Phoneme2Syllable(syllables)
        index_file = 0
        for syb in syllables:
            path_sound_from = f"source/Audio/Syllables/{syb}/sound0.wav"
            if os.path.exists(path_sound_from):
                sound_path = self.sound_file[index_file]
                y, sr = librosa.load(path_sound_from)
                new_y = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=self.steps[index_file])
                new_sr = int(sr * self.vit[index_file])
                soundfile.write(sound_path, new_y, new_sr)

                sound = AudioSegment.from_wav(sound_path)
                sound = sound.set_frame_rate(44100)
                sound = sound + self.volume[index_file]
                sound.export(sound_path, format="wav")

                index_file += 1

    def Exception(self, script, index):
        for expt in [self.exception_file[i] for i in range(0, len(self.exception_file), 2)]:
            if index + len(expt[:-1]) < len(script):
                if script[index:index + len(expt[:-1])] == expt[:-1]:
                    prononciation = [i for i in self.exception_file[self.exception_file.index(expt) + 1][:-1]
                                     if i in self.phonemes]
                    return True, prononciation
        return False, None


if __name__ == '__main__':
    parole = "Donc 'balle' se prononce ['b', 'a', 'l'] plutôt que ['b', 'a', 'ï'] ?"
    gen = Generation(script=parole)
    phoneme_txt = gen.script_phoneme
    syllables_txt = gen.Phoneme2Syllable()
    print(phoneme_txt)
    print(syllables_txt)
