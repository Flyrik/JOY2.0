# JOY

## Dépendance
  - tkinter
  - tkVideoPlayer
  - datetime
  - time
  - os
  - shutil
  - ctypes
  - json
  - logging
  - cv2 (picamera2 : raspberry)
  - PIL
  - imutils
  - tensorflow (version = 2.10.0)
  - keras
  - numpy
  - gpiozero
  - pigpio
  - subprocess

## Fichiers
```Projet/
├── Source/
│   ├── engrenage.png
│   ├── maison.png
│   ├── model2.h5
│   ├── previous_records.log
│   └── ... création d'autres dossiers ici ...
├── UI.py (App + accueil)
├── FrameProfilUser.py (class user + frame user)
├── FrameParameters.py (reglage servo + frame paramètre)
├── FrameHistorique.py (class history + frame historique)
├── FrameDetectingMood_extra.py (frame detecting mood + frame confirmation sentiment)
├── FrameActivities.py (frame activité en fonction emotion)
├── capteur_BPM.py (Lecture BPM)
└── ...
```

