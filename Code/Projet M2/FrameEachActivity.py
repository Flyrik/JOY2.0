import tkinter as tk
from tkVideoPlayer import TkinterVideo
import cv2
import random

import Audio


class Activity(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.label = None
        self.path_vid = None
        self.label1 = None
        self.label2 = None
        self.label3 = None
        self.video = None
        self.configure(bg='#f0f0f0')  # Couleur de fond pour rendre la frame plus agréable
        self.grid_columnconfigure(0, weight=1)
        self.label1_num, self.label3_num = 0, 0

        self.path_vid_fun1 = "10 Minutes of Random Memes #2.mp4"
        self.path_vid_fun2 = "UNUSUAL MEMES COMPILATION V273.mp4"
        self.path_vid_fun3 = "Vidéo Courte et Drôle )  #26.mp4"
        self.path_vid_funs = [self.path_vid_fun1, self.path_vid_fun2, self.path_vid_fun3]

        self.path_vid_breath1 = "ARRÊTER LE MENTAL  respiration 4-7-8 breathing.mp4"
        self.path_vid_breath2 = "Coherence cardiaque  exercice de respiration anti-stress (5 min).mp4"
        self.path_vid_breaths = [self.path_vid_breath1, self.path_vid_breath2]

        self.path_vid_motiv1 = "Just do it! meme.mp4"
        self.path_vid_motiv2 = "DO IT (1 min).mp4"
        self.path_vid_motivs = [self.path_vid_motiv1, self.path_vid_motiv2]

        self.path_vid_yoga1 = "Easy Underwater Yoga Poses for Kids  Sea Animals  The Yoga Guppy Asana Series.mp4"
        self.path_vid_yoga2 = "The Grinch Tries Yoga.mp4"
        self.path_vid_yoga3 = "Yoga Poses.mp4"
        self.path_vid_yogas = [self.path_vid_yoga1, self.path_vid_yoga2, self.path_vid_yoga3]

        self.conseil1 = ("Travailler la confiance en soi, c’est de s’accepter tel que l’on est. Stop aux comparaisons "
                         "qui font perdre l’estime de soi ! Se comparer de façon constructive, oui, mais le faire de "
                         "façon négative, non. Votre collègue travaille plus vite que vous ? Au lieu de vous sentir "
                         "rabaissé, demandez-vous comment améliorer votre productivité.\n\nNe vous cachez pas non "
                         "plus derrière une façade. Restez vous-même. L’authenticité est nettement plus appréciée et "
                         "évite des malentendus. Et puis, ne dit-on pas : « chassez le naturel, il revient au galop ? "
                         "» Chacun est comme il est, avec ses qualités et ses défauts. N’oubliez pas : personne n’est "
                         "parfait, même si certains tendent à nous le faire croire. D’ailleurs, c’est la diversité de "
                         "chacun d’entre nous qui fait la richesse des échanges et des expériences de vie.\n\nSoyez "
                         "donc fier(e) de vous, de vos décisions et de ce que vous entreprenez au quotidien même s’il "
                         "y a des loupés. Ils font partie de la vie et ça aussi il faut l’accepter.")
        self.conseil2 = ("Échouer n’est pas une fatalité. L’échec est notre compagnon de vie depuis… toujours ! "
                         "Rappelez-vous vos premières fois : premiers pas, première fois sur le vélo sans les petites "
                         "roues, premier rendez-vous, premier entretien d’embauche… Ont-elles toutes été des "
                         "réussites ? Probablement pas. En outre, il n’y a aucune honte à connaître des échecs, "
                         "car ils permettent justement de nous améliorer. De grands dirigeants ont commis des erreurs "
                         "et ils se sont relevés en analysant le comment du pourquoi, puis ils ont rectifié le "
                         "tir.\n\nLe fait de s’accorder le droit d’échouer est par ailleurs une excellente chose pour "
                         "travailler la confiance en soi. En effet, cela permet d’être beaucoup moins dur avec "
                         "soi-même, d’être plus tolérant et de relâcher la pression. Si vous faites de votre mieux, "
                         "pourquoi vous en vouloir indéfiniment ? Arrêtez de ruminer, comprenez vos erreurs et passez "
                         "à autre chose.")
        self.conseil3 = ("Dans confiance en soi, il y a « soi », c’est-à-dire « vous ». Pour optimiser votre confiance "
                         "en vous-même, vous devez vous écouter. Qui mieux que vous sait ce qu’il vous faut pour être "
                         "épanoui ? JOY peut-être 😉? Votre intuition vous dit que ce n’est pas le bon moment de "
                         "faire telle ou telle chose ? Suivez-la et peu importe si votre entourage, pro ou perso, "
                         "vous affirme le contraire. Vous avez le droit d’avoir votre propre opinion sans pour autant "
                         "manquer de respect vis-à-vis des autres. Prendre des décisions par soi-même est un "
                         "véritable boost pour la confiance en soi. Vous montrez que vous êtes capable de prendre en "
                         "main votre vie, vos projets et que vous assumerez les résultats.")
        self.conseil4 = ("Si vous avez mené un projet à bien, quel qu’il soit, n’attendez pas systématiquement un "
                         "retour, un remerciement de votre entourage même si c’est toujours appréciable bien sûr ("
                         "reconnaissance quand tu nous tiens). Vous avez parfaitement le droit de vous féliciter "
                         "vous-même du travail accompli. Attention, il ne s’agit nullement de vous mettre en avant "
                         "avec un « moi je », mais bel et bien de vous complimenter, car vous vous êtes donné les "
                         "moyens. Peut-être avez-vous surmonté des obstacles ou mis du temps à en venir à bout. Peu "
                         "importe, vous pouvez être fier(e) du résultat obtenu. S’autocongratuler fait donc partie "
                         "des nombreux conseils pour travailler la confiance en soi, mais aussi pour la renforcer au "
                         "quotidien.")
        self.conseil5 = ("Il est difficile pour vous de dire non par peur de vous sentir rejeté(e) ou bien parce que "
                         "vous êtes d’un naturel à rendre service ? Dire oui à tout et à tout le monde affecte "
                         "grandement votre confiance en vous, car vous n’êtes plus maître de votre temps. Ce temps "
                         "nécessaire dont vous avez besoin pour gérer l’ensemble de vos obligations professionnelles "
                         "et personnelles. Conséquence ? Vous êtes débordé(e), sous pression, vous n’arrivez pas à "
                         "tout faire et vous perdez peu à peu la confiance en vos capacités.\n\nIl est temps de dire "
                         "stop et de regagner la confiance en soi en apprenant à dire non ! Ce n’est pas parce que "
                         "vous refusez d’aider un collègue ou un ami qu’il vous en tiendra rigueur. Il suffit de lui "
                         "expliquer qu’à cet instant précis vous n’avez pas le temps, mais dès que cela est possible, "
                         "ce sera avec grand plaisir. Vous avez vous aussi des obligations et il n’y a pas de raison "
                         "de vous surcharger pour alléger quelqu’un d’autre.")
        self.conseil6 = ("Pour augmenter la confiance en soi, rien de tel que de prendre des initiatives. Soyez "
                         "audacieux(se) ! Ne laissez pas systématiquement les autres passer à l’action en premier. "
                         "Vous avez des idées, des suggestions pour un projet ? Soyez-en l’initiateur(rice). En un "
                         "seul mot : osez ! C’est en faisant le premier pas que vous développerez petit à petit votre "
                         "assurance. Les prochaines initiatives n’en seront que facilitées, car votre confiance en "
                         "vous aura grandi.")
        self.conseil6 = ("Prendre des risques est essentiel pour travailler la confiance en soi. Comment prouver à "
                         "vous-même, mais aussi aux autres, que vous êtes capable de réaliser telle ou telle chose si "
                         "vous n’affrontez pas vos peurs ? La peur du jugement, la peur de l’échec ou encore la peur "
                         "de ne pas savoir ne doit pas être un frein dans vos actions. Si vous vous arrêtez à ces "
                         "pensées limitantes, vous ne parviendrez jamais à aller au-delà des difficultés. Vous "
                         "risquez donc de perdre progressivement la confiance que vous avez en vous. Pour travailler "
                         "cela, il faut donc oser, se jeter à l’eau et accepter les conséquences, bénéfiques ou non.")
        self.conseils = [self.conseil1, self.conseil2, self.conseil3, self.conseil4, self.conseil5, self.conseil6]

        self.syllables = self.master.syllables

        self.exception = None

        self.audio = Audio

    def Act(self, act):
        print(act)
        if act == "Vidéo drôle":

            self.label = "Bon visionnage !😂"
            self.path_vid = self.path_vid_funs[random.randint(0, len(self.path_vid_funs) - 1)]
            self.vid(self.label, self.path_vid)

        elif act == "Vidéo de yoga":

            self.label = "Bon visionnage !🧘‍♂️"
            self.path_vid = self.path_vid_yogas[random.randint(0, len(self.path_vid_yogas) - 1)]
            self.vid(self.label, self.path_vid)

        elif act == "Exercice de\nRespiration":

            self.label = "😊🙌"
            self.path_vid = self.path_vid_breaths[random.randint(0, len(self.path_vid_breaths) - 1)]
            self.vid(self.label, self.path_vid)

        elif act == "Vidéo de motivation":
            print(act)

            self.label = "DO IT !"
            self.path_vid = self.path_vid_motivs[random.randint(0, len(self.path_vid_motivs) - 1)]
            self.vid(self.label, self.path_vid)

        else:

            self.label1 = tk.Label(self, text="Conseil du jour:", font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
            self.label1.pack()

            rnd = random.randint(0, len(self.conseils)-1)
            self.label2 = tk.Label(self, text=self.conseils[rnd], font=('Arial', 12), bg='#f0f0f0', fg='#333',
                                   justify='center', wraplength=550)
            self.label2.pack()
            self.label2.place(x=20, y=50)
            self.master.syllables = self.master.generation.Generation(self.conseils[rnd]).Phoneme2Syllable()
            self.syllables = self.master.syllables
            self.audio.Setting(self, script=self.conseils[rnd], vit=self.master.vitesse, timbre=self.master.timbre,
                               volume=self.master.volume)
            on_off = open("Source/Face/face.txt").readlines()
            if on_off[0][:3].strip() == "on":
                self.master.logo_img = "Source/Items/logo_notif_on.png"
            else:
                self.master.logo_img = "Source/Items/logo_notif_off.png"
            self.master.photo1 = tk.PhotoImage(file=self.master.logo_img)
            self.master.butt_logo.configure(image=self.master.photo1)

    @staticmethod
    def vid_size(path_vid):
        height = cv2.VideoCapture(path_vid).get(cv2.CAP_PROP_FRAME_WIDTH)
        width = cv2.VideoCapture(path_vid).get(cv2.CAP_PROP_FRAME_HEIGHT)

        return height, width

    def vid(self, label, path_vid):

        self.label3 = tk.Label(self, text=label, font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#333')
        self.label3.pack(padx=20, pady=10)

        self.video = TkinterVideo(self.master)
        self.video.load("Source/Activities/" + path_vid)
        x, y = self.vid_size("Source/Activities/" + path_vid)
        if x > 50:
            y *= 50 / x * 2
            x = 50 * 2
        if y > 80:
            x *= 80 / y * 2
            y = 80 * 2
        self.video.grid(row=1, column=0, sticky="n", ipadx=x, ipady=y, pady=y)
        self.video.play()

    # Montrer
    def show_it(self):
        self.master.hide_all()
        self.grid(row=1, column=0, columnspan=1, sticky="nsew")

    # Cacher
    def hide_it(self):
        self.grid_forget()
        try:
            if self.label1.winfo_exists() == 1:
                self.label1_num += self.label1.winfo_exists()
                if self.label1_num > 2:
                    self.label1.destroy()
                    self.label2.destroy()
                    self.label1_num = 0
        except Exception as e:
            self.exception = e
        try:
            if self.label3.winfo_exists() == 1:
                self.label3_num += self.label3.winfo_exists()
                if self.label3_num == 2:
                    self.video.destroy()
                if self.label3_num > 2:
                    self.label3.destroy()
                    self.label3_num = 0
        except Exception as e:
            self.exception = e
