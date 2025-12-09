# -*- coding: utf-8 -*-
# Importing libraries
import cv2
import numpy as np
from tensorflow.keras.models import load_model as load_model
from datetime import datetime


class Visage:
    def __init__(self, user, test=None, display=False):
        self.user = user
        self.display = display
        self.test = test

        self.xc, self.yc = 314, 215
        self.xc_face, self.yc_face = 314, 215
        self.d = 0
        self.vit = 5

        self.int_face = 0

        self.sourcil_gauche = [self.Sourcil_gauche()]
        self.sourcil_droit = [self.Sourcil_droit()]
        self.oeil_gauche = [self.Oeil_gauche()]
        self.oeil_droit = [self.Oeil_droit()]
        self.joues = [self.Joues()]
        self.bouche = [self.Bouche()]
        self.langue = [self.Langue()]

        self.emotion = None
        self.parole = False
        self.model_face = load_model("Source/Models/model_face.h5")
        self.classes = ["Asma", "Clorinda", "Médéric", "Pierre", "Sarah"]

        self.face_txt = ""
        self.on_off = True
        self.Affichage()

    @staticmethod
    def Detection_visage(classifier, image):
        classifier = cv2.CascadeClassifier(classifier)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        return classifier.detectMultiScale(gray, 1.1, 4)

    def Prediction(self, image):
        prediction = self.model_face.predict(image)
        return self.classes[np.argmax(prediction)]

    def Centre(self, classifier, image):
        x_y_w_h = self.Detection_visage(classifier, image)
        if len(x_y_w_h) != 0:
            x, y, w, h = x_y_w_h[0]
            self.xc = int((2 * x + w) / 2)
            self.yc = int((2 * y + h) / 2)
        for x, y, w, h in x_y_w_h:
            final_image = image[y:y + h, x:x + w]
            final_image = cv2.resize(final_image, (224, 224))
            final_image = np.expand_dims(final_image, axis=0)
            final_image = final_image / 255
            if self.Prediction(final_image) == self.user:
                self.xc = int((2 * x + w) / 2)
                self.yc = int((2 * y + h) / 2)
                break

    def Tracking(self, classifier, image):
        self.Centre(classifier, image)
        self.d = np.sqrt((self.xc_face - self.xc) ** 2 + (self.yc_face - self.yc) ** 2)
        if self.d > 5:
            self.xc_face += int((self.xc - self.xc_face) / self.vit)
            self.yc_face += int((self.yc - self.yc_face) / self.vit)

    def Sourcil_gauche(self, emotion="neutre"):
        if emotion in ["neutre", "ronfle"]:
            x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = -85, -60, -65, -75, -35, -75, -33, -70, -62, -70
        elif emotion in ["surpris", "perplexe", "triste", "embêté", "loufoque", "joyeux", "clin", "veille"]:
            x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = -85, -65, -70, -80, -45, -85, -40, -80, -65, -75
        elif emotion in ["timide", "dragueur"]:
            x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = -85, -65, -65, -75, -35, -75, -33, -70, -62, -70
        else:
            x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = self.Current_face()[0]

        return x1, y1, x2, y2, x3, y3, x4, y4, x5, y5

    def Sourcil_droit(self, emotion="neutre"):
        if emotion in ["neutre", "ronfle"]:
            x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = 85, -60, 65, -75, 35, -75, 33, -70, 62, -70
        elif emotion in ["surpris", "triste", "embêté", "loufoque", "joyeux", "veille"]:
            x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = 85, -65, 70, -80, 45, -85, 40, -80, 65, -75
        elif emotion in ["perplexe", "timide", "dragueur", "clin"]:
            x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = 85, -65, 65, -75, 35, -75, 33, -70, 62, -70
        else:
            x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = self.Current_face()[1]

        return x1, y1, x2, y2, x3, y3, x4, y4, x5, y5

    def Oeil_gauche(self, emotion="neutre"):
        if emotion in ["neutre", "surpris", "triste", "embêté"]:
            xc, yc = -50, -55
            axe_x, axes_y = 10, 10
            angle, start_angle, end_angle = 0, 90, 450
        elif emotion in ["perplexe"]:
            xc, yc = -45, -55
            axe_x, axes_y = 10, 10
            angle, start_angle, end_angle = 0, 90, 450
        elif emotion in ["timide", "dragueur"]:
            xc, yc = -35, -50
            axe_x, axes_y = 10, 10
            angle, start_angle, end_angle = 0, 90, 450
        elif emotion in ["loufoque"]:
            xc, yc = -20, -60
            axe_x, axes_y = 10, 10
            angle, start_angle, end_angle = 0, 90, 450
        elif emotion in ["joyeux"]:
            xc, yc = -50, -55
            axe_x, axes_y = 10, 12
            angle, start_angle, end_angle = 0, 150, 390
        elif emotion in ["veille"]:
            xc, yc = -50, -55
            axe_x, axes_y = 10, 10
            angle, start_angle, end_angle = 0, -30, 210
        else:
            xc, yc, axe_x, axes_y, angle, start_angle, end_angle = self.Current_face()[2]

        return xc, yc, axe_x, axes_y, angle, start_angle, end_angle

    def Oeil_droit(self, emotion="neutre"):
        if emotion in ["neutre", "surpris", "triste", "embêté"]:
            xc, yc = 50, -55
            axe_x, axes_y = 10, 10
            angle, start_angle, end_angle = 0, 90, 450
        elif emotion in ["perplexe"]:
            xc, yc = 55, -55
            axe_x, axes_y = 10, 10
            angle, start_angle, end_angle = 0, 90, 450
        elif emotion in ["timide", "dragueur"]:
            xc, yc = 75, -50
            axe_x, axes_y = 10, 10
            angle, start_angle, end_angle = 0, 90, 450
        elif emotion in ["loufoque"]:
            xc, yc = 20, -45
            axe_x, axes_y = 10, 10
            angle, start_angle, end_angle = 0, 90, 450
        elif emotion in ["joyeux"]:
            xc, yc = 50, -55
            axe_x, axes_y = 10, 12
            angle, start_angle, end_angle = 0, 150, 390
        elif emotion in ["clin"]:
            xc, yc = self.Current_face()[3][:2]
            axe_x, axes_y = 10, 0
            angle, start_angle, end_angle = 0, 90, 450
        elif emotion in ["veille"]:
            xc, yc = 50, -55
            axe_x, axes_y = 10, 10
            angle, start_angle, end_angle = 0, -30, 210
        else:
            xc, yc, axe_x, axes_y, angle, start_angle, end_angle = self.Current_face()[3]

        return xc, yc, axe_x, axes_y, angle, start_angle, end_angle

    @staticmethod
    def Joues(emotion="neutre"):
        if emotion == "timide":
            xc1, yc1 = -60, -15
            xc2, yc2 = 60, -15
            axe_x, axe_y = 20, 15
            angle, start_angle, end_angle = 0, 0, 360
        else:
            xc1, yc1 = -60, -15
            xc2, yc2 = 60, -15
            axe_x, axe_y = 0, 0
            angle, start_angle, end_angle = 0, 0, 360

        return xc1, yc1, xc2, yc2, axe_x, axe_y, angle, start_angle, end_angle

    def Bouche(self, emotion="neutre"):
        if emotion in ["neutre", "timide"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 17
            axe1x, axes1y, axe2x, axes2y = 40, 20, 40, 20
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        elif emotion in ["surpris", "veille"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 20
            axe1x, axes1y, axe2x, axes2y = 30, 25, 25, 20
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        elif emotion in ["perplexe", "embêté"]:
            xc1, yc1 = 10, 20
            xc2, yc2 = 10, 22
            axe1x, axes1y, axe2x, axes2y = 40, 5, 40, 4
            angle1, start_angle1, end_angle1 = 5, 0, 360
            angle2, start_angle2, end_angle2 = 5, 0, 360
        elif emotion in ["triste"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 22
            axe1x, axes1y, axe2x, axes2y = 40, 10, 40, 9
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        elif emotion in ["joyeux"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 16
            axe1x, axes1y, axe2x, axes2y = 40, 30, 40, 30
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        elif emotion in ["dragueur", "clin"]:
            xc1, yc1 = 20, 20
            xc2, yc2 = 16, 18
            axe1x, axes1y, axe2x, axes2y = 40, 30, 40, 30
            angle1, start_angle1, end_angle1 = -5, -5, 180
            angle2, start_angle2, end_angle2 = -5, 0, 360
        elif emotion in ["ronfle"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 20
            axe1x, axes1y, axe2x, axes2y = 20, 20, 18, 18
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        else:
            (xc1, yc1, xc2, yc2, axe1x, axes1y, axe2x, axes2y, angle1, start_angle1, end_angle1, angle2, start_angle2,
             end_angle2) = self.Current_face()[5]

        return (xc1, yc1, xc2, yc2, axe1x, axes1y, axe2x, axes2y, angle1, start_angle1, end_angle1, angle2,
                start_angle2, end_angle2)

    @staticmethod
    def Langue(emotion="neutre"):
        if emotion == "loufoque":
            xc1, yc1 = 20, 30
            xc2, yc2 = 20, 30
            axe1x, axes1y, axe2x, axes2y = 10, 30, 8, 28
            angle1, start_angle1, end_angle1 = -45, 0, 180
            angle2, start_angle2, end_angle2 = -45, 0, 180
        else:
            xc1, yc1 = 20, 30
            xc2, yc2 = 20, 30
            axe1x, axes1y, axe2x, axes2y = 0, 0, 0, 0
            angle1, start_angle1, end_angle1 = -45, 0, 180
            angle2, start_angle2, end_angle2 = -45, 0, 180

        return (xc1, yc1, xc2, yc2, axe1x, axes1y, axe2x, axes2y, angle1, start_angle1, end_angle1, angle2,
                start_angle2, end_angle2)

    def Parole(self, face_init, phoneme):
        if phoneme in ["a", "ã", "é", "è", "g", "l", "t", "û"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 20
            axe1x, axes1y, axe2x, axes2y = 20, 18, 18, 16
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        elif phoneme in ["b", "m", "p"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 22
            axe1x, axes1y, axe2x, axes2y = 30, 5, 30, 3
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        elif phoneme in ["ç", "j", "ñ", "n", "r", "s", "z"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 20
            axe1x, axes1y, axe2x, axes2y = 15, 20, 13, 18
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        elif phoneme in ["e", "ø", " o", "ô", "œ", "õ", "u", "ü", "y", "w"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 20
            axe1x, axes1y, axe2x, axes2y = 15, 15, 13, 13
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        elif phoneme in ["k", "d"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 20
            axe1x, axes1y, axe2x, axes2y = 30, 5, 30, 3
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        elif phoneme in ["f", "v"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 22
            axe1x, axes1y, axe2x, axes2y = 40, 5, 40, 3
            angle1, start_angle1, end_angle1 = 0, 180, 360
            angle2, start_angle2, end_angle2 = 0, 180, 360
        elif phoneme in ["ì"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 20
            axe1x, axes1y, axe2x, axes2y = 25, 15, 23, 13
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        elif phoneme in ["î", "i"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 20
            axe1x, axes1y, axe2x, axes2y = 40, 10, 38, 8
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        elif phoneme in ["ï"]:
            xc1, yc1 = 0, 20
            xc2, yc2 = 0, 20
            axe1x, axes1y, axe2x, axes2y = 30, 18, 28, 16
            angle1, start_angle1, end_angle1 = 0, 0, 360
            angle2, start_angle2, end_angle2 = 0, 0, 360
        else:
            (xc1, yc1, xc2, yc2, axe1x, axes1y, axe2x, axes2y, angle1, start_angle1, end_angle1, angle2, start_angle2,
             end_angle2) = self.Current_face()[5]

        cv2.ellipse(face_init, (self.xc_face + xc1, self.yc_face + yc1), (axe1x, axes1y), angle1,
                    start_angle1, end_angle1, (255, 255, 255), -1)
        cv2.ellipse(face_init, (self.xc_face + xc2, self.yc_face + yc2), (axe2x, axes2y), angle2,
                    start_angle2, end_angle2, (0, 0, 0), -1)

    def Coordinates(self, emotion_to="neutre"):
        faces = [i for i in self.Current_face()]
        size = len(faces)
        self_face_funct = [self.Sourcil_gauche(emotion_to), self.Sourcil_droit(emotion_to),
                           self.Oeil_gauche(emotion_to), self.Oeil_droit(emotion_to), self.Joues(emotion_to),
                           self.Bouche(emotion_to), self.Langue(emotion_to)]
        self_face = [[[int(faces[i][j] + k * (self_face_funct[i][j] - faces[i][j]) / 10) for j in range(len(faces[i]))]
                      for k in range(10)] for i in range(size)]
        self.sourcil_gauche = self_face[0]
        self.sourcil_gauche.append([f for f in self_face_funct[0]])
        self.sourcil_droit = self_face[1]
        self.sourcil_droit.append([f for f in self_face_funct[1]])
        self.oeil_gauche = self_face[2]
        self.oeil_gauche.append([f for f in self_face_funct[2]])
        self.oeil_droit = self_face[3]
        self.oeil_droit.append([f for f in self_face_funct[3]])
        self.joues = self_face[4]
        self.joues.append([f for f in self_face_funct[4]])
        self.bouche = self_face[5]
        self.bouche.append([f for f in self_face_funct[5]])
        self.langue = self_face[6]
        self.langue.append([f for f in self_face_funct[6]])

        self.int_face = 0

    def Face(self, classifier, face_init, image):
        self.Tracking(classifier, image)

        # Sourcil gauche
        x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = self.sourcil_gauche[self.int_face]
        points = np.array([[self.xc_face + x1, self.yc_face + y1], [self.xc_face + x2, self.yc_face + y2],
                           [self.xc_face + x3, self.yc_face + y3], [self.xc_face + x4, self.yc_face + y4],
                           [self.xc_face + x5, self.yc_face + y5]], np.int32)
        cv2.polylines(face_init, [points], True, (255, 255, 255), 2)

        # Sourcil droit
        x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = self.sourcil_droit[self.int_face]
        points = np.array([[self.xc_face + x1, self.yc_face + y1], [self.xc_face + x2, self.yc_face + y2],
                           [self.xc_face + x3, self.yc_face + y3], [self.xc_face + x4, self.yc_face + y4],
                           [self.xc_face + x5, self.yc_face + y5]], np.int32)
        cv2.polylines(face_init, [points], True, (255, 255, 255), 2)

        # Œil gauche
        xc, yc, axe_x, axes_y, angle, start_angle, end_angle = self.oeil_gauche[self.int_face]
        if self.xc != self.xc_face and self.d > 10:
            ecart = min([15, int(self.d / self.vit)]) * int((self.xc - self.xc_face) /
                                                            np.sqrt(((self.xc - self.xc_face) ** 2)))
            xc += ecart
        if self.yc != self.yc_face and self.d > 5:
            ecart = min([5, int(self.d / self.vit)]) * int((self.yc - self.yc_face) /
                                                           np.sqrt(((self.yc - self.yc_face) ** 2)))
            yc += ecart

        cv2.ellipse(face_init, (self.xc_face + xc, self.yc_face + yc), (axe_x, axes_y), angle,
                    start_angle, end_angle, (255, 255, 255), 2)

        # Œil droit
        xc, yc, axe_x, axes_y, angle, start_angle, end_angle = self.oeil_droit[self.int_face]
        if self.xc != self.xc_face and self.d > 10:
            ecart = min([15, int(self.d / self.vit)]) * int((self.xc - self.xc_face) /
                                                            np.sqrt(((self.xc - self.xc_face) ** 2)))
            xc += ecart
        if self.yc != self.yc_face and self.d > 5:
            ecart = min([5, int(self.d / self.vit)]) * int((self.yc - self.yc_face) /
                                                           np.sqrt(((self.yc - self.yc_face) ** 2)))
            yc += ecart

        cv2.ellipse(face_init, (self.xc_face + xc, self.yc_face + yc), (axe_x, axes_y), angle,
                    start_angle, end_angle, (255, 255, 255), 2)

        # Joues
        xc1, yc1, xc2, yc2, axe_x, axe_y, angle, start_angle, end_angle = self.joues[self.int_face]
        cv2.ellipse(face_init, (self.xc_face + xc1, self.yc_face + yc1), (axe_x, axe_y), angle,
                    start_angle, end_angle, (5, 5, 50), -1)
        cv2.ellipse(face_init, (self.xc_face + xc2, self.yc_face + yc2), (axe_x, axe_y), angle,
                    start_angle, end_angle, (5, 5, 50), -1)

        if not self.parole:
            # Bouche
            (xc1, yc1, xc2, yc2, axe1x, axes1y, axe2x, axes2y, angle1, start_angle1, end_angle1, angle2, start_angle2,
             end_angle2) = self.bouche[self.int_face]
            cv2.ellipse(face_init, (self.xc_face + xc1, self.yc_face + yc1), (axe1x, axes1y), angle1,
                        start_angle1, end_angle1, (255, 255, 255), -1)
            cv2.ellipse(face_init, (self.xc_face + xc2, self.yc_face + yc2), (axe2x, axes2y), angle2,
                        start_angle2, end_angle2, (0, 0, 0), -1)

            # Langue
            (xc1, yc1, xc2, yc2, axe1x, axes1y, axe2x, axes2y, angle1, start_angle1, end_angle1, angle2, start_angle2,
             end_angle2) = self.langue[self.int_face]
            cv2.ellipse(face_init, (self.xc_face + xc1, self.yc_face + yc1), (axe1x, axes1y), angle1,
                        start_angle1, end_angle1, (255, 255, 255), -1)
            cv2.ellipse(face_init, (self.xc_face + xc2, self.yc_face + yc2), (axe2x, axes2y), angle2,
                        start_angle2, end_angle2, (0, 0, 0), -1)

        if self.int_face < 10:
            self.int_face += 1

    def Current_face(self):
        sourcil_gauche = self.sourcil_gauche[self.int_face]
        sourcil_droit = self.sourcil_droit[self.int_face]
        oeil_gauche = self.oeil_gauche[self.int_face]
        oeil_droit = self.oeil_droit[self.int_face]
        joues = self.joues[self.int_face]
        bouche = self.bouche[self.int_face]
        langue = self.langue[self.int_face]

        return sourcil_gauche, sourcil_droit, oeil_gauche, oeil_droit, joues, bouche, langue

    def Maj_face_txt(self):
        emotion_to = self.face_txt[2][:-1].strip()
        if emotion_to != self.emotion:
            if emotion_to == "veille":
                self.face_txt[1] = f"{datetime.now().minute % 60} {datetime.now().second}\n"
                open("Source/Face/face.txt", 'w').writelines(self.face_txt)
                if self.emotion != "pré_som":
                    self.emotion = "pré_som"
                    self.Coordinates("neutre")
                elif self.int_face == 10:
                    self.oeil_gauche[10][-2:] = -90, 270
                    self.oeil_droit[10][-2:] = -90, 270
                    self.emotion = emotion_to
                    self.Coordinates(emotion_to)
            else:
                self.face_txt[1] = "\n"
                open("Source/Face/face.txt", 'w').writelines(self.face_txt)
                self.emotion = emotion_to
                self.Coordinates(emotion_to)

        # arrêt de cam et affichage du visage après 5 min de veille
        if emotion_to in ["veille", "ronfle"]:
            if (((datetime.now().minute - 5) % 60 > int(self.face_txt[1][:2].strip()) or (datetime.now().minute - 5) %
                 60 == int(self.face_txt[1][:2].strip())) and datetime.now().minute) >= int(self.face_txt[1][2:-2]):
                self.on_off = False

        if self.emotion == "veille" and self.int_face == 10:
            self.emotion = "ronfle"
            self.face_txt[2] = "ronfle\n"
            open("Source/Face/face.txt", 'w').writelines(self.face_txt)
            self.Coordinates("ronfle")
        if self.emotion == "ronfle" and self.int_face == 10:
            self.emotion = "veille"
            self.face_txt[2] = "veille\n"
            open("Source/Face/face.txt", 'w').writelines(self.face_txt)
            self.Coordinates("veille")

    @staticmethod
    def Show_frame(name_win, image):
        cv2.imshow(name_win, image)

    def Affichage(self):
        cam = cv2.VideoCapture(0)
        while True:
            self.face_txt = open("Source/Face/face.txt").readlines()
            frame = np.zeros((500, 500, 3), dtype=np.uint8)

            # Conditions to close camera and extract picture
            if self.test is not None:
                frame = cv2.imread(self.test)
            elif self.face_txt[0][:3].strip() == "off":
                if cam.isOpened():
                    cam.release()
                    self.xc, self.yc = 314, 215
            else:
                if not cam.isOpened():
                    cam.open(0)
            if cam.isOpened():
                _, frame = cam.read()
                x, y = frame.shape[:2]
                frame = np.array([[frame[i, -j - 1] for j in range(y)] for i in range(x)])

            frame = cv2.resize(frame, (500, 500))

            if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q')] or not self.on_off:
                break

            face_init = np.zeros((1000, 750, 3), dtype=np.uint8)
            if self.display:
                retour = frame
            else:
                retour = face_init

            self.Maj_face_txt()

            parole = self.face_txt[3][:3].strip()
            phonemes = self.face_txt[3][2:-1].strip()
            if parole == "on":
                self.parole = True
                self.Parole(face_init, phonemes)
            else:
                self.parole = False

            self.Face("Source/Face/face.xml", retour, frame)

            self.Show_frame('Face JOY', retour)


if __name__ == '__main__':
    mode_test = 'source/test/deux_visages.jpg'

    visage = Visage("Médéric")
