# # -*- coding: utf-8 -*-
# # Importing libraries
# import tensorflow as tf
# import cv2
# import numpy as np


# class Reconnaissance:
#     def __init__(self, classifiers, models=None, classes=None):
#         self.img_size = 224
#         self.classifiers = classifiers
#         if models is None:
#             self.models = ["" for _ in range(len(self.classifiers))]
#         else:
#             self.models = models
#             for model in self.models:
#                 if model != "":
#                     if str(type(model)) == "<class 'list'>":
#                         for mod in model:
#                             self.models[self.models.index(model)][model.index(mod)] = tf.keras.models.load_model(mod)
#                     else:
#                         self.models[self.models.index(model)] = tf.keras.models.load_model(model)
#             self.classes = classes

#     @staticmethod
#     def x_y_w_h(c_path, image):
#         classifier = cv2.CascadeClassifier(c_path)
#         gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
#         return classifier.detectMultiScale(gray, 1.1, 4)[0]

#     def Detection(self, image, colors_rec=(0, 0, 255), colors_txt=(255, 0, 0)):
#         face_roi = None
#         for c_path in self.classifiers:
#             classifier = cv2.CascadeClassifier(c_path)
#             gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
#             for x, y, w, h in classifier.detectMultiScale(gray, 1.1, 4):
#                 roi_gray = gray[y:y + h, x:x + h]
#                 roi_color = image[y:y + h, x:x + w]
#                 clss = classifier.detectMultiScale(roi_gray)
#                 for (ex, ey, ew, eh) in clss:
#                     face_roi = roi_color[ey: ey + eh, ex: ex + ew]
#                 if str(type(colors_rec)) == "<class 'list'>":
#                     color_rec = colors_rec[self.classifiers.index(c_path) % len(colors_rec)]
#                 else:
#                     color_rec = colors_rec

#                 try:
#                     final_image = cv2.resize(face_roi, (self.img_size, self.img_size))
#                     final_image = np.expand_dims(final_image, axis=0)
#                     final_image = final_image / 255
#                     model = self.models[self.classifiers.index(c_path)]
#                     if model != "":
#                         if str(type(model)) == "<class 'list'>":
#                             for mod in model:
#                                 if str(type(colors_txt)) == "<class 'list'>":
#                                     color_txt = colors_txt[model.index(mod) % len(colors_txt)]
#                                 else:
#                                     color_txt = colors_txt
#                                 classes = self.classes[self.classifiers.index(c_path)][model.index(mod)]
#                                 prediction = self.Prediction(final_image, model, classes)
#                                 self.Affichage_predict(image, prediction, x, y, w, h, color_rec=color_rec,
#                                                        color_txt=color_txt)

#                         else:
#                             if str(type(colors_txt)) == "<class 'list'>":
#                                 color_txt = colors_txt[self.classifiers.index(c_path) % len(colors_txt)]
#                             else:
#                                 color_txt = colors_txt
#                             classes = self.classes[self.classifiers.index(c_path)]
#                             prediction = self.Prediction(final_image, model, classes)
#                             self.Affichage_predict(image, prediction, x, y, w, h, color_rec=color_rec,
#                                                    color_txt=color_txt)
#                     else:
#                         cv2.rectangle(image, (x, y), (x + w, y + h), color_rec, 2)
#                 except Exception as e:
#                     print(e)

#     @staticmethod
#     def Prediction(image, model, classes=None):
#         prediction = model.predict(image)

#         if classes is not None:
#             return classes[np.argmax(prediction)]
#         else:
#             return prediction

#     @staticmethod
#     def Affichage_predict(image, predict, x, y, w, h, font_scale=1, font=cv2.FONT_HERSHEY_SIMPLEX,
#                           color_rec=(255, 0, 0), color_txt=(255, 0, 0)):

#         cv2.rectangle(image, (x, y), (x + w, y + h), color_rec, 2)
#         cv2.putText(image, predict, (x, y), font, font_scale, color_txt)

#     @staticmethod
#     def Affichage(name_win, image):
#         cv2.imshow(name_win, image)  # To display the return camera

#     def Retour_cam(self, test="t"):
#         img_path = None
#         cam = None
#         if test == 't':
#             img_path = 'Source/test/deux_visages.jpg'

#         else:
#             cam = cv2.VideoCapture(0)  # Opening of camera

#         while True:
#             # Conditions to close camera and extract picture
#             if test == 't':
#                 frame = cv2.imread(img_path)
#             else:
#                 success, frame = cam.read()
#                 if success == 0:
#                     break
#                 x, y = frame.shape[:2]
#                 frame = np.array([[frame[i, -j - 1] for j in range(y)] for i in range(x)])
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#             self.Detection(image=frame, colors_rec=[(255, 0, 0), (0, 255, 0), (0, 0, 255)])
#             self.Affichage('Retour cam', frame)


# if __name__ == '__main__':
#     # Using OpenCV's built-in Haar Cascade classifiers
#     face = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
#     eye = cv2.data.haarcascades + 'haarcascade_eye.xml'
#     mouth = cv2.data.haarcascades + 'haarcascade_smile.xml'

#     model_face = 'Source/Models/model_face.h5'
#     Classes = ["Asma", "Clorinda", "Médéric", "Pierre", "Sarah"]

#     reco = Reconnaissance(classifiers=[face, eye, mouth], models=[model_face, "", ""], classes=[Classes, "", ""])
#     reco.Retour_cam()
